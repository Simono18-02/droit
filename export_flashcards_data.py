"""Export flashcard data for the static web version."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from flashcards_droit import ANSWER_KEY, load_flashcards


ROOT = Path(__file__).resolve().parent
COURSE_DIR = ROOT / "cours droit"

CHAPTER_BY_SOURCE = {
    "ENISE CHAP 1 Définition et finalité du droit-1.pdf": {
        "id": "chap-1",
        "title": "Chapitre 1 - Définition et finalité du droit",
    },
    "ENISE CHAP 2 LES SOURCES DU DROIT.pdf": {
        "id": "chap-2",
        "title": "Chapitre 2 - Les sources du droit",
    },
    "ENISE CHAP 3 LA PREUVE DES DROITS.pdf": {
        "id": "chap-3",
        "title": "Chapitre 3 - La preuve des droits",
    },
    "CHAP 4.pdf": {
        "id": "chap-4",
        "title": "Chapitre 4 - Les juridictions",
    },
    "ENISE CHAP 5 MARD les modes alternatifs de règlement des différents.pdf": {
        "id": "chap-5",
        "title": "Chapitre 5 - Les MARD",
    },
    "ENISE CHAP 6 LES PERSONNES-1.pdf": {
        "id": "chap-6",
        "title": "Chapitre 6 - Les personnes",
    },
}

STOPWORDS = {
    "a", "afin", "ainsi", "alors", "au", "aucun", "aucune", "aux", "avec", "ce",
    "cela", "ces", "cet", "cette", "chaque", "comme", "comment", "dans", "de",
    "des", "du", "elle", "elles", "en", "est", "et", "etre", "fait", "il",
    "ils", "la", "le", "les", "leur", "leurs", "lorsque", "mais", "ne", "non",
    "notamment", "nous", "ou", "par", "pas", "peut", "plusieurs", "pour", "que",
    "quel", "quelle", "quelles", "quels", "qui", "sa", "se", "selon", "ses",
    "si", "sont", "sur", "un", "une", "vous", "doit", "reponse", "reponses",
}


@dataclass(frozen=True)
class CourseChunk:
    text: str
    source: str
    page: int
    terms: set[str]


def _normalize_text(value: str) -> str:
    value = value.casefold()
    value = re.sub(r"\s+", " ", value)
    return value.strip().rstrip(".,;:!?…")


def _ascii_fold(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"prud\s*hom(?:m|aux|al|ale|ales|aux|mes?)\w*", "prudhommes", value, flags=re.I)
    return value.casefold()


def _terms(value: str) -> set[str]:
    words = re.findall(r"[a-z0-9]{3,}", _ascii_fold(value))
    return {word for word in words if word not in STOPWORDS}


def _clean_course_text(value: str) -> str:
    value = value.replace("\x00", " ")
    value = value.replace("\uf0de", "-").replace("\uf0b7", "-")
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"\s+([,.;:!?])", r"\1", value)
    return value.strip()


def _course_chunks() -> list[CourseChunk]:
    if not COURSE_DIR.exists():
        return []

    from pypdf import PdfReader

    chunks: list[CourseChunk] = []
    for pdf in sorted(COURSE_DIR.glob("*.pdf")):
        reader = PdfReader(str(pdf))
        for page_index, page in enumerate(reader.pages, 1):
            raw_text = page.extract_text() or ""
            lines = [
                _clean_course_text(line)
                for line in raw_text.splitlines()
                if _clean_course_text(line)
            ]
            if not lines:
                continue

            page_chunks: list[str] = []
            current: list[str] = []
            current_length = 0
            for line in lines:
                if current and current_length + len(line) > 850:
                    page_chunks.append(" ".join(current))
                    current = []
                    current_length = 0
                current.append(line)
                current_length += len(line)
            if current:
                page_chunks.append(" ".join(current))

            for text in page_chunks:
                chunk_terms = _terms(text)
                if len(chunk_terms) < 4:
                    continue
                chunks.append(
                    CourseChunk(
                        text=text,
                        source=pdf.name,
                        page=page_index,
                        terms=chunk_terms,
                    )
                )
    return chunks


def _score_chunk(query_terms: set[str], chunk: CourseChunk, question: str) -> float:
    if not query_terms:
        return 0.0

    overlap = query_terms & chunk.terms
    score = len(overlap) / max(len(query_terms), 1)
    score += min(len(overlap), 8) * 0.045
    question_overlap = _terms(question) & chunk.terms
    score += len(question_overlap) * 0.12

    question_folded = _ascii_fold(question)
    chunk_folded = _ascii_fold(chunk.text)
    for phrase in re.findall(r"[a-z0-9]{4,}(?:\s+[a-z0-9]{4,}){1,3}", question_folded):
        if phrase in chunk_folded:
            score += 0.16
    return score


def _clean_sentence(value: str) -> str:
    value = _clean_course_text(value)
    value = re.sub(r"^\d+(?:\.\d+)*\s*[-–]?\s*", "", value)
    value = re.sub(r"^[A-Z]\s*[-–]\s*", "", value)
    value = value.strip(" -:;")
    return value


def _relevant_course_idea(card: Any, chunk: CourseChunk, max_length: int = 300) -> str:
    question_terms = _terms(card.question)
    answer_terms = _terms(" ".join(card.options[answer - 1] for answer in ANSWER_KEY.get(card.card_id, ()) if answer))
    useful_terms = question_terms | answer_terms
    pieces = re.split(r"(?<=[.!?])\s+|\s+-\s+|(?<=:)\s+", chunk.text)
    ranked: list[tuple[int, str]] = []

    for piece in pieces:
        sentence = _clean_sentence(piece)
        if len(sentence) < 24:
            continue
        terms = _terms(sentence)
        overlap = len(terms & useful_terms)
        if overlap:
            ranked.append((overlap, sentence))

    ranked.sort(key=lambda item: (-item[0], len(item[1])))
    selected: list[str] = []
    for _score, sentence in ranked[:3]:
        candidate = " ".join([*selected, sentence])
        if len(candidate) > max_length:
            continue
        selected.append(sentence)
        if len(candidate) > 170:
            break

    if not selected:
        return "Ce point est traité dans le chapitre indiqué, mais le passage extrait n'est pas assez net pour produire une explication fiable."

    idea = " ".join(selected)
    if idea and idea[-1] not in ".!?":
        idea += "."
    return idea


def _answer_sentence(card: Any) -> str:
    answers = ANSWER_KEY.get(card.card_id, ())
    if not answers:
        return "Aucune des propositions n'est retenue comme correcte dans ce QCM."

    labels = ", ".join(str(answer) for answer in answers)
    if len(answers) == 1:
        return f"La proposition {labels} est correcte."
    return f"Les propositions {labels} sont correctes."


def _wrong_options(card: Any) -> list[str]:
    answers = set(ANSWER_KEY.get(card.card_id, ()))
    return [
        f"{index}. {option.strip()}"
        for index, option in enumerate(card.options, 1)
        if index not in answers
    ]


def _correct_options(card: Any) -> list[str]:
    answers = ANSWER_KEY.get(card.card_id, ())
    return [
        f"{answer}. {card.options[answer - 1].strip()}"
        for answer in answers
        if 1 <= answer <= len(card.options)
    ]


def _option_label(index: int) -> str:
    return f"L'option {index}"


def _is_none_option(option: str) -> bool:
    option = option.casefold()
    return "aucune" in option or "aucun" in option or "n'est juste" in option


def _specific_explanation(card: Any) -> str | None:
    question = card.question.casefold()
    options = [option.casefold() for option in card.options]

    if "droit subjectif" in question:
        objective_index = next((i + 1 for i, option in enumerate(options) if "ensemble des règles" in option or "ensemble des regles" in option), None)
        correct = ", ".join(str(answer) for answer in ANSWER_KEY.get(card.card_id, ()))
        extra = (
            f" {_option_label(objective_index)} correspond à la définition du droit objectif."
            if objective_index
            else ""
        )
        return (
            f"{extra} Le droit subjectif désigne les prérogatives individuelles reconnues aux sujets de droit. "
            "Il se comprend donc par opposition au droit objectif, qui correspond aux règles générales applicables dans la société. "
            f"La proposition {correct} est donc la seule affirmation exacte."
        ).strip()

    if "droit objectif" in question:
        subjective_index = next((i + 1 for i, option in enumerate(options) if "prérogative" in option or "prerogative" in option or "faculté" in option or "faculte" in option), None)
        mandatory_index = next((i + 1 for i, option in enumerate(options) if "obligatoire" in option), None)
        opposition_index = next((i + 1 for i, option in enumerate(options) if "s'oppose au droit subjectif" in option), None)
        none_index = next((i + 1 for i, option in enumerate(card.options) if _is_none_option(option)), None)
        parts = []
        if none_index and none_index in ANSWER_KEY.get(card.card_id, ()):
            if subjective_index:
                parts.append(f"{_option_label(subjective_index)} renvoie au droit subjectif, pas au droit objectif.")
            parts.append(
                "Les autres propositions ne donnent pas la définition attendue du droit objectif, qui correspond à l'ensemble des règles générales applicables."
            )
            parts.append(f"{_option_label(none_index)} est donc correcte.")
            return " ".join(parts)
        if subjective_index:
            parts.append(f"{_option_label(subjective_index)} renvoie au droit subjectif, pas au droit objectif.")
        if mandatory_index and mandatory_index in ANSWER_KEY.get(card.card_id, ()):
            parts.append(f"{_option_label(mandatory_index)} est exacte car le droit objectif regroupe des règles obligatoires.")
        if opposition_index and opposition_index in ANSWER_KEY.get(card.card_id, ()):
            parts.append(f"{_option_label(opposition_index)} est exacte car le droit objectif se distingue du droit subjectif.")
        if any(_is_none_option(option) for option in card.options):
            parts.append("L'option « aucune de ces réponses » doit être écartée dès qu'une proposition exacte existe.")
        return " ".join(parts) if parts else None

    return None


def _concept_reason(question: str, option: str, is_correct: bool) -> str:
    q = _ascii_fold(question)
    o = _ascii_fold(option)
    short_option = option.strip().rstrip(".")

    if "droit subjectif" in q:
        if "ensemble des regles" in o or "regles de conduite" in o:
            return "cela définit le droit objectif, pas le droit subjectif"
        if "oppose au droit objectif" in o:
            return "le droit subjectif se définit par opposition au droit objectif"
        if _is_none_option(option):
            return "une proposition exacte existe"

    if "droit objectif" in q:
        if "prerogative" in o or "faculte" in o:
            return "cela renvoie au droit subjectif, c'est-à-dire à une prérogative individuelle"
        if "obligatoire" in o:
            return "le droit objectif regroupe des règles obligatoires"
        if "oppose au droit subjectif" in o:
            return "le droit objectif se distingue du droit subjectif"
        if "decoule du droit subjectif" in o:
            return "le rapport est inversé : le droit subjectif est reconnu par le droit objectif"
        if _is_none_option(option):
            return "elle n'est correcte que si aucune autre proposition ne l'est"

    if "cour de cassation" in q or "pourvoi" in q:
        if "droit" in o and ("fait" not in o or is_correct):
            return "la Cour de cassation contrôle l'application du droit"
        if "fait" in o and not is_correct:
            return "la Cour de cassation ne rejuge pas les faits"
        if "haute juridiction" in o:
            return "la Cour de cassation est la juridiction suprême de l'ordre judiciaire"
        if "tout type de pourvoi" in o:
            return "le pourvoi peut viser une décision rendue en dernier ressort"

    if "appel" in q or "premier degré" in q or "premier degre" in q:
        if "toujours" in o and not is_correct:
            return "l'appel n'est pas automatique : il dépend notamment du seuil et du délai"
        if "seuil" in o or "5000" in o or "délai" in o or "delai" in o:
            return "l'appel suppose de respecter les conditions de recevabilité"
        if "supérieur" in o or "superieur" in o:
            return "le montant ne suffit pas à lui seul, le délai compte aussi"

    if "juridiction territorialement" in q:
        if "défendeur" in o or "defendeur" in o:
            return "en principe, la juridiction compétente est celle du lieu où demeure le défendeur"
        if "demandeur" in o:
            return "le principe n'est pas le tribunal du demandeur"

    if "preuve" in q or "procès" in q or "proces" in q or "charge" in q:
        if "demandeur" in o and "défendeur" in o:
            return "la preuve pèse d'abord sur le demandeur, puis le défendeur doit prouver ses moyens de défense"
        if "demandeur" in o and "defendeur" in o:
            return "la preuve pèse d'abord sur le demandeur, puis le défendeur doit prouver ses moyens de défense"
        if "demandeur" in o and "defendeur" not in o:
            return "c'est incomplet : le demandeur supporte d'abord la preuve, mais le défendeur peut ensuite devoir prouver sa défense"
        if "defendeur" in o and "demandeur" not in o:
            return "l'ordre est inversé : la charge ne commence pas par le défendeur"
        if "parties" in o:
            return "dans un système accusatoire, les parties apportent les éléments de preuve"
        if "juge" in o and not is_correct:
            return "le juge apprécie la preuve, mais il n'en supporte pas en principe la charge"
        if "preuve parfaite" in q or "modes de preuve parfaite" in q:
            return "les preuves parfaites lient fortement le juge, notamment l'écrit, l'aveu judiciaire et le serment décisoire"

    if "présomption" in q or "presomption" in q:
        if "fait connu" in o and "fait inconnu" in o:
            return "une présomption consiste à déduire un fait inconnu d'un fait connu"
        if "ne peut pas apporter la preuve contraire" in o:
            return "une présomption irréfragable ne supporte pas la preuve contraire"
        if "preuve contraire" in o and not is_correct:
            return "cela correspond plutôt à une présomption simple"

    if "acte sous seing" in q or "sous-signature" in q:
        if "signature" in o:
            return "la signature des parties est nécessaire pour l'acte sous seing privé"
        if "preuve du contraire" in o:
            return "l'acte sous seing privé fait foi jusqu'à preuve contraire"
        if "aucun formalisme" in o:
            return "il est rédigé par les parties sans intervention d'un officier public, même si certaines formes restent exigées"
        if "pas de valeur" in o:
            return "l'acte sous seing privé a bien une valeur probatoire"

    if "acte authentique" in q:
        if "officier public" in o or "authentique" in o:
            return "l'acte authentique est reçu par un officier public compétent"
        if "copie" in q:
            return "la copie d'un acte authentique peut être admise comme preuve dans les conditions prévues"

    if "loi" in q or "promulgation" in q or "pouvoir législatif" in q or "pouvoir legislatif" in q:
        if "parlement" in o:
            return "la loi est votée par le Parlement"
        if "président de la république" in o or "president de la republique" in o:
            return "la promulgation relève du Président de la République"
        if "premier ministre" in o and "parlement" in o:
            return "l'initiative de la loi appartient concurremment au Premier ministre et aux parlementaires"
        if "rétroactive" in o or "retroactive" in o:
            return "en matière civile, la loi nouvelle peut parfois produire des effets sur des situations en cours selon les règles d'application dans le temps"

    if "traité" in q or "traite" in q:
        if "négoci" in o or "negoci" in o or "sign" in o or "ratifi" in o:
            return "un traité suppose négociation, signature et ratification"
        if "réciprocité" in o or "reciprocite" in o:
            return "l'application d'un traité dépend aussi du principe de réciprocité"

    if "règlements européens" in q or "reglements europeens" in q or "droit communautaire" in q:
        if "portée générale" in o or "portee generale" in o:
            return "le règlement européen a une portée générale"
        if "obligatoire" in o:
            return "le règlement européen est obligatoire dans tous ses éléments"
        if "réception" in o or "reception" in o:
            return "le règlement européen est directement applicable sans mesure de réception"

    if "médiation" in q or "mediation" in q or "médiateur" in q or "mediateur" in q:
        if "conventionnel" in o:
            return "la médiation repose sur une démarche amiable et conventionnelle"
        if "juridictionnel" in o:
            return "la médiation ne tranche pas le litige comme une juridiction"
        if "arbitrage" in o:
            return "la médiation n'est pas l'arbitrage : le médiateur aide les parties, l'arbitre rend une sentence"
        if "parties" in o or "juge" in o:
            return "le médiateur peut intervenir dans une logique amiable, selon la procédure et l'accord des parties"
        if "dessaisissement" in o:
            return "la médiation n'enlève pas nécessairement l'affaire au juge déjà saisi"
        if "conciliation" in o:
            return "la procédure civile favorise une phase de conciliation ou de règlement amiable"

    if "arbitrage" in q or "arbitre" in q or "sentence arbitrale" in q:
        if "juridictionnel" in o:
            return "l'arbitrage aboutit à une décision, la sentence arbitrale"
        if "conventionnel" in o:
            return "l'arbitrage repose sur l'accord des parties"
        if "amiable compositeur" in o or "équité" in o or "equite" in o:
            return "l'amiable composition permet de statuer en équité"
        if "clause compromissoire" in o:
            return "la clause compromissoire prévoit l'arbitrage avant la naissance du litige"

    if "personne morale" in q:
        if "objet social" in o:
            return "la personne morale agit dans la limite de son objet social"
        if "statuts" in o or "immatriculation" in o:
            return "la naissance de la personne morale passe par les formalités de constitution"
        if "patrimoine" in o:
            return "la personne morale a un patrimoine distinct"

    if "personne physique" in q or "personnalité juridique" in q or "personnalite juridique" in q:
        if "naissance" in o or "vivant" in o or "viable" in o:
            return "la personnalité juridique de la personne physique commence à la naissance, sous conditions"
        if "mort" in o or "décès" in o or "deces" in o:
            return "la personnalité juridique cesse au décès"

    if "nom de famille" in q or "nom présente" in q or "nom presente" in q:
        if "filiation" in o:
            return "le nom de famille est en principe transmis par la filiation"
        if "indisponible" in o or "imprescriptible" in o or "inaliénable" in o or "inalienable" in o:
            return "le nom obéit à des caractères protecteurs de l'identité de la personne"

    if "patrimoine" in q:
        if "actif" in o or "passif" in o:
            return "le patrimoine comprend un actif et un passif"
        if "personne" in o:
            return "le patrimoine est juridiquement rattaché à la personne"
        if "céder" in o or "ceder" in o:
            return "on ne cède pas son patrimoine comme universalité, seulement certains éléments qui le composent"

    if "bien" in q or "chose" in q:
        if "meuble" in o or "immeuble" in o:
            return "les biens se classent notamment en meubles et immeubles"
        if "fongible" in q and ("genre" in o or "rempla" in o):
            return "une chose fongible peut être remplacée par une chose équivalente"
        if "commune" in q:
            return "une chose commune n'appartient à personne et son usage est commun"

    if "contrat de travail" in q:
        if "subordination" in o:
            return "le lien de subordination est l'élément central du contrat de travail"
        if "prestation" in o or "rémunération" in o or "remuneration" in o:
            return "le contrat de travail suppose une prestation de travail et une rémunération"
        if "consentement" in q and ("erreur" in o or "dol" in o or "violence" in o):
            return "le consentement doit être libre et non vicié"

    if "cdd" in q or "contrat à durée déterminée" in q or "contrat a duree determinee" in q:
        if "deux jours ouvrables" in o:
            return "le CDD doit être transmis au salarié dans le délai légal de deux jours ouvrables"
        if "deux jours ouvrés" in o or "deux semaines" in o:
            return "ce délai ne correspond pas à la formulation retenue par le QCM"
        if "faute grave" in o or "force majeure" in o or "accord" in o:
            return "la rupture anticipée du CDD n'est admise que dans des cas limités"
        if "surcroît" in o or "surcroit" in o:
            return "le CDD peut répondre à un accroissement temporaire d'activité"

    if "cdi" in q and "période d'essai" in q or "periode d'essai" in q:
        if "deux mois" in o or "2 mois" in o:
            return "la durée maximale varie selon la catégorie du salarié ; deux mois correspond aux ouvriers et employés"

    if "prud" in q:
        if "employeurs" in o and "salari" in o:
            return "le conseil de prud'hommes est une juridiction paritaire composée de représentants des employeurs et des salariés"
        if "uniquement" in o:
            return "le caractère paritaire exclut une composition uniquement salariale ou uniquement patronale"

    if "doctrine" in q:
        if "loi" in o or "jugement" in o:
            return "la doctrine est une opinion ou analyse juridique, elle n'a pas la valeur normative d'une loi ni l'autorité d'un jugement"
        if "juristes" in o or "travaux" in o or "études" in o or "etudes" in o:
            return "la doctrine correspond aux travaux et opinions des juristes"

    if _is_none_option(option):
        return "elle n'est correcte que si aucune autre proposition n'est exacte"

    if is_correct:
        return f"c'est la formulation retenue pour ce point du cours : « {short_option} »"
    return f"elle propose « {short_option} », ce qui n'est pas l'élément retenu pour répondre à cette question"


def _option_explanations(card: Any, include_wrong_limit: int = 4) -> str:
    answers = set(ANSWER_KEY.get(card.card_id, ()))
    parts: list[str] = []
    for index, option in enumerate(card.options, 1):
        if index in answers:
            parts.append(f"L'option {index} est correcte car {_concept_reason(card.question, option, True)}.")

    wrong_parts = []
    for index, option in enumerate(card.options, 1):
        if index not in answers:
            wrong_parts.append(f"L'option {index} est écartée car {_concept_reason(card.question, option, False)}.")

    if len(wrong_parts) > include_wrong_limit:
        parts.extend(wrong_parts[:include_wrong_limit])
        remaining = len(wrong_parts) - include_wrong_limit
        parts.append(f"Les {remaining} autres propositions sont également écartées car elles ne correspondent pas au point de cours visé.")
    else:
        parts.extend(wrong_parts)
    return " ".join(parts)


def _chapter_label(chunk: CourseChunk | None) -> str:
    if chunk is None:
        return "le cours fourni"
    return CHAPTER_BY_SOURCE.get(chunk.source, {}).get("title", chunk.source)


def _justification_sentence(card: Any, chunk: CourseChunk | None) -> str:
    answers = ANSWER_KEY.get(card.card_id, ())
    specific = _specific_explanation(card)
    if specific:
        return specific

    if not answers:
        return (
            "Aucune option ne reprend correctement la règle attendue. "
            f"Il faut donc sélectionner « aucune des réponses proposées ». {_option_explanations(card)}"
        )

    return _option_explanations(card)


def _method_sentence(card: Any, chunk: CourseChunk | None) -> str:
    answers = ANSWER_KEY.get(card.card_id, ())
    chapter = _chapter_label(chunk)
    location = f"du {chapter}" if chunk is not None else "du cours"
    if not answers:
        return "À retenir : ne force pas une réponse lorsqu'aucune proposition ne correspond au cours."
    if len(answers) == 1:
        return "À retenir : la bonne option est celle qui reprend précisément la définition ou la règle visée."
    return "À retenir : la réponse est cumulative ; oublier une option correcte rend la réponse incomplète."


def _course_explanation(card: Any, chunk: CourseChunk | None) -> str:
    return f"{_answer_sentence(card)} {_justification_sentence(card, chunk)} {_method_sentence(card, chunk)}"


def _course_note(card: Any, chunks: list[CourseChunk]) -> dict[str, str]:
    query = " ".join([card.question, *card.options])
    query_terms = _terms(query)
    ranked = sorted(
        chunks,
        key=lambda chunk: _score_chunk(query_terms, chunk, card.question),
        reverse=True,
    )
    best = ranked[0] if ranked else None
    score = _score_chunk(query_terms, best, card.question) if best else 0.0
    question_terms = _terms(card.question)
    question_overlap = question_terms & best.terms if best else set()
    required_overlap = min(2, len(question_terms))

    if best is None or score < 0.24 or len(question_overlap) < required_overlap:
        return {
            "text": _course_explanation(card, None),
            "source": "",
        }

    return {
        "text": _course_explanation(card, best),
        "source": f"{best.source}, p. {best.page}",
    }


def _chapter_from_note(note: dict[str, str]) -> dict[str, str]:
    source = note.get("source", "").split(", p. ", 1)[0]
    return CHAPTER_BY_SOURCE.get(
        source,
        {
            "id": "sans-chapitre",
            "title": "Sans chapitre fiable",
        },
    )


def _difficulty(card: Any) -> str:
    answers = ANSWER_KEY.get(card.card_id, ())
    if len(card.options) >= 7 or len(answers) >= 4:
        return "Difficile"
    if len(card.options) >= 5 or len(answers) >= 2:
        return "Moyen"
    return "Facile"


def _card_key(card: object) -> tuple[str, tuple[str, ...], tuple[int, ...]]:
    return (
        _normalize_text(card.question),
        tuple(_normalize_text(option) for option in card.options),
        tuple(ANSWER_KEY.get(card.card_id, ())),
    )


def _dedupe_cards(cards: list[object]) -> list[object]:
    unique_cards = []
    seen: set[tuple[str, tuple[str, ...], tuple[int, ...]]] = set()
    for card in cards:
        key = _card_key(card)
        if key in seen:
            continue
        seen.add(key)
        unique_cards.append(card)
    return unique_cards


def main() -> None:
    source_cards = load_flashcards(ROOT / "pdf.py")
    cards = _dedupe_cards(source_cards)
    chunks = _course_chunks()
    exported_cards = []
    for card in cards:
        note = _course_note(card, chunks)
        exported_cards.append(
            {
                "id": card.card_id,
                "sourceNumber": card.source_number,
                "sourceTitle": card.source_title,
                "questionNumber": card.question_number,
                "question": card.question,
                "options": list(card.options),
                "answers": list(ANSWER_KEY.get(card.card_id, ())),
                "courseNote": note,
                "chapter": _chapter_from_note(note),
                "difficulty": _difficulty(card),
                "multiple": len(ANSWER_KEY.get(card.card_id, ())) != 1,
            }
        )

    chapters = []
    seen_chapters = set()
    for card in exported_cards:
        chapter = card["chapter"]
        if chapter["id"] in seen_chapters:
            continue
        seen_chapters.add(chapter["id"])
        chapters.append(chapter)

    payload = {
        "appTitle": "Flashcards QCM Droit",
        "chapters": chapters,
        "cards": exported_cards,
    }

    data = json.dumps(payload, ensure_ascii=False, indent=2)
    (ROOT / "flashcards-data.js").write_text(
        f"window.FLASHCARDS_DATA = {data};\n",
        encoding="utf-8",
    )
    removed = len(source_cards) - len(cards)
    missing_notes = sum(1 for card in payload["cards"] if not card["courseNote"]["source"])
    print(
        f"Exported {len(cards)} cards to flashcards-data.js "
        f"({removed} strict duplicates removed, {missing_notes} without reliable course note)"
    )


if __name__ == "__main__":
    main()

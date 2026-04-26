"""Audit QCM answer keys against exported cards and course notes."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "flashcards-data.js"
REPORT_PATH = ROOT / "audit_questions.csv"


def _load_payload() -> dict:
    text = DATA_PATH.read_text(encoding="utf-8")
    return json.loads(text.split("=", 1)[1].strip().rstrip(";"))


def _norm(value: str) -> str:
    return re.sub(r"\s+", " ", value.casefold()).strip()


def _has_multiple_hint(question: str) -> bool:
    q = _norm(question)
    hints = (
        "plusieurs réponses",
        "plusieurs reponses",
        "réponses possibles",
        "reponses possibles",
        "plusieurs réponses possibles",
        "choisir la ou les",
        "la ou les",
    )
    return any(hint in q for hint in hints)


def _option_mentions_none(option: str) -> bool:
    o = _norm(option)
    return any(
        text in o
        for text in (
            "n'est juste",
            "ne sont justes",
            "aucune de ces réponses",
            "aucune de ces reponses",
            "aucune réponse",
            "aucune reponse",
            "toutes les réponses sont fausses",
        )
    )


def _row(card: dict) -> dict:
    answers = card.get("answers", [])
    option_count = len(card.get("options", []))
    issues: list[str] = []

    if not answers:
        issues.append("NO_ANSWER_KEY")
    if any(answer < 1 or answer > option_count for answer in answers):
        issues.append("ANSWER_OUT_OF_RANGE")
    if len(set(answers)) != len(answers):
        issues.append("DUPLICATE_ANSWER_INDEX")
    if len(answers) > 1 and not card.get("multiple"):
        issues.append("MULTIPLE_FLAG_FALSE")
    if len(answers) == 1 and card.get("multiple"):
        issues.append("MULTIPLE_FLAG_TRUE_WITH_SINGLE")
    if _has_multiple_hint(card["question"]) and len(answers) <= 1:
        issues.append("QUESTION_HINTS_MULTIPLE_BUT_SINGLE_KEY")
    if not _has_multiple_hint(card["question"]) and len(answers) > 1:
        issues.append("NO_MULTIPLE_HINT_BUT_MULTIPLE_KEY")
    if len(answers) > 1:
        selected_options = [card["options"][answer - 1] for answer in answers if 1 <= answer <= option_count]
        if any(_option_mentions_none(option) for option in selected_options):
            issues.append("NONE_OPTION_COMBINED_WITH_OTHER")
    if not card.get("courseNote", {}).get("source"):
        issues.append("NO_RELIABLE_COURSE_NOTE")

    return {
        "id": card["id"],
        "chapter": card.get("chapter", {}).get("title", ""),
        "question": card["question"],
        "option_count": option_count,
        "answers": ",".join(str(answer) for answer in answers),
        "answer_count": len(answers),
        "ui_control": "checkboxes" if card.get("multiple") else "radio",
        "issues": ";".join(issues),
        "course_source": card.get("courseNote", {}).get("source", ""),
    }


def main() -> None:
    payload = _load_payload()
    rows = [_row(card) for card in payload["cards"]]
    with REPORT_PATH.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    issue_counts: dict[str, int] = {}
    for row in rows:
        for issue in filter(None, row["issues"].split(";")):
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

    print(f"cards={len(rows)}")
    print(f"report={REPORT_PATH.name}")
    for issue, count in sorted(issue_counts.items()):
        print(f"{issue}={count}")


if __name__ == "__main__":
    main()

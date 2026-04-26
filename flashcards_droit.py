# -*- coding: utf-8 -*-
"""Application Windows de flashcards pour les QCM de droit."""

from __future__ import annotations

import ast
import json
import random
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText


APP_TITLE = "Flashcards QCM Droit"
ALL_SOURCES_LABEL = "Toutes les sources"


ANSWER_KEY_BY_SOURCE: dict[int, list[tuple[int, ...]]] = {
    1: [
        (2,), (1, 2, 3, 4, 5), (1, 4, 7, 8), (3, 4, 5, 6), (3,),
        (1, 2, 3), (3,), (3,), (1,), (1, 2),
        (3,), (3,), (1,), (3,), (1,),
        (1,), (1, 2, 3, 4, 5), (3,), (2, 3), (2, 4, 5, 7, 8),
        (), (1,), (4,), (2,), (2, 3),
        (1, 2, 4, 5), (2,), (4,), (1,), (2,),
        (4,), (3,), (3,), (4,), (1,),
        (1,), (1, 2, 4), (2,), (4,), (1, 4, 5),
        (1,), (1, 3), (2, 3, 5), (1, 3, 4, 6), (1, 2, 3, 4),
        (1,), (1, 2, 3), (3,), (1,), (1, 2),
        (3,), (1,), (1,), (2, 3), (1, 3, 4),
        (1,), (1, 2), (1, 2, 3), (2, 3), (1, 2, 3),
        (1, 3), (2,), (3, 4), (2, 3, 4, 5), (1,),
        (1, 2, 3, 4, 5), (1, 2, 3, 4, 5), (1,), (1,), (2,),
        (1, 2), (2,), (1, 3), (2, 3, 4), (2, 3, 4),
        (3,), (2,), (2,), (2,), (1, 2, 3, 4),
        (1, 2, 3), (1,), (2,), (4,), (4,),
        (1, 2, 3), (2, 3), (2,), (1, 2), (1,),
        (2,), (2, 3), (1, 3), (1,), (3,),
        (2,), (1, 3, 4), (1,), (2,), (1, 2, 3),
    ],
    2: [
        (4,), (2,), (1, 2, 4, 5), (2,), (1,),
        (2,), (1,), (4,), (1,), (1,),
        (2,), (1, 2), (2,), (1, 3), (2, 3, 4),
        (2, 3, 4), (3,), (2,), (2,), (3,),
        (3,), (3,), (2,), (4,), (1,),
        (1,), (3,), (1, 2, 3, 5), (2,), (4,),
        (1, 4, 5), (1,), (1, 3), (2, 3, 5), (1, 3, 4, 6),
        (1, 3, 4, 5), (2,), (4,), (1, 2, 3, 4), (4,),
        (3, 4), (2, 5, 8, 9), (1, 2, 3, 4, 5), (3, 5, 6, 7), (1, 2, 3, 4, 5),
        (1, 2, 3), (3,), (3,), (1,), (1, 2, 3),
        (3,), (3,), (1,), (1, 2), (1,),
        (1, 2), (3,), (1,), (1, 2), (1, 3, 4),
        (1, 4), (2,), (2, 3), (2,), (1, 3, 4),
        (1,), (3, 4), (1, 2), (1, 2, 3), (2, 3),
        (1, 2, 3), (1, 2, 3), (1, 3), (2,), (4, 6, 7),
        (2,), (2, 3, 4, 5), (3,), (1,), (1,),
        (2,), (1, 2, 3, 4, 5), (1, 2, 3, 4, 5), (1,), (3, 4, 6),
        (2, 3, 4), (2,), (1, 2, 3, 4), (1, 2, 3, 4), (1,),
        (2,), (3,), (4,), (1, 2, 3), (2, 3),
        (2,), (1, 2), (1,), (2,), (2, 3),
        (1, 3), (1, 3), (2,), (2,), (1, 3, 4),
        (1,), (2, 3), (2, 4, 5, 7, 8), (), (2,),
        (4,),
    ],
    3: [
        (2,), (1, 2, 3, 4, 5), (1, 4, 7, 8), (3, 4, 5, 6), (3,),
        (1, 2, 3), (3,), (3,), (1,), (1, 2),
        (3,), (2, 3), (2, 4, 5, 7, 8), (), (1,),
        (4,), (2,), (3,), (1, 2, 4, 5), (2,),
        (4,), (1,), (2,), (4,), (3,),
        (3,), (4,), (1,), (1,), (1, 2, 4),
        (2,), (4,), (1, 4, 5), (1,), (1, 3),
        (2, 3, 5), (1, 3, 4, 6), (1, 2, 3, 4), (1,), (1, 2, 3),
        (3,), (1,), (1, 2), (3,), (1,),
        (1,), (2, 3), (1, 3, 4), (1,), (1, 2),
        (1, 2, 3), (2, 3), (1, 2, 3), (1, 3), (2,),
        (3, 4), (2, 3, 4, 5), (1,), (1, 2, 3, 4, 5), (1, 2, 3, 4, 5),
        (1,), (1,), (2,), (1, 2), (2,),
        (1, 3), (2, 3, 4), (2, 3, 4), (3,), (2,),
        (2,), (2,), (1, 2, 3, 4), (1, 2, 3), (1,),
        (2,), (), (4,), (1, 2, 3), (2, 3),
        (2,), (1, 2), (1,), (2,), (2, 3),
        (1, 3), (1,), (3,), (2,), (1, 3, 4),
        (1,),
    ],
    4: [
        (3,), (1, 2, 4, 5), (2,), (1,), (4,),
        (3,), (2,), (3,), (3,), (3,),
        (1, 2, 3), (1,), (2, 3, 4), (1, 3, 4, 6), (1, 3, 4, 5),
        (2,), (4,), (1, 2, 3, 4), (2, 5), (3, 4),
        (1, 2, 3, 4, 5), (3, 4, 5, 6), (3,), (1, 2, 3), (1,),
        (3,), (3,), (1, 2), (1,), (1, 2),
        (3,), (1,), (1, 3, 4), (1, 4), (2,),
        (2, 3), (2,), (1, 3, 4), (3, 4), (1, 2),
        (1, 2, 3), (2, 3), (1, 2, 3), (1, 2, 3), (1, 3),
        (2,), (4, 6, 7), (2, 3, 4, 5), (1,), (1, 2, 3, 4, 5),
        (1, 2, 3, 4, 5), (3, 4, 6), (2, 3, 4), (2,), (2, 3, 4, 5),
        (1, 2, 3, 4), (1,), (2,), (3,), (4,),
        (1, 2, 3), (2, 3), (2,), (1, 2), (1,),
        (2, 3), (2,), (4,), (1, 3), (2,),
    ],
    5: [
        (1,), (3,), (2,), (1,), (2, 5, 6, 8),
        (2,), (2,), (5,), (4,), (1,),
        (1,), (1,), (4,), (1,), (3,),
        (1,), (1,), (3,), (3,), (1,),
        (1,), (2,), (1,), (1,), (1,),
        (1,), (1,), (2,), (4,), (1,),
        (), (1,), (1, 2),
    ],
    6: [
        (1, 4), (1, 2, 4), (1, 3, 4, 5), (1, 3, 4), (1, 3, 4),
        (2, 3), (1, 2, 4), (2, 3, 4), (2, 6), (1, 2, 3),
        (1, 2, 3, 4), (1, 2, 4, 5), (1, 2, 3), (1, 2, 5), (3, 4),
        (1, 3, 4), (1, 5, 6), (2, 4, 5), (1, 3), (2, 3),
        (2, 3, 5), (3, 5), (1, 3, 4), (1, 5), (1, 2, 4),
        (1, 3), (2,), (3,), (2, 3, 4), (1,),
        (2, 3, 4), (1, 2, 3), (1, 3), (1, 2, 3, 4, 5), (1, 3, 4),
        (3, 4), (1, 2, 3), (1, 2, 3, 4), (1, 2, 4), (1, 2, 3),
    ],
}

ANSWER_KEY: dict[str, tuple[int, ...]] = {
    f"S{source_number}-Q{question_number}": answers
    for source_number, source_answers in ANSWER_KEY_BY_SOURCE.items()
    for question_number, answers in enumerate(source_answers, 1)
}


@dataclass(frozen=True)
class Flashcard:
    card_id: str
    source_number: int
    source_title: str
    question_number: int
    question: str
    options: tuple[str, ...]


def _literal_assignments(path: Path) -> dict[str, object]:
    """Read top-level literal assignments from pdf.py without importing it."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    values: dict[str, object] = {}

    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id.startswith("SOURCE_"):
                try:
                    values[target.id] = ast.literal_eval(node.value)
                except (ValueError, SyntaxError):
                    pass

    return values


def load_flashcards(path: Path) -> list[Flashcard]:
    values = _literal_assignments(path)
    cards: list[Flashcard] = []

    for source_number in range(1, 100):
        title_key = f"SOURCE_{source_number}_TITLE"
        data_key = f"SOURCE_{source_number}"
        if title_key not in values and data_key not in values:
            if source_number > 6:
                break
            continue

        title = str(values.get(title_key, f"Source {source_number}"))
        questions = values.get(data_key, [])
        if not isinstance(questions, list):
            continue

        for question_number, item in enumerate(questions, 1):
            if not isinstance(item, tuple) or len(item) != 2:
                continue
            question, options = item
            if not isinstance(question, str) or not isinstance(options, list):
                continue
            clean_options = tuple(str(option) for option in options)
            cards.append(
                Flashcard(
                    card_id=f"S{source_number}-Q{question_number}",
                    source_number=source_number,
                    source_title=title,
                    question_number=question_number,
                    question=question,
                    options=clean_options,
                )
            )

    return cards


class FlashcardApp(tk.Tk):
    def __init__(self, cards: list[Flashcard], progress_path: Path) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1080x720")
        self.minsize(840, 600)

        self.all_cards = cards
        self.filtered_cards: list[Flashcard] = list(cards)
        self.progress_path = progress_path
        self.known_ids: set[str] = set()
        self.review_ids: set[str] = set()
        self.current_index = 0
        self.show_answer = False

        self.source_var = tk.StringVar(value=ALL_SOURCES_LABEL)
        self.search_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="Toutes")
        self.status_var = tk.StringVar()
        self.counter_var = tk.StringVar()

        self._load_progress()
        self._configure_style()
        self._build_ui()
        self._bind_events()
        self._apply_filters(reset_index=True)

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI Semibold", 18))
        style.configure("Meta.TLabel", foreground="#4c5564")
        style.configure("Accent.TButton", font=("Segoe UI Semibold", 10))
        style.configure("Card.TFrame", background="#f8fafc", relief="solid", borderwidth=1)
        style.configure("Side.TFrame", background="#eef2f7")
        style.configure("Source.TRadiobutton", background="#eef2f7")

    def _build_ui(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        sidebar = ttk.Frame(self, style="Side.TFrame", padding=(18, 18, 18, 18))
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.columnconfigure(0, weight=1)

        ttk.Label(sidebar, text=APP_TITLE, style="Title.TLabel", background="#eef2f7").grid(
            row=0, column=0, sticky="w", pady=(0, 18)
        )

        ttk.Label(sidebar, text="Source", background="#eef2f7").grid(row=1, column=0, sticky="w")
        source_values = [ALL_SOURCES_LABEL]
        source_values.extend(
            f"Source {number} ({count})"
            for number, count in self._source_counts().items()
        )
        self.source_combo = ttk.Combobox(
            sidebar,
            textvariable=self.source_var,
            values=source_values,
            state="readonly",
            width=28,
        )
        self.source_combo.grid(row=2, column=0, sticky="ew", pady=(4, 14))

        ttk.Label(sidebar, text="Recherche", background="#eef2f7").grid(row=3, column=0, sticky="w")
        search_entry = ttk.Entry(sidebar, textvariable=self.search_var, width=28)
        search_entry.grid(row=4, column=0, sticky="ew", pady=(4, 14))

        ttk.Label(sidebar, text="Statut", background="#eef2f7").grid(row=5, column=0, sticky="w")
        mode_frame = ttk.Frame(sidebar, style="Side.TFrame")
        mode_frame.grid(row=6, column=0, sticky="ew", pady=(4, 14))
        for idx, label in enumerate(("Toutes", "A revoir", "Acquises")):
            ttk.Radiobutton(
                mode_frame,
                text=label,
                value=label,
                variable=self.mode_var,
                style="Source.TRadiobutton",
            ).grid(row=idx, column=0, sticky="w", pady=1)

        ttk.Separator(sidebar).grid(row=7, column=0, sticky="ew", pady=12)

        ttk.Button(sidebar, text="Mélanger", command=self._shuffle).grid(
            row=8, column=0, sticky="ew", pady=3
        )
        ttk.Button(sidebar, text="Réinitialiser la session", command=self._reset_session).grid(
            row=9, column=0, sticky="ew", pady=3
        )
        ttk.Button(sidebar, text="Sauver", command=self._save_progress).grid(
            row=10, column=0, sticky="ew", pady=3
        )

        stats = ttk.Frame(sidebar, style="Side.TFrame")
        stats.grid(row=11, column=0, sticky="sew", pady=(24, 0))
        stats.columnconfigure(0, weight=1)
        self.progress = ttk.Progressbar(stats, mode="determinate", maximum=100)
        self.progress.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(stats, textvariable=self.status_var, style="Meta.TLabel", background="#eef2f7").grid(
            row=1, column=0, sticky="w"
        )

        main = ttk.Frame(self, padding=(22, 18, 22, 18))
        main.grid(row=0, column=1, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(2, weight=1)

        topbar = ttk.Frame(main)
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.columnconfigure(1, weight=1)
        ttk.Label(topbar, textvariable=self.counter_var, style="Meta.TLabel").grid(row=0, column=0, sticky="w")
        self.source_label = ttk.Label(topbar, text="", style="Meta.TLabel", anchor="e")
        self.source_label.grid(row=0, column=1, sticky="e")

        self.title_label = ttk.Label(main, text="", font=("Segoe UI Semibold", 13), wraplength=780)
        self.title_label.grid(row=1, column=0, sticky="ew", pady=(14, 8))

        card_frame = ttk.Frame(main, style="Card.TFrame", padding=18)
        card_frame.grid(row=2, column=0, sticky="nsew")
        card_frame.columnconfigure(0, weight=1)
        card_frame.rowconfigure(0, weight=1)

        self.card_text = ScrolledText(
            card_frame,
            wrap="word",
            font=("Segoe UI", 12),
            padx=14,
            pady=14,
            relief="flat",
            background="#ffffff",
            foreground="#172033",
            insertwidth=0,
        )
        self.card_text.grid(row=0, column=0, sticky="nsew")
        self.card_text.tag_configure("question", font=("Segoe UI Semibold", 14), spacing3=12)
        self.card_text.tag_configure("option", lmargin1=22, lmargin2=44, spacing1=5)
        self.card_text.tag_configure(
            "correct",
            foreground="#156534",
            font=("Segoe UI Semibold", 12),
            lmargin1=22,
            lmargin2=44,
            spacing1=5,
        )
        self.card_text.tag_configure(
            "answer_note",
            foreground="#156534",
            font=("Segoe UI Semibold", 11),
            spacing1=10,
        )
        self.card_text.tag_configure("muted", foreground="#5f6b7a")
        self.card_text.configure(state="disabled")

        actions = ttk.Frame(main)
        actions.grid(row=3, column=0, sticky="ew", pady=(16, 0))
        actions.columnconfigure(2, weight=1)

        ttk.Button(actions, text="Précédente", command=self._previous).grid(row=0, column=0, padx=(0, 8))
        self.flip_button = ttk.Button(actions, text="Voir réponse", command=self._flip, style="Accent.TButton")
        self.flip_button.grid(
            row=0, column=1, padx=(0, 8)
        )
        ttk.Button(actions, text="Suivante", command=self._next).grid(row=0, column=2, sticky="w")

        self.review_button = ttk.Button(actions, text="A revoir", command=self._toggle_review)
        self.review_button.grid(row=0, column=3, padx=(8, 0))
        self.known_button = ttk.Button(actions, text="Acquise", command=self._toggle_known)
        self.known_button.grid(row=0, column=4, padx=(8, 0))

    def _bind_events(self) -> None:
        self.source_combo.bind("<<ComboboxSelected>>", lambda _event: self._apply_filters(reset_index=True))
        self.search_var.trace_add("write", lambda *_args: self._apply_filters(reset_index=True))
        self.mode_var.trace_add("write", lambda *_args: self._apply_filters(reset_index=True))
        self.bind("<Left>", lambda _event: self._previous())
        self.bind("<Right>", lambda _event: self._next())
        self.bind("<space>", lambda _event: self._flip())
        self.bind("r", lambda _event: self._toggle_review())
        self.bind("k", lambda _event: self._toggle_known())
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _source_counts(self) -> dict[int, int]:
        counts: dict[int, int] = {}
        for card in self.all_cards:
            counts[card.source_number] = counts.get(card.source_number, 0) + 1
        return dict(sorted(counts.items()))

    def _selected_source_number(self) -> int | None:
        label = self.source_var.get()
        if label == ALL_SOURCES_LABEL:
            return None
        try:
            return int(label.split()[1])
        except (IndexError, ValueError):
            return None

    def _apply_filters(self, reset_index: bool) -> None:
        selected_source = self._selected_source_number()
        search = self.search_var.get().strip().casefold()
        mode = self.mode_var.get()

        cards = self.all_cards
        if selected_source is not None:
            cards = [card for card in cards if card.source_number == selected_source]
        if search:
            cards = [
                card
                for card in cards
                if search in card.question.casefold()
                or any(search in option.casefold() for option in card.options)
            ]
        if mode == "A revoir":
            cards = [card for card in cards if card.card_id in self.review_ids]
        elif mode == "Acquises":
            cards = [card for card in cards if card.card_id in self.known_ids]

        self.filtered_cards = cards
        if reset_index:
            self.current_index = 0
            self.show_answer = False
        elif self.current_index >= len(self.filtered_cards):
            self.current_index = max(0, len(self.filtered_cards) - 1)

        self._render_card()

    def _current_card(self) -> Flashcard | None:
        if not self.filtered_cards:
            return None
        return self.filtered_cards[self.current_index]

    def _render_card(self) -> None:
        total = len(self.filtered_cards)
        known_total = len(self.known_ids)
        review_total = len(self.review_ids)
        self.status_var.set(f"{known_total} acquises - {review_total} à revoir")

        self.progress.configure(value=(known_total / len(self.all_cards) * 100) if self.all_cards else 0)

        card = self._current_card()
        self.card_text.configure(state="normal")
        self.card_text.delete("1.0", "end")

        if card is None:
            self.counter_var.set("0 / 0")
            self.source_label.configure(text="")
            self.title_label.configure(text="Aucune carte trouvée")
            self.card_text.insert("end", "Aucune question ne correspond aux filtres actuels.", "muted")
            self.card_text.configure(state="disabled")
            self.flip_button.configure(text="Voir réponse")
            self.review_button.configure(text="A revoir")
            self.known_button.configure(text="Acquise")
            return

        self.counter_var.set(f"{self.current_index + 1} / {total}")
        self.source_label.configure(text=f"Source {card.source_number} - Q{card.question_number}")
        self.title_label.configure(text=card.source_title)

        badges = []
        if card.card_id in self.known_ids:
            badges.append("Acquise")
        if card.card_id in self.review_ids:
            badges.append("A revoir")
        if badges:
            self.card_text.insert("end", " / ".join(badges) + "\n\n", "muted")

        self.card_text.insert("end", card.question.strip() + "\n", "question")
        self.card_text.insert("end", "\nOptions\n", "muted")

        answers = ANSWER_KEY.get(card.card_id, ())
        for idx, option in enumerate(card.options, 1):
            if self.show_answer and idx in answers:
                self.card_text.insert("end", f"✓ {idx}. {option.strip()}\n", "correct")
            else:
                self.card_text.insert("end", f"□ {idx}. {option.strip()}\n", "option")

        if self.show_answer:
            if answers:
                labels = ", ".join(str(index) for index in answers)
                self.card_text.insert("end", f"\nRéponse : {labels}", "answer_note")
            else:
                self.card_text.insert(
                    "end",
                    "\nRéponse : aucune des options proposées ne semble correcte.",
                    "answer_note",
                )
            self.flip_button.configure(text="Masquer réponse")
        else:
            self.flip_button.configure(text="Voir réponse")

        self.review_button.configure(
            text="Retirer à revoir" if card.card_id in self.review_ids else "A revoir"
        )
        self.known_button.configure(
            text="Retirer acquise" if card.card_id in self.known_ids else "Acquise"
        )

        self.card_text.configure(state="disabled")

    def _previous(self) -> None:
        if not self.filtered_cards:
            return
        self.current_index = (self.current_index - 1) % len(self.filtered_cards)
        self.show_answer = False
        self._render_card()

    def _next(self) -> None:
        if not self.filtered_cards:
            return
        self.current_index = (self.current_index + 1) % len(self.filtered_cards)
        self.show_answer = False
        self._render_card()

    def _flip(self) -> None:
        if not self.filtered_cards:
            return
        self.show_answer = not self.show_answer
        self._render_card()

    def _shuffle(self) -> None:
        if len(self.filtered_cards) < 2:
            return
        random.shuffle(self.filtered_cards)
        self.current_index = 0
        self.show_answer = False
        self._render_card()

    def _toggle_known(self) -> None:
        card = self._current_card()
        if card is None:
            return
        if card.card_id in self.known_ids:
            self.known_ids.remove(card.card_id)
        else:
            self.known_ids.add(card.card_id)
            self.review_ids.discard(card.card_id)
        self._save_progress(silent=True)
        self._apply_filters(reset_index=False)

    def _toggle_review(self) -> None:
        card = self._current_card()
        if card is None:
            return
        if card.card_id in self.review_ids:
            self.review_ids.remove(card.card_id)
        else:
            self.review_ids.add(card.card_id)
            self.known_ids.discard(card.card_id)
        self._save_progress(silent=True)
        self._apply_filters(reset_index=False)

    def _reset_session(self) -> None:
        answer = messagebox.askyesno(
            APP_TITLE,
            "Réinitialiser les cartes acquises et à revoir ?",
        )
        if not answer:
            return
        self.known_ids.clear()
        self.review_ids.clear()
        self._save_progress(silent=True)
        self._apply_filters(reset_index=False)

    def _load_progress(self) -> None:
        if not self.progress_path.exists():
            return
        try:
            data = json.loads(self.progress_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        self.known_ids = set(data.get("known", []))
        self.review_ids = set(data.get("review", []))

    def _save_progress(self, silent: bool = False) -> None:
        data = {
            "updated_at": datetime.now().isoformat(timespec="seconds"),
            "known": sorted(self.known_ids),
            "review": sorted(self.review_ids),
        }
        self.progress_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        if not silent:
            messagebox.showinfo(APP_TITLE, "Progression sauvegardée.")

    def _close(self) -> None:
        self._save_progress(silent=True)
        self.destroy()


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    data_path = base_dir / "pdf.py"
    progress_path = base_dir / "flashcards_progress.json"

    if not data_path.exists():
        messagebox.showerror(APP_TITLE, f"Fichier introuvable : {data_path}")
        return

    try:
        cards = load_flashcards(data_path)
    except Exception as exc:  # noqa: BLE001 - show a GUI error for startup failures.
        messagebox.showerror(APP_TITLE, f"Impossible de charger les questions :\n{exc}")
        return

    if not cards:
        messagebox.showerror(APP_TITLE, "Aucune question n'a été trouvée dans pdf.py.")
        return

    app = FlashcardApp(cards, progress_path)
    app.mainloop()


if __name__ == "__main__":
    main()

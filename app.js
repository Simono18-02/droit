const STORAGE_KEY = "flashcards-qcm-droit-progress-v3";
const LEGACY_KEY = "flashcards-qcm-droit-progress";

const data = window.FLASHCARDS_DATA || { cards: [], chapters: [] };
const cards = data.cards || [];
const chapters = data.chapters || [];
const cardById = new Map(cards.map((card) => [card.id, card]));

const state = {
  filtered: [...cards],
  index: 0,
  selectedAnswers: new Set(),
  answered: false,
  optionOrders: new Map(),
  sessionStartedAt: Date.now(),
  sessionCorrect: 0,
  sessionAnswered: 0,
  activeTab: "train",
  selectedChapters: new Set(chapters.map((chapter) => chapter.id)),
  source: "all",
  search: "",
  mode: "all",
  difficulty: "all",
  limit: "all",
  settings: {
    instantCorrection: true,
    shuffleOptions: false,
    darkMode: false,
    compactMode: false,
  },
  known: new Set(),
  review: new Set(),
  bookmarks: new Set(),
  attempts: {},
  streak: 0,
  bestStreak: 0,
};

const els = {
  deckSummary: document.querySelector("#deckSummary"),
  chapterFilters: document.querySelector("#chapterFilters"),
  allChaptersButton: document.querySelector("#allChaptersButton"),
  noChaptersButton: document.querySelector("#noChaptersButton"),
  sourceFilter: document.querySelector("#sourceFilter"),
  searchInput: document.querySelector("#searchInput"),
  modeFilter: document.querySelector("#modeFilter"),
  difficultyFilter: document.querySelector("#difficultyFilter"),
  limitFilter: document.querySelector("#limitFilter"),
  instantCorrectionToggle: document.querySelector("#instantCorrectionToggle"),
  shuffleOptionsToggle: document.querySelector("#shuffleOptionsToggle"),
  darkModeToggle: document.querySelector("#darkModeToggle"),
  compactModeToggle: document.querySelector("#compactModeToggle"),
  statusText: document.querySelector("#statusText"),
  percentText: document.querySelector("#percentText"),
  progressBar: document.querySelector("#progressBar"),
  chapterStats: document.querySelector("#chapterStats"),
  tabs: [...document.querySelectorAll(".tab")],
  views: [...document.querySelectorAll(".view")],
  counterText: document.querySelector("#counterText"),
  sessionScoreText: document.querySelector("#sessionScoreText"),
  timerText: document.querySelector("#timerText"),
  sourceTitle: document.querySelector("#sourceTitle"),
  sourceText: document.querySelector("#sourceText"),
  badgeList: document.querySelector("#badgeList"),
  questionText: document.querySelector("#questionText"),
  answerHint: document.querySelector("#answerHint"),
  optionsList: document.querySelector("#optionsList"),
  feedbackBox: document.querySelector("#feedbackBox"),
  feedbackTitle: document.querySelector("#feedbackTitle"),
  answerNote: document.querySelector("#answerNote"),
  courseNoteBox: document.querySelector("#courseNoteBox"),
  courseNoteText: document.querySelector("#courseNoteText"),
  courseNoteSource: document.querySelector("#courseNoteSource"),
  previousButton: document.querySelector("#previousButton"),
  submitButton: document.querySelector("#submitButton"),
  nextButton: document.querySelector("#nextButton"),
  bookmarkButton: document.querySelector("#bookmarkButton"),
  reviewButton: document.querySelector("#reviewButton"),
  knownButton: document.querySelector("#knownButton"),
  dashSessionScore: document.querySelector("#dashSessionScore"),
  dashGlobalScore: document.querySelector("#dashGlobalScore"),
  dashStreak: document.querySelector("#dashStreak"),
  dashBestStreak: document.querySelector("#dashBestStreak"),
  dashAttempts: document.querySelector("#dashAttempts"),
  dashWrong: document.querySelector("#dashWrong"),
  dashboardChapters: document.querySelector("#dashboardChapters"),
  newSessionButton: document.querySelector("#newSessionButton"),
  exportButton: document.querySelector("#exportButton"),
  importInput: document.querySelector("#importInput"),
  resetButton: document.querySelector("#resetButton"),
  exportText: document.querySelector("#exportText"),
  shuffleButton: document.querySelector("#shuffleButton"),
  sortDefaultButton: document.querySelector("#sortDefaultButton"),
  wrongOnlyButton: document.querySelector("#wrongOnlyButton"),
  printButton: document.querySelector("#printButton"),
  cardList: document.querySelector("#cardList"),
};

function emptyAttempt() {
  return { attempts: 0, correct: 0, wrong: 0, lastCorrect: null, lastAt: null };
}

function getAttempt(cardId) {
  return state.attempts[cardId] || emptyAttempt();
}

function loadProgress() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || localStorage.getItem(LEGACY_KEY) || "{}");
    state.known = new Set(Array.isArray(saved.known) ? saved.known : []);
    state.review = new Set(Array.isArray(saved.review) ? saved.review : []);
    state.bookmarks = new Set(Array.isArray(saved.bookmarks) ? saved.bookmarks : []);
    state.attempts = saved.attempts && typeof saved.attempts === "object" ? saved.attempts : {};
    state.streak = Number(saved.streak || 0);
    state.bestStreak = Number(saved.bestStreak || 0);
    if (saved.settings) state.settings = { ...state.settings, ...saved.settings };
    if (Array.isArray(saved.selectedChapters) && saved.selectedChapters.length) {
      state.selectedChapters = new Set(saved.selectedChapters);
    }
  } catch {
    state.known = new Set();
    state.review = new Set();
    state.bookmarks = new Set();
    state.attempts = {};
  }
}

function saveProgress() {
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      updatedAt: new Date().toISOString(),
      known: [...state.known].sort(),
      review: [...state.review].sort(),
      bookmarks: [...state.bookmarks].sort(),
      attempts: state.attempts,
      streak: state.streak,
      bestStreak: state.bestStreak,
      settings: state.settings,
      selectedChapters: [...state.selectedChapters],
    }),
  );
}

function chapterCount(chapterId) {
  return cards.filter((card) => card.chapter?.id === chapterId).length;
}

function populateChapters() {
  els.chapterFilters.replaceChildren();
  chapters.forEach((chapter) => {
    const label = document.createElement("label");
    label.className = "chapter-choice";
    const input = document.createElement("input");
    input.type = "checkbox";
    input.value = chapter.id;
    input.checked = state.selectedChapters.has(chapter.id);
    const span = document.createElement("span");
    span.textContent = `${chapter.title} (${chapterCount(chapter.id)})`;
    label.append(input, span);
    els.chapterFilters.append(label);
  });
}

function populateSources() {
  const counts = cards.reduce((acc, card) => {
    acc.set(card.sourceNumber, (acc.get(card.sourceNumber) || 0) + 1);
    return acc;
  }, new Map());
  els.sourceFilter.replaceChildren(new Option("Toutes les sources", "all"));
  [...counts.entries()].sort((a, b) => a[0] - b[0]).forEach(([source, count]) => {
    els.sourceFilter.add(new Option(`Source ${source} (${count})`, String(source)));
  });
}

function setSettingsControls() {
  els.instantCorrectionToggle.checked = state.settings.instantCorrection;
  els.shuffleOptionsToggle.checked = state.settings.shuffleOptions;
  els.darkModeToggle.checked = state.settings.darkMode;
  els.compactModeToggle.checked = state.settings.compactMode;
  document.body.classList.toggle("dark", state.settings.darkMode);
  document.body.classList.toggle("compact", state.settings.compactMode);
}

function queryMatches(card, query) {
  if (!query) return true;
  const haystack = [
    card.question,
    ...(card.options || []),
    card.courseNote?.text || "",
    card.courseNote?.source || "",
    card.chapter?.title || "",
  ].join(" ").toLocaleLowerCase("fr-FR");
  return haystack.includes(query);
}

function cardMatchesMode(card) {
  const attempt = getAttempt(card.id);
  if (state.mode === "unseen") return attempt.attempts === 0;
  if (state.mode === "wrong") return attempt.wrong > 0 || attempt.lastCorrect === false;
  if (state.mode === "review") return state.review.has(card.id);
  if (state.mode === "known") return state.known.has(card.id);
  if (state.mode === "bookmarked") return state.bookmarks.has(card.id);
  if (state.mode === "without-note") return !card.courseNote?.source;
  return true;
}

function applyFilters(resetIndex = true) {
  const query = state.search.trim().toLocaleLowerCase("fr-FR");
  const limit = state.limit === "all" ? Infinity : Number(state.limit);
  state.filtered = cards
    .filter((card) => state.selectedChapters.has(card.chapter?.id))
    .filter((card) => state.source === "all" || String(card.sourceNumber) === state.source)
    .filter((card) => state.difficulty === "all" || card.difficulty === state.difficulty)
    .filter((card) => queryMatches(card, query))
    .filter(cardMatchesMode)
    .slice(0, limit);

  if (resetIndex) {
    state.index = 0;
    state.selectedAnswers.clear();
    state.answered = false;
  } else if (state.index >= state.filtered.length) {
    state.index = Math.max(0, state.filtered.length - 1);
  }
  render();
}

function currentCard() {
  return state.filtered[state.index] || null;
}

function sameAnswers(a, b) {
  if (b.length === 0) return a.size === 1 && a.has(0);
  if (a.size !== b.length) return false;
  return b.every((answer) => a.has(answer));
}

function displayQuestion(card) {
  if (card.answers.length <= 1) {
    return card.question
      .replace(/\s*\((?:plusieurs réponses|plusieurs réponses possibles|réponses possibles)\)\s*/gi, " ")
      .replace(/\s+/g, " ")
      .trim();
  }
  return card.question.trim();
}

function orderedOptions(card) {
  if (card.answers.length === 0) {
    return [
      ...card.options.map((text, index) => ({ text, number: index + 1 })),
      { text: "Aucune des réponses proposées", number: 0 },
    ];
  }
  if (!state.settings.shuffleOptions) {
    return card.options.map((text, index) => ({ text, number: index + 1 }));
  }
  if (!state.optionOrders.has(card.id)) {
    const order = card.options.map((text, index) => ({ text, number: index + 1 }));
    for (let i = order.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [order[i], order[j]] = [order[j], order[i]];
    }
    state.optionOrders.set(card.id, order);
  }
  return state.optionOrders.get(card.id);
}

function renderStats() {
  const knownCount = state.known.size;
  const reviewCount = state.review.size;
  const percent = cards.length ? Math.round((knownCount / cards.length) * 100) : 0;
  const sessionPercent = state.sessionAnswered ? Math.round((state.sessionCorrect / state.sessionAnswered) * 100) : 0;
  els.statusText.textContent = `${knownCount} acquises - ${reviewCount} à revoir`;
  els.percentText.textContent = `${percent}%`;
  els.progressBar.value = percent;
  els.sessionScoreText.textContent = `Score ${state.sessionCorrect}/${state.sessionAnswered} (${sessionPercent}%)`;
  els.deckSummary.textContent = `${cards.length} questions · ${chapters.length} chapitres · ${state.filtered.length} filtrées`;

  els.chapterStats.replaceChildren();
  chapters.forEach((chapter) => {
    const chapterCards = cards.filter((card) => card.chapter?.id === chapter.id);
    const done = chapterCards.filter((card) => state.known.has(card.id)).length;
    const row = document.createElement("div");
    row.className = "chapter-stat";
    row.innerHTML = `<span>${chapter.title.replace("Chapitre ", "Ch. ")}</span><strong>${done}/${chapterCards.length}</strong>`;
    els.chapterStats.append(row);
  });
}

function renderBadges(card) {
  els.badgeList.replaceChildren();
  const badges = [
    [card.chapter?.title || "Sans chapitre", "neutral"],
    [card.difficulty, "neutral"],
  ];
  if (card.multiple) badges.push(["Réponses multiples", "neutral"]);
  if (state.known.has(card.id)) badges.push(["Acquise", "known"]);
  if (state.review.has(card.id)) badges.push(["A revoir", "review"]);
  if (state.bookmarks.has(card.id)) badges.push(["Favori", "bookmark"]);
  badges.forEach(([text, type]) => {
    const badge = document.createElement("span");
    badge.className = `badge ${type}`;
    badge.textContent = text;
    els.badgeList.append(badge);
  });
}

function renderEmpty() {
  els.counterText.textContent = "0 / 0";
  els.sourceText.textContent = "";
  els.sourceTitle.textContent = "Aucune carte trouvée";
  els.badgeList.replaceChildren();
  els.questionText.textContent = "Aucune question ne correspond aux filtres actuels.";
  els.answerHint.textContent = "";
  els.optionsList.replaceChildren();
  els.feedbackBox.hidden = true;
  els.courseNoteText.textContent = "";
  els.courseNoteSource.textContent = "";
  [els.previousButton, els.submitButton, els.nextButton, els.bookmarkButton, els.reviewButton, els.knownButton].forEach((button) => {
    button.disabled = true;
  });
}

function renderCard() {
  const card = currentCard();
  if (!card) {
    renderEmpty();
    return;
  }

  [els.previousButton, els.submitButton, els.nextButton, els.bookmarkButton, els.reviewButton, els.knownButton].forEach((button) => {
    button.disabled = false;
  });

  const attempt = getAttempt(card.id);
  els.counterText.textContent = `${state.index + 1} / ${state.filtered.length}`;
  els.sourceText.textContent = `Source ${card.sourceNumber} - Q${card.questionNumber} · ${attempt.attempts} tentative(s)`;
  els.sourceTitle.textContent = card.sourceTitle;
  els.questionText.textContent = displayQuestion(card);
  els.answerHint.textContent = card.multiple ? "Plusieurs réponses peuvent être correctes." : "Une seule réponse est attendue.";
  if (card.answers.length === 0) {
    els.answerHint.textContent = "Aucune des réponses proposées peut être correcte.";
  }
  els.submitButton.textContent = state.answered ? "Corrigé" : "Valider";
  els.submitButton.disabled = state.answered || state.selectedAnswers.size === 0;
  els.reviewButton.textContent = state.review.has(card.id) ? "Retirer à revoir" : "A revoir";
  els.knownButton.textContent = state.known.has(card.id) ? "Retirer acquise" : "Acquise";
  els.bookmarkButton.textContent = state.bookmarks.has(card.id) ? "Retirer favori" : "Favori";

  renderBadges(card);
  els.optionsList.replaceChildren();
  orderedOptions(card).forEach((option) => {
    const item = document.createElement("li");
    const selected = state.selectedAnswers.has(option.number);
    const correct = card.answers.includes(option.number);
    const noneCorrect = card.answers.length === 0 && option.number === 0;
    item.className = "option";
    if (selected) item.classList.add("selected");
    if (state.answered && (correct || noneCorrect)) item.classList.add("correct");
    if (state.answered && selected && !correct && !noneCorrect) item.classList.add("wrong");

    const label = document.createElement("label");
    const input = document.createElement("input");
    input.type = card.multiple ? "checkbox" : "radio";
    input.name = "answer";
    input.value = String(option.number);
    input.checked = selected;
    input.disabled = state.answered;
    const text = document.createElement("span");
    text.innerHTML = `<strong>${option.number}.</strong> ${option.text.trim()}`;
    label.append(input, text);
    item.append(label);
    els.optionsList.append(item);
  });

  els.courseNoteBox.hidden = false;
  els.courseNoteBox.open = false;
  els.courseNoteText.textContent = card.courseNote?.text || "";
  els.courseNoteSource.textContent = card.courseNote?.source ? `Source : ${card.courseNote.source}` : "Source : non trouvée avec certitude dans les PDF.";

  if (state.answered) {
    const isCorrect = sameAnswers(state.selectedAnswers, card.answers);
    els.feedbackBox.hidden = false;
    els.feedbackBox.className = `feedback ${isCorrect ? "ok" : "bad"}`;
    els.feedbackTitle.textContent = isCorrect ? "Bonne réponse" : "Réponse à revoir";
    els.answerNote.textContent = card.answers.length
      ? `Réponse attendue : ${card.answers.join(", ")}`
      : "Réponse attendue : aucune des options proposées.";
  } else {
    els.feedbackBox.hidden = true;
  }
}

function globalScore() {
  const totals = Object.values(state.attempts).reduce(
    (acc, item) => {
      acc.correct += Number(item.correct || 0);
      acc.attempts += Number(item.attempts || 0);
      acc.wrong += Number(item.wrong || 0);
      return acc;
    },
    { correct: 0, attempts: 0, wrong: 0 },
  );
  return totals;
}

function renderDashboard() {
  const sessionPercent = state.sessionAnswered ? Math.round((state.sessionCorrect / state.sessionAnswered) * 100) : 0;
  const totals = globalScore();
  const globalPercent = totals.attempts ? Math.round((totals.correct / totals.attempts) * 100) : 0;
  els.dashSessionScore.textContent = `${sessionPercent}%`;
  els.dashGlobalScore.textContent = `${globalPercent}%`;
  els.dashStreak.textContent = String(state.streak);
  els.dashBestStreak.textContent = String(state.bestStreak);
  els.dashAttempts.textContent = String(totals.attempts);
  els.dashWrong.textContent = String(totals.wrong);

  els.dashboardChapters.replaceChildren();
  chapters.forEach((chapter) => {
    const chapterCards = cards.filter((card) => card.chapter?.id === chapter.id);
    const attempts = chapterCards.reduce((sum, card) => sum + getAttempt(card.id).attempts, 0);
    const correct = chapterCards.reduce((sum, card) => sum + getAttempt(card.id).correct, 0);
    const known = chapterCards.filter((card) => state.known.has(card.id)).length;
    const percent = attempts ? Math.round((correct / attempts) * 100) : 0;
    const row = document.createElement("div");
    row.className = "chapter-progress";
    row.innerHTML = `
      <div><strong>${chapter.title}</strong><span>${known}/${chapterCards.length} acquises · ${attempts} tentatives</span></div>
      <meter min="0" max="100" value="${percent}"></meter>
      <strong>${percent}%</strong>
    `;
    els.dashboardChapters.append(row);
  });
}

function renderList() {
  els.cardList.replaceChildren();
  state.filtered.forEach((card, index) => {
    const attempt = getAttempt(card.id);
    const row = document.createElement("button");
    row.type = "button";
    row.className = "list-row";
    row.innerHTML = `
      <span>${index + 1}. ${card.question}</span>
      <small>${card.chapter?.title || "Sans chapitre"} · ${card.difficulty} · ${attempt.correct}/${attempt.attempts}</small>
    `;
    row.addEventListener("click", () => {
      state.index = index;
      switchTab("train");
      resetAnswerState();
      render();
    });
    els.cardList.append(row);
  });
}

function render() {
  renderStats();
  renderCard();
  renderDashboard();
  renderList();
}

function resetAnswerState() {
  state.selectedAnswers.clear();
  state.answered = false;
}

function previousCard() {
  if (!state.filtered.length) return;
  state.index = (state.index - 1 + state.filtered.length) % state.filtered.length;
  resetAnswerState();
  render();
}

function nextCard() {
  if (!state.filtered.length) return;
  state.index = (state.index + 1) % state.filtered.length;
  resetAnswerState();
  render();
}

function submitAnswer() {
  const card = currentCard();
  if (!card || state.answered || state.selectedAnswers.size === 0) return;
  const correct = sameAnswers(state.selectedAnswers, card.answers);
  const attempt = getAttempt(card.id);
  attempt.attempts += 1;
  attempt.lastCorrect = correct;
  attempt.lastAt = new Date().toISOString();
  if (correct) {
    attempt.correct += 1;
    state.sessionCorrect += 1;
    state.streak += 1;
    state.bestStreak = Math.max(state.bestStreak, state.streak);
    state.known.add(card.id);
    state.review.delete(card.id);
  } else {
    attempt.wrong += 1;
    state.streak = 0;
    state.review.add(card.id);
    state.known.delete(card.id);
  }
  state.attempts[card.id] = attempt;
  state.sessionAnswered += 1;
  state.answered = true;
  saveProgress();
  if (!state.settings.instantCorrection) nextCard();
  render();
}

function toggleKnown() {
  const card = currentCard();
  if (!card) return;
  if (state.known.has(card.id)) state.known.delete(card.id);
  else {
    state.known.add(card.id);
    state.review.delete(card.id);
  }
  saveProgress();
  applyFilters(false);
}

function toggleReview() {
  const card = currentCard();
  if (!card) return;
  if (state.review.has(card.id)) state.review.delete(card.id);
  else {
    state.review.add(card.id);
    state.known.delete(card.id);
  }
  saveProgress();
  applyFilters(false);
}

function toggleBookmark() {
  const card = currentCard();
  if (!card) return;
  if (state.bookmarks.has(card.id)) state.bookmarks.delete(card.id);
  else state.bookmarks.add(card.id);
  saveProgress();
  render();
}

function shuffleFiltered() {
  for (let i = state.filtered.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [state.filtered[i], state.filtered[j]] = [state.filtered[j], state.filtered[i]];
  }
  state.index = 0;
  resetAnswerState();
  render();
}

function sortDefault() {
  applyFilters(true);
}

function newSession() {
  state.sessionStartedAt = Date.now();
  state.sessionCorrect = 0;
  state.sessionAnswered = 0;
  state.streak = 0;
  state.index = 0;
  resetAnswerState();
  shuffleFiltered();
}

function resetProgress() {
  if (!confirm("Réinitialiser toute la progression, les scores, favoris et erreurs ?")) return;
  state.known.clear();
  state.review.clear();
  state.bookmarks.clear();
  state.attempts = {};
  state.streak = 0;
  state.bestStreak = 0;
  state.sessionCorrect = 0;
  state.sessionAnswered = 0;
  saveProgress();
  applyFilters(false);
}

function exportProgress() {
  els.exportText.hidden = false;
  els.exportText.value = localStorage.getItem(STORAGE_KEY) || "{}";
  els.exportText.select();
}

function importProgress(file) {
  if (!file) return;
  const reader = new FileReader();
  reader.addEventListener("load", () => {
    try {
      const parsed = JSON.parse(String(reader.result || "{}"));
      localStorage.setItem(STORAGE_KEY, JSON.stringify(parsed));
      loadProgress();
      populateChapters();
      setSettingsControls();
      applyFilters(true);
    } catch {
      alert("Le fichier de progression n'est pas lisible.");
    }
  });
  reader.readAsText(file);
}

function switchTab(tab) {
  state.activeTab = tab;
  els.tabs.forEach((button) => button.classList.toggle("active", button.dataset.tab === tab));
  els.views.forEach((view) => view.classList.toggle("active", view.id === `${tab}View`));
}

function bindEvents() {
  els.chapterFilters.addEventListener("change", (event) => {
    if (event.target.type !== "checkbox") return;
    if (event.target.checked) state.selectedChapters.add(event.target.value);
    else state.selectedChapters.delete(event.target.value);
    saveProgress();
    applyFilters(true);
  });
  els.allChaptersButton.addEventListener("click", () => {
    state.selectedChapters = new Set(chapters.map((chapter) => chapter.id));
    populateChapters();
    saveProgress();
    applyFilters(true);
  });
  els.noChaptersButton.addEventListener("click", () => {
    state.selectedChapters.clear();
    populateChapters();
    saveProgress();
    applyFilters(true);
  });
  els.sourceFilter.addEventListener("change", () => {
    state.source = els.sourceFilter.value;
    applyFilters(true);
  });
  els.searchInput.addEventListener("input", () => {
    state.search = els.searchInput.value;
    applyFilters(true);
  });
  els.modeFilter.addEventListener("change", () => {
    state.mode = els.modeFilter.value;
    applyFilters(true);
  });
  els.difficultyFilter.addEventListener("change", () => {
    state.difficulty = els.difficultyFilter.value;
    applyFilters(true);
  });
  els.limitFilter.addEventListener("change", () => {
    state.limit = els.limitFilter.value;
    applyFilters(true);
  });
  [
    [els.instantCorrectionToggle, "instantCorrection"],
    [els.shuffleOptionsToggle, "shuffleOptions"],
    [els.darkModeToggle, "darkMode"],
    [els.compactModeToggle, "compactMode"],
  ].forEach(([control, key]) => {
    control.addEventListener("change", () => {
      state.settings[key] = control.checked;
      if (key === "shuffleOptions") state.optionOrders.clear();
      setSettingsControls();
      saveProgress();
      render();
    });
  });
  els.optionsList.addEventListener("change", (event) => {
    const value = Number(event.target.value);
    const card = currentCard();
    if (!card || !value) return;
    if (!card.multiple || card.answers.length === 0 || value === 0) state.selectedAnswers.clear();
    if (event.target.checked) state.selectedAnswers.add(value);
    else state.selectedAnswers.delete(value);
    renderCard();
  });
  els.previousButton.addEventListener("click", previousCard);
  els.nextButton.addEventListener("click", nextCard);
  els.submitButton.addEventListener("click", submitAnswer);
  els.bookmarkButton.addEventListener("click", toggleBookmark);
  els.reviewButton.addEventListener("click", toggleReview);
  els.knownButton.addEventListener("click", toggleKnown);
  els.shuffleButton.addEventListener("click", shuffleFiltered);
  els.sortDefaultButton.addEventListener("click", sortDefault);
  els.wrongOnlyButton.addEventListener("click", () => {
    els.modeFilter.value = "wrong";
    state.mode = "wrong";
    applyFilters(true);
  });
  els.printButton.addEventListener("click", () => window.print());
  els.newSessionButton.addEventListener("click", newSession);
  els.exportButton.addEventListener("click", exportProgress);
  els.importInput.addEventListener("change", () => importProgress(els.importInput.files[0]));
  els.resetButton.addEventListener("click", resetProgress);
  els.tabs.forEach((button) => button.addEventListener("click", () => switchTab(button.dataset.tab)));

  document.addEventListener("keydown", (event) => {
    if (["INPUT", "SELECT", "TEXTAREA"].includes(event.target.tagName)) return;
    if (event.key === "ArrowLeft") previousCard();
    if (event.key === "ArrowRight") nextCard();
    if (event.key === "Enter") submitAnswer();
    if (event.key.toLocaleLowerCase("fr-FR") === "r") toggleReview();
    if (event.key.toLocaleLowerCase("fr-FR") === "k") toggleKnown();
    if (event.key.toLocaleLowerCase("fr-FR") === "f") toggleBookmark();
    if (/^[0-9]$/.test(event.key)) {
      const card = currentCard();
      const value = Number(event.key);
      const maxOption = card.answers.length === 0 ? card.options.length : card.options.length;
      if (!card || value > maxOption || (value === 0 && card.answers.length !== 0) || state.answered) return;
      if (!card.multiple || card.answers.length === 0 || value === 0) state.selectedAnswers.clear();
      if (state.selectedAnswers.has(value)) state.selectedAnswers.delete(value);
      else state.selectedAnswers.add(value);
      renderCard();
    }
  });
}

function tickTimer() {
  const elapsed = Math.floor((Date.now() - state.sessionStartedAt) / 1000);
  const minutes = String(Math.floor(elapsed / 60)).padStart(2, "0");
  const seconds = String(elapsed % 60).padStart(2, "0");
  els.timerText.textContent = `${minutes}:${seconds}`;
}

loadProgress();
populateChapters();
populateSources();
setSettingsControls();
bindEvents();
applyFilters(true);
setInterval(tickTimer, 1000);
tickTimer();

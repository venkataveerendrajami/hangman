// =====================================================
// Hangman — frontend logic
// Talks to the Flask backend via three JSON endpoints:
//   GET  /api/state    -> current game state
//   POST /api/guess     -> submit a letter guess
//   POST /api/restart   -> start a brand new game
// =====================================================

const ALPHABET = "abcdefghijklmnopqrstuvwxyz".split("");

// Cache references to the DOM elements we update often.
const wordDisplayEl = document.getElementById("word-display");
const attemptsLeftEl = document.getElementById("attempts-left");
const attemptsMaxEl = document.getElementById("attempts-max");
const guessedListEl = document.getElementById("guessed-letters");
const messageEl = document.getElementById("message");
const keyboardEl = document.getElementById("keyboard");
const guessFormEl = document.getElementById("guess-form");
const letterInputEl = document.getElementById("letter-input");
const submitBtnEl = document.getElementById("submit-guess");
const restartBtnEl = document.getElementById("restart-btn");
const overlayEl = document.getElementById("result-overlay");
const overlayRestartBtnEl = document.getElementById("overlay-restart-btn");
const resultTitleEl = document.getElementById("result-title");
const resultTextEl = document.getElementById("result-word");

// Build the on-screen A-Z keyboard once, when the page first loads.
function buildKeyboard() {
  keyboardEl.innerHTML = "";
  ALPHABET.forEach((letter) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "key";
    btn.textContent = letter.toUpperCase();
    btn.dataset.letter = letter;
    btn.addEventListener("click", () => submitGuess(letter));
    keyboardEl.appendChild(btn);
  });
}

// Render the underscores / revealed letters as individual boxes.
function renderWordDisplay(displayWord) {
  wordDisplayEl.innerHTML = "";
  const characters = displayWord.split(" ");

  characters.forEach((ch) => {
    const span = document.createElement("span");
    if (ch === "_") {
      span.className = "letter-slot blank";
      span.textContent = "_";
    } else {
      span.className = "letter-slot";
      span.textContent = ch;
    }
    wordDisplayEl.appendChild(span);
  });
}

// Show/hide the hangman body parts based on how many wrong guesses
// have happened so far (1 part per wrong guess, up to max_attempts).
function renderHangman(wrongCount) {
  const parts = document.querySelectorAll("#hangman-svg .part");
  parts.forEach((part) => {
    const partNumber = parseInt(part.dataset.part, 10);
    if (partNumber <= wrongCount) {
      part.classList.add("visible");
    } else {
      part.classList.remove("visible");
    }
  });
}

// Update every on-screen keyboard key to reflect guessed/correct/wrong state.
function renderKeyboard(state) {
  const buttons = keyboardEl.querySelectorAll(".key");
  buttons.forEach((btn) => {
    const letter = btn.dataset.letter;
    const wasGuessed = state.guessed_letters.includes(letter);
    const wasWrong = state.wrong_letters.includes(letter);

    btn.classList.toggle("correct", wasGuessed && !wasWrong);
    btn.classList.toggle("wrong", wasWrong);

    // Disable a key once it has been used, or once the game is over.
    btn.disabled = wasGuessed || state.status !== "playing";
  });
}

// Show the win/lose overlay, or keep it hidden while still playing.
function renderOverlay(state) {
  if (state.status === "playing") {
    overlayEl.classList.add("hidden");
    return;
  }

  const won = state.status === "won";
  resultTitleEl.textContent = won ? "You win! 🎉" : "Game over";
  resultTitleEl.classList.toggle("lost", !won);
  resultTextEl.textContent = state.word ? state.word.toUpperCase() : "";

  overlayEl.classList.remove("hidden");
}

// Master render function: takes a state object from the backend
// and updates every part of the page to match it.
function renderState(state) {
  renderWordDisplay(state.display_word);
  renderHangman(state.max_attempts - state.attempts_left);
  renderKeyboard(state);

  attemptsLeftEl.textContent = state.attempts_left;
  attemptsMaxEl.textContent = state.max_attempts;

  guessedListEl.textContent =
    state.guessed_letters.length > 0
      ? state.guessed_letters.join(", ").toUpperCase()
      : "None yet";

  if (state.message) {
    messageEl.textContent = state.message;
  }

  // Color the message depending on whether the game has ended.
  messageEl.style.color =
    state.status === "lost" ? "var(--red)" :
    state.status === "won" ? "var(--amber)" : "var(--amber)";

  const gameOver = state.status !== "playing";
  letterInputEl.disabled = gameOver;
  submitBtnEl.disabled = gameOver;

  renderOverlay(state);

  if (!gameOver) {
    letterInputEl.value = "";
    letterInputEl.focus();
  }
}

// ===== API calls =====

async function fetchState() {
  const response = await fetch("/api/state");
  const state = await response.json();
  renderState(state);
}

async function submitGuess(letter) {
  if (!letter) return;

  const response = await fetch("/api/guess", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ letter }),
  });
  const state = await response.json();
  renderState(state);
}

async function restartGame() {
  const response = await fetch("/api/restart", { method: "POST" });
  const state = await response.json();
  renderState(state);
}

// ===== Event listeners =====

guessFormEl.addEventListener("submit", (event) => {
  event.preventDefault();
  const letter = letterInputEl.value.trim().toLowerCase();
  submitGuess(letter);
});

restartBtnEl.addEventListener("click", restartGame);
overlayRestartBtnEl.addEventListener("click", restartGame);

// Only allow letters to be typed into the guess box.
letterInputEl.addEventListener("input", () => {
  letterInputEl.value = letterInputEl.value.replace(/[^a-zA-Z]/g, "");
});

// ===== Initial load =====

buildKeyboard();
fetchState();

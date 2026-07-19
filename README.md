# Hangman Game (Flask + HTML/CSS/JS)

A simple, full-stack Hangman game. The backend (Python/Flask) tracks the
secret word and game state per player using Flask sessions. The frontend
(HTML/CSS/JavaScript) is a responsive chalkboard-themed interface where
you guess letters either by typing them or tapping the on-screen keyboard.

## Project structure

```
hangman/
│
├── app.py              # Flask backend: game logic + API routes
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Main page
├── static/
│   ├── style.css        # Styling (responsive, mobile-friendly)
│   └── script.js         # Frontend logic / API calls
└── README.md
```

## How it works

- The secret word is chosen randomly from a fixed list of 5 words:
  `apple`, `banana`, `tiger`, `house`, `river`.
- You have **6 wrong guesses** allowed before the game is lost.
- Each guess updates:
  - the revealed word (underscores for unrevealed letters),
  - the hangman drawing (one new part per wrong guess),
  - the remaining attempts counter,
  - the list of guessed letters.
- Guessing a letter you've already tried is blocked with a friendly message.
- Winning or losing shows a result screen with a **Restart Game** button
  that starts a brand new round with a new random word.

## Setup & run

1. (Recommended) create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate      # on Windows: venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python app.py
   ```

4. Open your browser at:

   ```
   http://127.0.0.1:5000
   ```

## API endpoints (used internally by the frontend)

| Method | Endpoint        | Description                                  |
|--------|-----------------|-----------------------------------------------|
| GET    | `/`             | Renders the game page                         |
| GET    | `/api/state`    | Returns the current game state as JSON        |
| POST   | `/api/guess`    | Submits a letter guess (`{ "letter": "a" }`)  |
| POST   | `/api/restart`  | Starts a brand new game                       |

## Notes

- Game state is stored server-side in the Flask **session** (a signed
  cookie), so the secret word is never sent to the browser until the
  round ends — this also means each browser/tab can play its own game.
- Built using core Python concepts as required: the `random` module,
  `while` loops, `if`/`else` logic, string handling, and lists.

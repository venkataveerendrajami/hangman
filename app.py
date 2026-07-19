"""
Hangman Game - Flask Backend
-----------------------------
This file contains all the game logic for Hangman.

How the game works:
  1. The server picks a random secret word from a fixed list.
  2. The player guesses one letter at a time.
  3. Correct letters are revealed in the word display.
  4. Wrong letters reduce the number of remaining attempts.
  5. The player wins by guessing the whole word before running out
     of attempts, or loses if attempts reach zero.

The game state (the secret word, guessed letters, wrong guess count)
is stored in the Flask "session", which keeps a separate game per
browser/user using a secure cookie.
"""

import random
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)

# A secret key is required for Flask to be able to use sessions.
# In a real production app this should come from an environment
# variable, but a fixed string is fine for this learning project.
app.secret_key = "hangman-secret-key-change-me"

# ---------------------------------------------------------------
# GAME SETTINGS
# ---------------------------------------------------------------

# The fixed list of words the game can choose from (a Python list of strings).
WORD_LIST = ["apple", "banana", "tiger", "house", "river"]

# How many wrong guesses the player is allowed before losing.
MAX_ATTEMPTS = 6


# ---------------------------------------------------------------
# GAME LOGIC HELPERS
# ---------------------------------------------------------------

def start_new_game():
    """Pick a new random word and reset the game state in the session."""
    # random.choice() picks one random item from the WORD_LIST list.
    secret_word = random.choice(WORD_LIST)

    session["word"] = secret_word
    session["guessed_letters"] = []   # list of every letter the player has tried
    session["wrong_guesses"] = 0      # how many of those guesses were wrong
    session.modified = True


def build_masked_word(word, guessed_letters):
    """
    Build the current display of the word using underscores for
    letters that have not been guessed yet, e.g. "a _ p _ e".

    This uses a while loop (as required) to walk through the word
    one character at a time.
    """
    display = ""
    index = 0

    while index < len(word):
        current_letter = word[index]

        # if-else: show the real letter if it has been guessed,
        # otherwise show a blank underscore.
        if current_letter in guessed_letters:
            display += current_letter + " "
        else:
            display += "_ "

        index += 1

    return display.strip()


def is_word_fully_guessed(word, guessed_letters):
    """
    Check whether every letter in the secret word has been guessed.
    Uses a while loop to check each letter one at a time.
    """
    index = 0
    fully_guessed = True

    while index < len(word):
        if word[index] not in guessed_letters:
            fully_guessed = False
            break
        index += 1

    return fully_guessed


def get_game_status(word, guessed_letters, wrong_guesses):
    """Return 'won', 'lost', or 'playing' based on the current state."""
    if is_word_fully_guessed(word, guessed_letters):
        return "won"
    elif wrong_guesses >= MAX_ATTEMPTS:
        return "lost"
    else:
        return "playing"


def get_current_state(message=""):
    """
    Build a dictionary describing the full current game state.
    This is sent to the frontend as JSON after every action.
    """
    # If there is no game in progress yet, start one automatically.
    if "word" not in session:
        start_new_game()

    word = session["word"]
    guessed_letters = session.get("guessed_letters", [])
    wrong_guesses = session.get("wrong_guesses", 0)

    status = get_game_status(word, guessed_letters, wrong_guesses)

    # Work out which guessed letters were wrong, so the frontend can
    # show them separately (e.g. in red) from correct guesses.
    wrong_letters = []
    for letter in guessed_letters:
        if letter not in word:
            wrong_letters.append(letter)

    state = {
        "display_word": build_masked_word(word, guessed_letters),
        "word_length": len(word),
        "guessed_letters": sorted(guessed_letters),
        "wrong_letters": sorted(wrong_letters),
        "attempts_left": MAX_ATTEMPTS - wrong_guesses,
        "max_attempts": MAX_ATTEMPTS,
        "status": status,
        "message": message,
    }

    # Only reveal the secret word once the game has actually ended.
    if status in ("won", "lost"):
        state["word"] = word

    return state


# ---------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------

@app.route("/")
def index():
    """Show the main game page. A fresh game is started automatically
    the first time a player visits (handled inside get_current_state)."""
    return render_template("index.html")


@app.route("/api/state", methods=["GET"])
def api_state():
    """Return the current game state as JSON. Starts a new game if needed."""
    return jsonify(get_current_state())


@app.route("/api/guess", methods=["POST"])
def api_guess():
    """Handle a single letter guess submitted by the player."""
    data = request.get_json(silent=True) or {}
    raw_letter = data.get("letter", "")

    # Clean up the input: strip spaces and make it lowercase.
    letter = str(raw_letter).strip().lower()

    # Make sure a game actually exists before processing the guess.
    if "word" not in session:
        start_new_game()

    word = session["word"]
    guessed_letters = session.get("guessed_letters", [])
    wrong_guesses = session.get("wrong_guesses", 0)
    current_status = get_game_status(word, guessed_letters, wrong_guesses)

    message = ""

    # if-else chain handling every case the guess could fall into.
    if current_status != "playing":
        message = "The game is already over. Start a new game to keep playing."

    elif len(letter) != 1 or not letter.isalpha():
        message = "Please enter a single letter from A to Z."

    elif letter in guessed_letters:
        # Prevent duplicate guesses.
        message = "You already guessed '" + letter + "'. Try a different letter."

    else:
        # This is a brand new, valid guess - record it.
        guessed_letters.append(letter)

        if letter in word:
            message = "Nice! '" + letter + "' is in the word."
        else:
            wrong_guesses += 1
            message = "Sorry, '" + letter + "' is not in the word."

        session["guessed_letters"] = guessed_letters
        session["wrong_guesses"] = wrong_guesses
        session.modified = True

    return jsonify(get_current_state(message=message))


@app.route("/api/restart", methods=["POST"])
def api_restart():
    """Start a completely new game (new random word, reset attempts)."""
    start_new_game()
    return jsonify(get_current_state(message="New game started. Good luck!"))


if __name__ == "__main__":
    # Running with debug=True gives helpful error messages during development.
    app.run(debug=True)

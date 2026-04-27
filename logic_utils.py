import json
import os
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "player_history.json")


def _load_all_history() -> dict:
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def load_player_history(name: str) -> list:
    """Return the list of past games for a player, newest first.

    Returns an empty list if the player has no history.
    """
    all_history = _load_all_history()
    games = all_history.get(name.lower(), [])
    return list(reversed(games))


def save_game_to_history(name: str, game_entry: dict) -> None:
    """Append a completed game entry to the player's history.

    game_entry should contain: date, difficulty, secret, guess_log,
    score, attempts, won, coach_review.
    """
    all_history = _load_all_history()
    key = name.lower()
    if key not in all_history:
        all_history[key] = []
    game_entry["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    all_history[key].append(game_entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(all_history, f)


def get_range_for_difficulty(difficulty: str):
    """Return the inclusive (low, high) guessing range for the given difficulty.

    Returns:
        (1, 20) for Easy, (1, 50) for Normal, (1, 100) for Hard or unknown.
    """
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 50
    if difficulty == "Hard":
        return 1, 100
    return 1, 100


def parse_guess(raw: str, difficulty: str):
    """
    Validate and parse raw text input into an integer guess.

    Args:
        raw: Raw string from the player. May be None or empty.
        difficulty: Current difficulty, used to check the valid range.

    Returns:
        (True, int, None) on success, or (False, None, error_str) on failure.
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    low, high = get_range_for_difficulty(difficulty)
    if value < low or value > high:
        return False, None, f"Enter a number between {low} and {high}."

    return True, value, None


def get_proximity_hint(guess: int, secret: int) -> str:
    """Return a hot/cold emoji hint based on how close the guess is to the secret.

    Returns:
        🔥🔥🔥 Super hot (≤3), 🔥 Warm (≤10), 🌡️ Lukewarm (≤20), 🥶 Cold (>20).
    """
    distance = abs(guess - secret)
    if distance <= 3:
        return "🔥🔥🔥 Super hot!"
    if distance <= 10:
        return "🔥 Warm!"
    if distance <= 20:
        return "🌡️ Lukewarm..."
    return "🥶 Cold"


def check_guess(guess, secret):
    """
    Compare a guess to the secret number.

    Returns:
        A (outcome, message) tuple where outcome is "Win", "Too High", or "Too Low".
    """
    if guess == secret:
        return "Win", "🎉 Correct!"

    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    else:
        return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """
    Apply score changes for a guess outcome.

    Win awards 100 - 10*(attempt_number-1) points (min 10).
    Too High or Too Low each deduct 5 points.

    Returns:
        Updated score as an int.
    """
    if outcome == "Win":
        points = 100 - 10 * (attempt_number - 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score

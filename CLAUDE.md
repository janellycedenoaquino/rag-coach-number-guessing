# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the Streamlit app
python3 -m streamlit run app.py

# Run all tests
pytest

# Run a single test by name
pytest tests/test_game_logic.py::test_winning_guess
```

## Architecture

This is a Streamlit number-guessing game. The codebase is intentionally split so that all game logic lives outside the UI layer and can be unit-tested without Streamlit.

**`logic_utils.py`** — pure Python, no Streamlit imports. Contains every game rule:
- `get_range_for_difficulty` — maps difficulty string to `(low, high)` int tuple
- `parse_guess` — validates raw text input; returns `(ok, int_or_None, err_or_None)`
- `check_guess` — compares guess to secret; returns `(outcome, message)` where outcome is `"Win"`, `"Too High"`, or `"Too Low"`
- `get_proximity_hint` — hot/cold emoji string based on `abs(guess - secret)`
- `update_score` — win awards `max(10, 100 - 10*(attempt-1))` pts; each wrong guess deducts 5
- `load_leaderboard` / `save_to_leaderboard` — read/write `leaderboard.json` (top-5, by score descending, case-insensitive name dedup)

**`app.py`** — Streamlit UI only. All game state lives in `st.session_state`:
- `secret`, `attempts`, `score`, `status` (`"playing"` | `"won"` | `"lost"`), `history`, `guess_log`, `difficulty`, `leaderboard_saved`
- Changing difficulty via the sidebar resets all session state and generates a new secret
- The debug panel (rendered via `styles.py`) always shows the secret number — it is intentionally visible for the educational debugging exercise

**`styles.py`** — all CSS and HTML string constants/generators. Functions like `leaderboard_html`, `info_panel_html`, and `debug_panel_html` return raw HTML strings consumed by `st.html()` / `st.sidebar.html()`.

**`tests/test_game_logic.py`** — pytest tests covering only `logic_utils.py`. `conftest.py` inserts the repo root into `sys.path` so imports resolve without installation.

**`leaderboard.json`** — generated at runtime; not committed. Persists top-5 scores across sessions.

**`.streamlit/config.toml`** — sets the app's color theme (primary `#ff2d78`, background `#ede9fe`).

## Key constraints

- Keep game logic in `logic_utils.py` and UI in `app.py`. Tests import from `logic_utils` directly and must not require Streamlit.
- `save_to_leaderboard` rejects a new score unless it strictly exceeds the player's existing score — return value signals success (`True`/`False`).
- Difficulty ranges: Easy 1–20 (6 attempts), Normal 1–50 (8 attempts), Hard 1–100 (5 attempts). The attempt limits live only in `app.py`'s `attempt_limit_map`.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the Streamlit app
python3 -m streamlit run app.py

# Run all tests
python3 -m pytest

# Run a single test by name
python3 -m pytest tests/test_game_logic.py::test_winning_guess

# Run the AI evaluation harness
python3 eval_harness.py
```

## Architecture

This is a Streamlit number-guessing game extended with an AI coaching layer. The codebase is split so all logic lives outside the UI and can be unit-tested without Streamlit.

**`logic_utils.py`** — pure Python, no Streamlit. Contains all game rules and persistence:
- `get_range_for_difficulty` — maps difficulty string to `(low, high)` int tuple
- `parse_guess` — validates raw text input; returns `(ok, int_or_None, err_or_None)`
- `check_guess` — compares guess to secret; returns `(outcome, message)` where outcome is `"Win"`, `"Too High"`, or `"Too Low"`
- `get_proximity_hint` — hot/cold emoji string based on `abs(guess - secret)`
- `update_score` — win awards `max(10, 100 - 10*(attempt-1))` pts; each wrong guess deducts 5
- `load_player_history(name)` / `save_game_to_history(name, entry)` — read/write `player_history.json` (keyed by lowercase player name; each entry stores date, difficulty, secret, guess_log, score, attempts, won, coach_review)

**`ai_coach.py`** — pure Python, no Streamlit. RAG + Ollama coaching engine:
- `get_mid_game_tip(guess_log, difficulty, attempts_left, secret)` — retrieves the most relevant strategy doc from `knowledge_base/`, builds a prompt, calls Ollama (`llama3.2`), runs the response through guardrails, returns a coaching tip string
- `get_postgame_review(guess_log, secret, difficulty, won)` — generates a post-game breakdown via Ollama
- Internal `_retrieve(difficulty, guess_count, attempts_left)` — rule-based doc selection (Hard mode → hard_mode_tips, low attempts → common_mistakes, etc.)

**`guardrails.py`** — pure Python. Safety layer between app and Ollama:
- `sanitize_prompt(prompt, secret)` — replaces any mention of the secret in the prompt with `[HIDDEN]` before sending to Ollama
- `validate_response(response, secret)` — blocks any AI response containing the secret or any number within ±2 of it; returns `(safe, text_or_fallback)`

**`knowledge_base/`** — 5 plain-text strategy docs used as the RAG retrieval source:
`binary_search.txt`, `hot_cold_hints.txt`, `common_mistakes.txt`, `hard_mode_tips.txt`, `scoring_strategy.txt`

**`app.py`** — Streamlit UI only. Flow:
1. Sign-in screen on first load (`player_name` stored in session state)
2. Sidebar shows difficulty settings + player's full game history (expandable cards with past coach reviews)
3. Each guess → `logic_utils` validates and scores → `ai_coach` generates a mid-game tip → displayed below the guess history table
4. Game ends → coach generates post-game review → game auto-saved to `player_history.json` → history updates in sidebar

Session state keys: `player_name`, `secret`, `attempts`, `score`, `status` (`"playing"` | `"won"` | `"lost"`), `history`, `guess_log`, `difficulty`, `history_saved`, `coach_tip`, `coach_review`

**`styles.py`** — all CSS and HTML string constants/generators. `info_panel_html` and `debug_panel_html` return raw HTML consumed by `st.html()`.

**`eval_harness.py`** — standalone evaluation script. Runs 6 predefined game scenarios through the coach and 6 guardrail cases, prints a pass/fail summary. No Streamlit required.

**`tests/`** — two pytest files:
- `test_game_logic.py` — covers all `logic_utils.py` functions
- `test_guardrails.py` — 13 tests covering `sanitize_prompt` and `validate_response` edge cases

**`player_history.json`** — generated at runtime; not committed. Persists all player game history across sessions.

**`.streamlit/config.toml`** — sets the app's color theme (primary `#ff2d78`, background `#ede9fe`).

## Key constraints

- Keep game logic in `logic_utils.py`, AI logic in `ai_coach.py`, and safety logic in `guardrails.py`. None of these may import Streamlit — tests run without it.
- `ai_coach.py` receives the secret only to pass to guardrails — it must never place the raw secret value directly in the Ollama prompt.
- Ollama must be running locally (`ollama serve`) with `llama3.2` pulled for the coach to work. The app degrades gracefully to fallback strings if Ollama is unreachable.
- Difficulty ranges: Easy 1–20 (6 attempts), Normal 1–50 (8 attempts), Hard 1–100 (5 attempts). Attempt limits live only in `app.py`'s `attempt_limit_map`.
- Post-game history is saved once per game via the `history_saved` session state flag to prevent duplicate entries on reruns.

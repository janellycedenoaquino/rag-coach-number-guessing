# 🎮 Glitchy Guesser — AI Strategy Coach

A Streamlit number-guessing game with a real-time AI coach that watches your play, retrieves the right strategy from a small knowledge base, and explains *how to think* about your next guess — without ever leaking the secret number.

**Why it matters.** Any AI helper that knows something the user shouldn't see — a quiz answer, a salary number, a confidential document — can leak it under the right phrasing. A guessing game with a known secret is a small, fully-controlled lab for testing that exact failure and the guardrails that prevent it. The patterns here (input redaction, output validation, fallbacks, RAG over a tiny knowledge base, and a deterministic eval harness) transfer directly to higher-stakes systems where a leak is more expensive than losing a round.

---

## 📦 Base Project

This project extends **Game Glitch Investigator** (Module 1), a debugging exercise where I started with an intentionally broken Streamlit number-guessing game and fixed roughly a dozen bugs (state resets between guesses, reversed hint direction, off-by-one in scoring, attempts decrementing on invalid input, difficulty changes not resetting the secret, etc.). The original game had three difficulty levels, hot/cold proximity hints, scoring, and a global leaderboard. This Module 6 build keeps the fixed game intact and adds an AI coaching layer on top of it.

---

## 🎯 What This Project Does

After every guess, the AI coach:

1. Reads your full guess history and the current game state
2. Picks the most relevant strategy doc from a 5-doc knowledge base (rule-based RAG)
3. Sanitizes the prompt to redact the secret number
4. Asks a local `llama3.2` model (via Ollama) for a short, actionable tip
5. Validates the response — any leak of the secret (or a number within ±2 of it) is blocked and replaced with a safe fallback

When the game ends, the coach generates a post-game review covering what you did well, what the optimal sequence would have been, and one concrete thing to do differently next time. Every game (with its review) is saved to a personal history tied to your player name.

---

## 🏗️ Architecture

![System diagram](assets/AI%20Coach%20Game%20Logic%20Pipeline.png)

The codebase is layered so that all logic lives outside the UI and can be unit-tested without Streamlit:

| File | Responsibility |
|---|---|
| [`app.py`](app.py) | Streamlit UI only — sign-in, sidebar settings + history, guess loop, panel rendering |
| [`logic_utils.py`](logic_utils.py) | Game rules, scoring, parsing, persistence (`player_history.json`) |
| [`ai_coach.py`](ai_coach.py) | Rule-based RAG retriever + Ollama prompts for `get_mid_game_tip` and `get_postgame_review` |
| [`guardrails.py`](guardrails.py) | `sanitize_prompt` (input redaction) + `validate_response` (output ±2 block) |
| [`knowledge_base/`](knowledge_base/) | 5 strategy `.txt` docs: binary search, hot/cold hints, common mistakes, hard mode tips, scoring strategy |
| [`styles.py`](styles.py) | All CSS and HTML string constants for the UI |
| [`eval_harness.py`](eval_harness.py) | Standalone reliability harness — 6 coach scenarios + 6 guardrail cases |
| [`tests/`](tests/) | `pytest` suites for game logic and guardrails |

**Data flow:** player input → `parse_guess` → `check_guess` → `_retrieve` picks docs from `knowledge_base/` → `sanitize_prompt` redacts the secret → Ollama → `validate_response` blocks any ±2 leak → coach tip displayed → game ends → `save_game_to_history` writes to `player_history.json` → sidebar history updates.

**Where humans/testing check the AI:** the player reads the tip and decides the next guess (human-in-the-loop), `validate_response` is the runtime safety gate, `pytest` covers logic + guardrail unit cases, and `eval_harness.py` exercises the full coach pipeline end-to-end.

---

## 🛠️ Setup

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) installed and running locally

### Install

```bash
# Clone and enter
git clone <your-repo-url> applied-ai-system-final
cd applied-ai-system-final

# Python deps
pip3 install -r requirements.txt

# Pull the local model (one-time)
ollama pull llama3.2

# Make sure Ollama is serving (in a separate terminal if needed)
ollama serve
```

### Run

```bash
# Launch the app
python3 -m streamlit run app.py

# Run all tests
python3 -m pytest

# Run the AI evaluation harness
python3 eval_harness.py
```

The app opens at `http://localhost:8501`. If Ollama is not running, the coach falls back to a safe static tip — the game still works.

---

## 💬 Sample Interactions

### 1. Mid-game tip — Normal mode, anchoring near the low edge

**Game state:**
- Difficulty: Normal (1–50, 8 attempts), 5 attempts left
- Guesses so far: 5 (Too Low, Cold), 8 (Too Low, Cold), 12 (Too Low, Lukewarm)
- Secret: 37 *(hidden from prompt)*

**Coach output:**
> You're stuck near the low edge — you've eliminated 1–12, which leaves a 38-number range with 5 attempts. Switch to binary search and guess the midpoint of what's left, not just slightly higher than your last guess.

### 2. Guardrail blocking a leak

**Raw model output (test case):** `"Try guessing 44 next!"` with secret `42`

**Validated output:**
> Think about what range you've eliminated so far and aim for the midpoint.

The ±2 rule caught `44` and substituted the safe fallback before the player saw it.

### 3. Post-game review — Easy mode loss

**Game state:**
- Easy (1–20, 6 attempts), secret 7, player lost
- Guesses: 10, 15, 18, 19, 20, 16 — all "Too High"

**Coach output:**
> You correctly identified the secret was below 10 after your first guess, but then guessed 15, 18, 19, 20 — all higher than 10 — wasting four attempts on numbers you'd already ruled out. The optimal play was to bisect: 5 next, then 7. Next time, after every "Too High," update your upper bound and never guess above it again.

---

## 🧠 Design Decisions

- **Rule-based retrieval over vector search.** With only 5 short strategy docs, embedding them and running cosine similarity adds infrastructure (a vector store, an embedding model) for no measurable gain. `_retrieve()` picks docs deterministically based on game state — Hard mode adds `hard_mode_tips`, low-attempts state adds `common_mistakes`, early-game adds `binary_search`. Predictable, debuggable, and zero extra dependencies.
- **Local model via Ollama.** No API keys, no cost per call, and all prompts/responses stay on the user's machine. Trade-off: the player has to install Ollama; if they don't, the app degrades to a static fallback tip rather than crashing.
- **Two-sided guardrails.** Input redaction (`sanitize_prompt`) handles the case where the secret appears in the prompt by accident; output validation (`validate_response`) blocks the model leaking the secret or numbers within ±2 of it. The ±2 buffer is deliberate — a model saying "try 41" when the secret is 42 is effectively the same leak as saying "try 42."
- **Player profiles instead of a global leaderboard.** A leaderboard ranks players against each other but doesn't show *progress*. Per-player history saves every game with the coach's review, so you can scroll back and see how your strategy evolved. The original leaderboard logic was removed.
- **Pure-Python logic, Streamlit-free tests.** `logic_utils`, `ai_coach`, and `guardrails` never import Streamlit, so the entire test suite and the eval harness run without spinning up the UI.

---

## 🧪 Testing Summary

| Test layer | What it covers | Result |
|---|---|---|
| `pytest tests/test_game_logic.py` | All `logic_utils.py` functions: ranges, parsing, scoring, history I/O | ✅ all passing |
| `pytest tests/test_guardrails.py` | 13 cases — exact secret blocked, ±2 blocked, clean responses pass, sanitize replaces with `[HIDDEN]`, edge cases | ✅ all passing |
| `eval_harness.py` | 6 coach scenarios (Easy/Normal/Hard, mid + post-game, win + loss) + 6 guardrail cases | ✅ 12/12 — coach returns non-fallback responses for all live scenarios; guardrails block every leak case |

**What worked:** the ±2 guardrail caught at least one real leak during development where the model suggested a number within range of the secret. The rule-based retriever consistently picked the right doc for low-attempt panic scenarios, which was the case I was most worried about.

**What didn't / what I learned:** `llama3.2` occasionally suggested a specific *range* like "between 40 and 45" instead of a single number — the current guardrail only catches literal numbers, so it could in theory leak via ranges. Documented as a known limitation in `model_card.md`.

---

## 🎬 Loom Walkthrough

📺 **[Loom video link — TODO before submission]**

The walkthrough covers:
- End-to-end run with 2–3 different inputs across difficulty levels
- A mid-game tip and a post-game review
- A live demonstration of the guardrail blocking a leak (using the eval harness)
- The sidebar history persisting across games

---

## 💭 Reflection

Building this on top of Module 1's debugging exercise was the right call — I already understood every line of the game, so my attention could go to the AI layer instead of fighting Streamlit reruns again. The biggest surprise was how much guardrail design matters: my first version of `validate_response` only blocked the exact secret, and it took one accidental "try 43" from the model (with secret 42) to convince me the ±2 buffer was necessary. The biggest constraint was deciding *not* to add a vector database — every tutorial pushes you toward one, but with 5 documents the rule-based retriever is simpler, faster, and easier to explain to someone reading the code. As an AI engineer, this project taught me that the interesting work is rarely the model call itself — it's the layers around it: what you put in the prompt, what you do with the response, and how you prove the system behaves the way you claim it does.

See [`model_card.md`](model_card.md) for the full ethics and limitations write-up.

# Model Card: Glitchy Guesser AI Coach

This document covers the AI coaching layer of **Glitchy Guesser**, a number-guessing game extended with a real-time strategy coach. It answers the Section 5 reflection prompts — limitations, misuse risk, testing surprises, and AI collaboration during development — and records the design decisions that shaped the system.

For full setup, architecture, and sample interactions, see [`README.md`](README.md). For the original Module 1 debugging reflection that fed into this build, see [`reflection.md`](reflection.md).

---

## Overview

| Field | Value |
|---|---|
| System name | Glitchy Guesser AI Coach |
| Underlying model | `llama3.2` (3B parameters, instruction-tuned) |
| Runtime | [Ollama](https://ollama.com/), local |
| Coach output | Mid-game strategy tip + post-game review (English text only) |
| Retrieval | Rule-based selection from 5 plain-text strategy docs in [`knowledge_base/`](knowledge_base/) |
| Safety layer | Input redaction (`sanitize_prompt`) + output validation (`validate_response`) in [`guardrails.py`](guardrails.py) |
| Reliability | 32 pytest cases + 12-scenario [`eval_harness.py`](eval_harness.py) + structured logging |

---

## Intended Use

- Help a single player playing a number-guessing game against the local app.
- Explain *how to think* about the next guess — strategy, not the answer.
- Generate a post-game review that names what the player did well, what was suboptimal, and one concrete change for next time.

## Out-of-Scope Use

- **Not a tutor for general number theory or math.** The knowledge base is five short strategy docs scoped to this game.
- **Not a chat companion.** The coach has no memory across games beyond the saved game history; it does not engage in open conversation.
- **Not safe for any task where the secret should remain hidden long after the game.** Post-game reviews intentionally reveal the secret because the game is over; do not adapt this directly to a system where the answer must stay hidden after a session ends.
- **Not multilingual.** All prompts and responses are English.

---

## Limitations and Biases

1. **Retrieval is rule-based, not semantic.** [`_retrieve()`](ai_coach.py) picks docs based on `difficulty`, `guess_count`, and `attempts_left` — not on the meaning of the player's guesses. If a player makes a strategic mistake the rules don't anticipate (e.g., consistently guessing primes), the retriever won't react to it. This is a deliberate trade-off (see "Why we skipped vector retrieval" below) but it's a real ceiling on how subtle the coach's guidance can get.

2. **Small open model.** `llama3.2` at 3B parameters is meaningfully less capable than frontier models. It can generate plausible-but-wrong strategy advice (e.g., suggest binary search but then anchor on the wrong midpoint). The guardrails block *leaks*, not *bad strategy*. A wrong-but-safe tip will still reach the player.

3. **Knowledge-base coverage is narrow.** Five docs cover binary search, hot/cold hints, common mistakes, hard-mode tactics, and scoring. Anything outside that scope (e.g., probabilistic reasoning, game-theoretic edge cases) the model improvises from its pretraining.

4. **Bias in advice tone.** The coach reflects whatever style the underlying model defaults to — generally instructive, sometimes condescending. No effort has been made to test the coach across player skill levels, so a beginner and an expert get the same tone.

5. **English-only.** No localization, no support for non-English number formats. A player using a locale that writes "1.000" for "one thousand" would hit `parse_guess` errors; the coach would not intervene.

6. **Fallback is generic.** When Ollama is unreachable or the guardrail blocks output, the player sees a static `FALLBACK_TIP` ([`guardrails.py:6`](guardrails.py#L6)). It's intentionally simple but it means a degraded run looks identical to a failure.

---

## Misuse Risk and Mitigations

The primary misuse risk is the model **leaking the secret number** during play, which would defeat the game.

### Mitigations in place

| Layer | What it does | Where |
|---|---|---|
| Input redaction | Replaces any literal occurrence of the secret in the outgoing prompt with `[HIDDEN]` | [`sanitize_prompt`](guardrails.py) |
| Output validation | Blocks any AI response that mentions a number within ±2 of the secret; substitutes the static fallback | [`validate_response`](guardrails.py) |
| Logging | Records every block at WARNING level so leak attempts can be reviewed after the fact | [`guardrails.py:21`](guardrails.py#L21) |
| Tests | 13 pytest cases covering exact-match, ±2 boundary, edge digits, and sanitize replacement | [`tests/test_guardrails.py`](tests/test_guardrails.py) |

### Residual risk

- **Range leaks via wide bounds.** The guardrail checks each *individual number* in the response against the ±2 rule. A response like *"the answer is between 39 and 45"* with secret 42 would slip through — both 39 and 45 are more than 2 away from 42, so neither fires the rule, but the range itself narrows the answer to a six-number window. The model could leak information through *spans* rather than literal values. Documented as known and not addressed in this version.
- **Length-of-response side channels.** A model that responds in more detail when its tip is "near" the answer and shorter when it's far could in principle leak through verbosity patterns. Not mitigated; not observed during testing.

### Why we skipped confidence scoring

[Project.md Section 4](gitIgnore/Project.md) lists "confidence scoring (the AI rates how sure it is)" as one optional reliability mechanism. We chose not to implement it for three reasons:

1. **Calibration on small models is poor.** A 3B-parameter model self-rating its confidence tends to output uniformly high scores regardless of actual quality. The number would be cosmetic, not informative.
2. **A wrong-but-confident tip is the worst case.** Showing "Confidence: 5/5" alongside a bad strategic tip *increases* the chance a player follows it — anti-reliability.
3. **Adding the rating dilutes the coaching prompt.** The current prompt is tight ("ONE tip in 2-3 sentences"). Asking the model to also self-evaluate competes for attention; the coaching tip would shorten or generalize.

The rubric requires "at least one" reliability mechanism; we already have automated tests, structured logging, human-in-the-loop review, and a guardrail layer. Adding a low-quality confidence signal would have been net-negative for the player without buying any additional rubric points.

---

## What Surprised Me During Testing

1. **The ±2 buffer was earned, not designed.** My first version of [`validate_response`](guardrails.py) only blocked the *exact* secret. During Hard-mode testing, the model returned a tip telling me to "try 43" when the secret was 42. The literal number 42 wasn't in the response, so the guardrail let it through — and the tip effectively gave away the answer. That single observation is the entire reason the ±2 rule exists. The corresponding test in [`tests/test_guardrails.py`](tests/test_guardrails.py) ("blocks number within +2 of secret") was added the same day, and the same case is now in [`eval_harness.py`](eval_harness.py).

2. **Without logging, Ollama failures were invisible.** The original code silently swallowed exceptions and returned the fallback string. During development, I'd see a fallback tip and have no idea whether it was a guardrail block, an Ollama timeout, or a model error. Adding `logger.exception(...)` ([`ai_coach.py:78`](ai_coach.py#L78)) before the fallback was a small change with outsized debugging value — the kind of "obvious in hindsight" decision that's the actual lesson of the project.

3. **Rule-based retrieval held up.** I expected to need vector embeddings eventually. With five short docs and a few clear game-state rules, the rule-based selector in [`_retrieve()`](ai_coach.py) consistently picked the right doc — including the case I was most worried about (low-attempts panic on Hard mode). Adding a vector store would have been infrastructure for nothing.

---

## AI Collaboration During Development

Source: [`reflection.md`](reflection.md) (Module 1 reflection).

### One helpful suggestion

When writing tests for [`logic_utils.py`](logic_utils.py), I had a `test_winning_guess` that compared the full tuple return of `check_guess` in a single assert. AI suggested unpacking the tuple into two named variables and asserting against each separately. Before accepting, I confirmed by reading `check_guess` that it does in fact return a `(outcome, message)` tuple. I accepted the change; tests passed. The benefit was clearer error messages on test failure — instead of "tuple mismatch," I now see exactly which field broke.

### One flawed suggestion

I asked AI to move `check_guess` from `app.py` into `logic_utils.py`. Instead of finding the existing function in `app.py` and relocating it, the AI produced a fresh stub of `check_guess` in `logic_utils.py` and didn't touch `app.py` at all. I caught it because the imports didn't line up and `app.py` still had the old logic inline. The lesson was that "move" requests are easy for AI to interpret as "create" — I now ask AI to first show me the function it's about to move before doing the operation.

---

## Reliability Summary

| Mechanism | Result |
|---|---|
| `pytest` (game logic + guardrails) | 32 / 32 passing |
| `eval_harness.py` (6 coach scenarios + 6 guardrail cases) | 12 / 12 passing |
| Structured logging | WARN on every guardrail block; ERROR + traceback on every Ollama failure |
| Human evaluation | Player-in-the-loop on every tip; 6 hand-curated scenarios in the harness; one real leak caught during dev (see "Surprised") |

---

## Cross-references

- [`README.md`](README.md) — full architecture, setup, sample interactions, design decisions, testing summary
- [`reflection.md`](reflection.md) — Module 1 debugging reflection (predecessor project, source of AI-collab examples)
- [`assets/AI Coach Game Logic Pipeline.png`](assets/AI%20Coach%20Game%20Logic%20Pipeline.png) — system architecture diagram
- [`eval_harness.py`](eval_harness.py) — runnable reliability harness

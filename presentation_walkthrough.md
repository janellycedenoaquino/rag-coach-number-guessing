# 🎤 7-Minute Presentation Walkthrough — RAG Coach: Number Guessing

**Target length:** 7 minutes (rubric: [Project.md:124](gitIgnore/Project.md#L124) — 5-7 min)
**Format:** live screen-share + narration. No slides — your "deck" is the running app, the terminal, and your editor with these files open as tabs.
**Repo:** https://github.com/janellycedenoaquino/ReasonQuest
**Loom backup:** https://www.loom.com/share/95c5734fcd894e439ea4ff279ece4ae5 (ready to play if anything live breaks)

---

## ⏱️ Time budget at a glance

| # | Beat | Duration | Cumulative |
|---|---|---|---|
| 1 | Intro + base project context | 0:45 | 0:45 |
| 2 | End-to-end live run | 1:15 | 2:00 |
| 3 | Stretch 1 — Multi-doc RAG | 1:00 | 3:00 |
| 4 | Stretch 2 — Agentic critique loop | 1:15 | 4:15 |
| 5 | Stretch 3 — Reliability + ±2 guardrail story | 1:00 | 5:15 |
| 6 | Stretch 4 — Specialization A/B | 1:15 | 6:30 |
| 7 | What I learned + close | 0:30 | 7:00 |

If you're running long, the trim point is **Beat 6** (skip the live `python3 comparisons/baseline_vs_constrained.py` run — just open `comparisons/results.md` and read the deltas).

---

## ✅ Pre-flight checklist (run 5 minutes before you start)

- [ ] `ollama serve` running in a terminal pane (and `ollama list` shows `llama3.2`)
- [ ] App started fresh: `python3 -m streamlit run app.py` — leave on the sign-in screen
- [ ] Browser zoomed to ~125% so the coach text is legible from the back of the room
- [ ] Two terminal panes ready and font-bumped:
  - **Pane A:** for `pytest` and `eval_harness.py`
  - **Pane B:** for the `comparisons/` script
- [ ] Editor tabs open in this order (left → right):
  1. [`README.md`](README.md) — scrolled to **🧭 Retrieval Strategy** section
  2. [`ai_coach.py`](ai_coach.py) — scrolled to `_retrieve()` (line ~18) and `get_mid_game_tip()` (line ~135)
  3. [`guardrails.py`](guardrails.py) — `validate_response()` visible
  4. [`comparisons/results.md`](comparisons/results.md) — scrolled to the aggregate table
  5. [`model_card.md`](model_card.md) — scrolled to "Specialization" and "What Surprised Me" sections
- [ ] Delete `player_history.json` (or pick a fresh player name like "demo") so the sidebar history demo lands clean
- [ ] Run `python3 eval_harness.py` once before you go on — warms the model so the live demo isn't cold-starting
- [ ] Phone on Do Not Disturb, system notifications silenced

---

## Beat 1 — Intro + base project (0:45)

**Show:** the app on the sign-in screen.

**Say (verbatim ok):**
> "This is RAG Coach: Number Guessing. It started as Game Glitch Investigator in Module 1 — a deliberately-broken Streamlit number-guessing game where I fixed about a dozen bugs: state resets, reversed hints, off-by-one scoring, attempts decrementing on invalid input. For the final project I kept the fixed game and added an AI coaching layer on top — a local llama3.2 model that watches your play, retrieves the right strategy from a small knowledge base, and gives you a tip after every guess without ever leaking the secret number."

**Click:** type your name ("demo") → "Start Playing 🚀".

---

## Beat 2 — End-to-end live run (1:15)

**Show:** the main game screen, Normal difficulty.

**Say:**
> "Let me play one round so you see the full loop."

**Click:** make 2-3 deliberately spread-out guesses (e.g. 25, 12, 38). For each, **point at the coach tip** that appears below the guess history.

**Say (after the second tip):**
> "Every one of those tips is a multi-step pipeline — not just one model call. I'll unpack it in the next minute."

**If you win or run out:** the post-game review pops up.

**Say (pointing at the sidebar):**
> "The game just saved itself to my player history with the coach's review attached. Past games stack here so I can scroll back and see how my strategy evolved."

---

## Beat 3 — Stretch 1: Multi-doc state-aware RAG (1:00)

**Click:** sidebar → start a fresh **Hard** mode game → make one guess (e.g. 50).

**Say:**
> "The retriever isn't a single-doc lookup. It looks at three signals — difficulty, guess count, and attempts left — and combines up to two strategy docs. On Hard mode + first guess, it pulls **both** `hard_mode_tips.txt` and `binary_search.txt` because the player needs the 'five attempts is tight' reality *and* the optimal-play algorithm at the same moment."

**Switch to:** [README.md → 🧭 Retrieval Strategy](README.md#%F0%9F%A7%AD-retrieval-strategy-multi-source-state-aware-rag) section.

**Point at:** the retrieval matrix table.

**Say:**
> "The matrix is in the README — six game-state rows, each with its own doc combination. And it's rule-based, not vector-based: with five short docs, cosine similarity buys nothing, and the rules are debuggable — every tip can be traced back to a doc."

**Switch to:** [ai_coach.py:18-42](ai_coach.py#L18-L42) — `_retrieve()`.

**Say:**
> "Here's the actual retriever — twenty lines of Python, no embedding model, no vector store."

---

## Beat 4 — Stretch 2: Agentic critique loop (1:15)

**Switch back to:** the running Hard game's coach tip.

**Click:** the **🤖 Coach reasoning** expander under the tip.

**Say (walk through the trace):**
> "Each tip goes through a three-stage agent loop. **Draft** — the coach generates a candidate. **Critique** — a second pass asks: does this suggest a number? does it leak the secret? is it vague? If the critic says BAD, the coach **regenerates** with the critique fed back into the prompt. Then the **guardrail** runs the final ±2 check. Every step is observable here — and in the eval harness output."

**Switch to:** Pane A → run `python3 eval_harness.py` (already warm from pre-flight).

**Point at:** any line that says `(REGENERATED)` — usually scenario 3 or 4.

**Say:**
> "Scenario 3 — Hard mode first guess — the critic flagged the first draft, the model rewrote it, and the guardrail double-checked the rewrite. That's a real agentic step chain, not a single model call dressed up."

**If pressed on cost:** "Two to three Ollama calls per tip instead of one. Documented as a limitation in the model card. For a turn-based game, the latency is acceptable."

---

## Beat 5 — Stretch 3 / Reliability: tests + ±2 guardrail story (1:00)

**Switch to:** Pane A → `python3 -m pytest -q`.

**Say (while the output appears):**
> "Thirty-two pytest cases — game logic and guardrails — all passing. Plus the eval harness you just saw, twelve scenarios, also passing."

**Switch to:** [guardrails.py](guardrails.py) → `validate_response`.

**Say:**
> "The interesting part is *why* the guardrail looks like this. My first version only blocked the literal secret. During Hard-mode testing, llama told me to 'try 43' when the secret was 42. The exact number wasn't in the response — but the tip effectively gave away the answer. That single observation is the entire reason the ±2 buffer exists."

**Switch to:** [model_card.md](model_card.md) → "What Surprised Me During Testing" section.

**Say:**
> "I added the regression test the same day. It's now in the pytest suite and the eval harness."

---

## Beat 6 — Stretch 4: Specialization A/B (1:15)

**Switch to:** Pane B → `python3 comparisons/baseline_vs_constrained.py`.

**Say (while it runs — ~30s):**
> "To prove the constrained prompt isn't decorative, I built an A/B. Same four scenarios, two prompt variants — a baseline that's just 'you are a game coach, help them' and the production prompt with retrieval context, length cap, and a no-numbers rule. Single Ollama call each, guardrails off, so we see raw model behavior."

**When the aggregate prints:** point at the three deltas.

**Say:**
> "Constrained prompt is 63% shorter, mentions 74% fewer numbers, and would-be guardrail blocks dropped 50%. The prompt is doing real safety work *before* the guardrail has to fire."

**Switch to:** [comparisons/results.md](comparisons/results.md).

**Say:**
> "The full per-scenario side-by-side is committed to `comparisons/results.md` — every output, both variants, with metrics."

**Trim option:** if you're running long, skip the live run and **start at the `results.md` view** — saves ~30s.

---

## Beat 7 — What I learned + close (0:30)

**Switch to:** [portfolio_reflection.md](portfolio_reflection.md).

**Say:**
> "What I take away from this build: the model call is the smallest part of the system. The engineering lives in the layers around it — retrieval, guardrails, the critique loop, the eval harness, the A/B that proves the prompt earns its keep. I'd rather ship a smaller system I can fully defend than a bigger one I'd have to hand-wave. Repo is at github.com/janellycedenoaquino/ReasonQuest. Thanks — happy to take questions."

---

## 🎯 Anticipated Q&A (with one-sentence answers)

| Likely question | Your answer |
|---|---|
| **"Why didn't you use a vector database?"** | Five short strategy docs and a clear rule set — cosine similarity adds infrastructure for no measurable gain. The rule-based selector is deterministic, debuggable, and zero-dependency. |
| **"Why didn't you add confidence scoring?"** | Calibration on a 3B model is poor and a wrong-but-confident tip is the worst case. I have four other reliability mechanisms — adding a low-quality confidence signal would have been net-negative. The full reasoning is in `model_card.md` under "Why we skipped confidence scoring." |
| **"Could the model still leak the secret?"** | Yes — a residual risk I documented. The guardrail checks each *individual number* against ±2; a response like "the answer is between 39 and 45" with secret 42 would slip through because neither 39 nor 45 is within ±2. Span-based leaks are known and not addressed in this version. |
| **"What happens if Ollama isn't running?"** | The coach degrades gracefully to a static fallback tip — the game still works. Logged at ERROR level so you can tell a degraded run from a failure. |
| **"Why local Ollama instead of an API?"** | No API keys, no per-call cost, prompts stay on the user's machine. Trade-off is the player has to install Ollama. |
| **"How does the agent loop know when to regenerate?"** | The critic LLM emits `OK` or `BAD: <reason>`. On `BAD`, the original prompt plus the critic's reason is fed back to the coach for a rewrite. Code is in [`ai_coach.py:_critique_tip`](ai_coach.py#L61-L95). |
| **"What's the latency cost of the agent loop?"** | Two to three Ollama calls per tip — about 2-4 seconds on local llama3.2 versus one call. Acceptable for turn-based; documented as a limitation. |

---

## 🔗 Quick-jump links (to keep open in editor tabs)

- [README.md](README.md) — 🧭 Retrieval Strategy section
- [ai_coach.py](ai_coach.py) — `_retrieve()` line 18, `get_mid_game_tip()` line 135
- [guardrails.py](guardrails.py) — `validate_response()` line 19
- [eval_harness.py](eval_harness.py) — coach scenarios + guardrail cases
- [comparisons/results.md](comparisons/results.md) — A/B aggregate + per-scenario outputs
- [model_card.md](model_card.md) — "What Surprised Me", "Specialization", "Why we skipped confidence scoring"
- [portfolio_reflection.md](portfolio_reflection.md) — closing line source
- Loom backup: https://www.loom.com/share/95c5734fcd894e439ea4ff279ece4ae5

---

## 🛟 If something breaks live

| Failure | Recovery |
|---|---|
| Streamlit hangs / port in use | Kill with `Ctrl-C`, restart `python3 -m streamlit run app.py` — but if you're mid-presentation, **switch to the Loom** instead of debugging on stage |
| Ollama not responding | Skip Beat 4's live regenerate demo; instead show the harness output from Pane A which already ran during pre-flight |
| `eval_harness.py` very slow | You ran it during pre-flight — **scroll back** in Pane A to the cached output instead of re-running |
| `comparisons/` script slow | Trim option: open `results.md` directly, skip the live run |
| You blank on a number | "63% shorter, 74% fewer numbers, half the near-secret leaks" — those are the only three you need to remember |

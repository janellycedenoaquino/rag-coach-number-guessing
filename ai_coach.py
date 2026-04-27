import logging
import os
import ollama
from guardrails import sanitize_prompt, validate_response, FALLBACK_TIP, FALLBACK_REVIEW

logger = logging.getLogger(__name__)

KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")
MODEL = "llama3.2"
ATTEMPT_LIMITS = {"Easy": 6, "Normal": 8, "Hard": 5}


def _load_doc(filename: str) -> str:
    with open(os.path.join(KNOWLEDGE_BASE_DIR, filename), "r") as f:
        return f.read()


def _retrieve(difficulty: str, guess_count: int, attempts_left: int) -> str:
    """Select the most relevant knowledge base docs for the current game state."""
    docs = []

    if difficulty == "Hard":
        docs.append(_load_doc("hard_mode_tips.txt"))

    if guess_count <= 1:
        docs.append(_load_doc("binary_search.txt"))
    elif attempts_left <= 2:
        docs.append(_load_doc("common_mistakes.txt"))
    elif guess_count <= 3:
        docs.append(_load_doc("hot_cold_hints.txt"))

    if not docs:
        docs.append(_load_doc("binary_search.txt"))

    # Deduplicate, cap at 2 docs to keep the prompt tight
    seen, unique = set(), []
    for doc in docs:
        if doc not in seen:
            seen.add(doc)
            unique.append(doc)

    return "\n\n---\n\n".join(unique[:2])


def _format_guess_log(guess_log: list) -> str:
    if not guess_log:
        return "No guesses yet."
    lines = [
        f"  Guess {entry['#']}: {entry['Guess']} → {entry['Result']} ({entry['Proximity']})"
        for entry in guess_log
    ]
    return "\n".join(lines)


def _draft_tip(prompt: str) -> str:
    """Single Ollama call producing a candidate tip from a fully-built prompt."""
    response = ollama.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"].strip()


def _critique_tip(tip: str, difficulty: str, guess_count: int, secret: int) -> tuple:
    """
    Second LLM pass: review a candidate tip and flag if it (a) suggests specific numbers,
    (b) reveals the secret, or (c) is vague/not actionable.

    Returns (is_ok: bool, reason: str). On any error, defaults to OK so the loop never blocks
    a play session — the guardrail layer is the final safety net.
    """
    critique_prompt = sanitize_prompt(
        f"You are reviewing a coaching tip for a number guessing game.\n"
        f"GAME CONTEXT: Difficulty {difficulty}, {guess_count} guess(es) made.\n"
        f"TIP TO REVIEW: \"{tip}\"\n\n"
        f"Flag this tip if it does ANY of the following:\n"
        f"1. Suggests a specific number to guess (e.g. \"try 30\", \"go with 42\").\n"
        f"2. Hints at or reveals the secret in any way.\n"
        f"3. Is too vague to act on (e.g. \"keep trying\", \"think harder\").\n\n"
        f"Respond with EXACTLY one of these formats — no other text:\n"
        f"OK\n"
        f"BAD: <one short sentence saying which rule was broken>",
        secret,
    )

    try:
        verdict = _draft_tip(critique_prompt)
        upper = verdict.upper().lstrip()
        if upper.startswith("OK"):
            return True, ""
        if upper.startswith("BAD"):
            reason = verdict.split(":", 1)[1].strip() if ":" in verdict else "unspecified"
            return False, reason
        logger.warning("Critic returned unexpected verdict; treating as OK: %s", verdict[:80])
        return True, ""
    except Exception:
        logger.exception("Critique call failed; treating tip as OK and falling through to guardrail")
        return True, ""


def get_mid_game_tip(guess_log: list, difficulty: str, attempts_left: int, secret: int) -> dict:
    """
    Return a real-time coaching tip via a self-critique agent loop.
    The secret is used only to run guardrails — it is never placed in the prompt.

    Pipeline: draft → critique → (regenerate if BAD) → guardrail → final.

    Returns a dict:
        {
            "final": str,        # tip text shown to the player
            "trace": list[dict], # ordered reasoning steps for the UI expander
        }
    """
    guess_count = len(guess_log)
    context = _retrieve(difficulty, guess_count, attempts_left)
    low, high = {"Easy": (1, 20), "Normal": (1, 50), "Hard": (1, 100)}[difficulty]

    base_prompt = sanitize_prompt(
        f"You are a concise number guessing game coach. Give ONE tip in 2-3 sentences max.\n\n"
        f"STRATEGY REFERENCE:\n{context}\n\n"
        f"GAME STATE:\n"
        f"- Difficulty: {difficulty} (range {low}–{high}, {ATTEMPT_LIMITS[difficulty]} attempts total)\n"
        f"- Attempts left: {attempts_left}\n"
        f"- Guess history:\n{_format_guess_log(guess_log)}\n\n"
        f"Give one specific, actionable tip based on what the player just did. "
        f"Do NOT guess or suggest specific numbers. Focus on strategy only.",
        secret,
    )

    trace = []

    try:
        draft = _draft_tip(base_prompt)
        trace.append({"step": "draft", "content": draft})

        ok, reason = _critique_tip(draft, difficulty, guess_count, secret)
        trace.append({"step": "critique", "content": "OK" if ok else f"BAD: {reason}"})

        if not ok:
            regen_prompt = sanitize_prompt(
                base_prompt
                + f"\n\nIMPORTANT: A reviewer flagged your previous attempt because: {reason}. "
                f"Rewrite the tip without that issue. Strategy only — no specific numbers.",
                secret,
            )
            current = _draft_tip(regen_prompt)
            trace.append({"step": "regenerate", "content": current})
        else:
            current = draft

        safe, result = validate_response(current, secret)
        trace.append({"step": "guardrail", "content": "passed" if safe else "blocked — substituted fallback"})
        trace.append({"step": "final", "content": result})
        return {"final": result, "trace": trace}

    except Exception:
        logger.exception("Mid-game tip generation failed (Ollama unavailable or model error); returning FALLBACK_TIP")
        trace.append({"step": "error", "content": "Ollama call failed; using static fallback"})
        trace.append({"step": "final", "content": FALLBACK_TIP})
        return {"final": FALLBACK_TIP, "trace": trace}


def get_postgame_review(guess_log: list, secret: int, difficulty: str, won: bool) -> str:
    """
    Return a post-game coaching breakdown after the game ends.
    The secret is revealed in the review since the game is over.
    """
    attempt_limit = ATTEMPT_LIMITS[difficulty]
    outcome = "won" if won else "lost"
    low, high = {"Easy": (1, 20), "Normal": (1, 50), "Hard": (1, 100)}[difficulty]

    docs = "\n\n---\n\n".join([
        _load_doc("binary_search.txt"),
        _load_doc("common_mistakes.txt"),
    ])

    prompt = (
        f"You are a number guessing game coach. Write a post-game review in under 100 words.\n\n"
        f"STRATEGY REFERENCE:\n{docs}\n\n"
        f"GAME SUMMARY:\n"
        f"- Difficulty: {difficulty} (range {low}–{high}, {attempt_limit} attempts)\n"
        f"- Secret number: {secret}\n"
        f"- Outcome: Player {outcome} using {len(guess_log)} of {attempt_limit} attempts\n"
        f"- Guess history:\n{_format_guess_log(guess_log)}\n\n"
        f"Cover exactly three things:\n"
        f"1. What the player did well or where they went wrong.\n"
        f"2. What the optimal sequence would have looked like.\n"
        f"3. One concrete thing to do differently next time."
    )

    try:
        response = ollama.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
        return response["message"]["content"].strip()
    except Exception:
        logger.exception("Post-game review generation failed (Ollama unavailable or model error); returning FALLBACK_REVIEW")
        return FALLBACK_REVIEW

import os
import ollama
from guardrails import sanitize_prompt, validate_response, FALLBACK_TIP, FALLBACK_REVIEW

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


def get_mid_game_tip(guess_log: list, difficulty: str, attempts_left: int, secret: int) -> str:
    """
    Return a real-time coaching tip based on the player's current game state.
    The secret is used only to run guardrails — it is never placed in the prompt.
    """
    guess_count = len(guess_log)
    context = _retrieve(difficulty, guess_count, attempts_left)
    low, high = {"Easy": (1, 20), "Normal": (1, 50), "Hard": (1, 100)}[difficulty]

    prompt = sanitize_prompt(
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

    try:
        response = ollama.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
        raw = response["message"]["content"].strip()
        safe, result = validate_response(raw, secret)
        return result
    except Exception:
        return FALLBACK_TIP


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
        return FALLBACK_REVIEW

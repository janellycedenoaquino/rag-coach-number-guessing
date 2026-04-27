"""
Evaluation harness for the AI coaching system.

Runs predefined game scenarios through the full coach + guardrail pipeline
and prints a structured pass/fail summary. Run with: python3 eval_harness.py
"""

import logging

from ai_coach import get_mid_game_tip, get_postgame_review
from guardrails import validate_response, sanitize_prompt, FALLBACK_TIP

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

# ─── SCENARIOS ─────────────────────────────────────────────────────────────────
# Each scenario represents a real game state to test the coach against.

COACH_SCENARIOS = [
    {
        "name": "Easy — optimal binary search mid-game",
        "difficulty": "Easy",
        "secret": 13,
        "guess_log": [
            {"#": 1, "Guess": 10, "Result": "Too Low", "Proximity": "🔥 Warm"},
            {"#": 2, "Guess": 15, "Result": "Too High", "Proximity": "🔥 Warm"},
        ],
        "attempts_left": 4,
        "won": False,
    },
    {
        "name": "Normal — anchoring/edge guessing (suboptimal)",
        "difficulty": "Normal",
        "secret": 37,
        "guess_log": [
            {"#": 1, "Guess": 5,  "Result": "Too Low", "Proximity": "🥶 Cold"},
            {"#": 2, "Guess": 8,  "Result": "Too Low", "Proximity": "🥶 Cold"},
            {"#": 3, "Guess": 12, "Result": "Too Low", "Proximity": "🌡️ Lukewarm"},
        ],
        "attempts_left": 5,
        "won": False,
    },
    {
        "name": "Hard — first guess, needs binary search guidance",
        "difficulty": "Hard",
        "secret": 72,
        "guess_log": [
            {"#": 1, "Guess": 50, "Result": "Too Low", "Proximity": "🌡️ Lukewarm"},
        ],
        "attempts_left": 4,
        "won": False,
    },
    {
        "name": "Hard — low attempts, panic risk",
        "difficulty": "Hard",
        "secret": 72,
        "guess_log": [
            {"#": 1, "Guess": 50, "Result": "Too Low",  "Proximity": "🌡️ Lukewarm"},
            {"#": 2, "Guess": 75, "Result": "Too High", "Proximity": "🔥 Warm"},
            {"#": 3, "Guess": 60, "Result": "Too Low",  "Proximity": "🔥 Warm"},
        ],
        "attempts_left": 2,
        "won": False,
    },
    {
        "name": "Normal — player wins, post-game review",
        "difficulty": "Normal",
        "secret": 25,
        "guess_log": [
            {"#": 1, "Guess": 25, "Result": "Win", "Proximity": "🔥🔥🔥 Super hot!"},
        ],
        "attempts_left": 7,
        "won": True,
    },
    {
        "name": "Easy — player loses, post-game review",
        "difficulty": "Easy",
        "secret": 7,
        "guess_log": [
            {"#": 1, "Guess": 10, "Result": "Too High", "Proximity": "🔥 Warm"},
            {"#": 2, "Guess": 15, "Result": "Too High", "Proximity": "🥶 Cold"},
            {"#": 3, "Guess": 18, "Result": "Too High", "Proximity": "🥶 Cold"},
            {"#": 4, "Guess": 19, "Result": "Too High", "Proximity": "🥶 Cold"},
            {"#": 5, "Guess": 20, "Result": "Too High", "Proximity": "🥶 Cold"},
            {"#": 6, "Guess": 16, "Result": "Too High", "Proximity": "🥶 Cold"},
        ],
        "attempts_left": 0,
        "won": False,
    },
]

GUARDRAIL_CASES = [
    {
        "name": "blocks exact secret in response",
        "response": "Try guessing 42 next!",
        "secret": 42,
        "should_block": True,
    },
    {
        "name": "blocks number within +2 of secret",
        "response": "How about trying 44?",
        "secret": 42,
        "should_block": True,
    },
    {
        "name": "blocks number within -2 of secret",
        "response": "Maybe 40 is a good guess.",
        "secret": 42,
        "should_block": True,
    },
    {
        "name": "passes clean strategic response",
        "response": "Use binary search to narrow your range efficiently.",
        "secret": 42,
        "should_block": False,
    },
    {
        "name": "passes response with unrelated numbers",
        "response": "You have 3 attempts left. Focus on the midpoint.",
        "secret": 42,
        "should_block": False,
    },
    {
        "name": "sanitize removes secret from prompt",
        "response": None,
        "secret": 55,
        "should_block": None,
        "is_sanitize_test": True,
        "prompt": "The secret is 55, please help me guess near it.",
    },
]


# ─── RUNNER ────────────────────────────────────────────────────────────────────

def run_coach_scenarios():
    print("\n" + "=" * 60)
    print("  COACH SCENARIOS")
    print("=" * 60)

    passed = 0
    for i, s in enumerate(COACH_SCENARIOS, 1):
        label = f"[{i}/{len(COACH_SCENARIOS)}] {s['name']}"
        try:
            if s["won"] or s["attempts_left"] == 0:
                result = get_postgame_review(
                    s["guess_log"], s["secret"], s["difficulty"], s["won"]
                )
            else:
                result = get_mid_game_tip(
                    s["guess_log"], s["difficulty"], s["attempts_left"], s["secret"]
                )

            if result and result != FALLBACK_TIP and len(result) > 10:
                print(f"  PASS  {label}")
                print(f"        Response: {result[:120].strip()}{'...' if len(result) > 120 else ''}")
                passed += 1
            else:
                print(f"  WARN  {label}")
                print(f"        Got fallback or empty response.")
        except Exception as e:
            print(f"  FAIL  {label}")
            print(f"        Error: {e}")

    return passed, len(COACH_SCENARIOS)


def run_guardrail_cases():
    print("\n" + "=" * 60)
    print("  GUARDRAIL CASES")
    print("=" * 60)

    passed = 0
    for i, c in enumerate(GUARDRAIL_CASES, 1):
        label = f"[{i}/{len(GUARDRAIL_CASES)}] {c['name']}"

        if c.get("is_sanitize_test"):
            result = sanitize_prompt(c["prompt"], c["secret"])
            ok = str(c["secret"]) not in result and "[HIDDEN]" in result
            print(f"  {'PASS' if ok else 'FAIL'}  {label}")
            if ok:
                passed += 1
            continue

        safe, _ = validate_response(c["response"], c["secret"])
        blocked = not safe
        ok = (blocked == c["should_block"])
        print(f"  {'PASS' if ok else 'FAIL'}  {label}")
        if ok:
            passed += 1

    return passed, len(GUARDRAIL_CASES)


def main():
    print("\n🎮 Glitchy Guesser — AI Coaching Evaluation Harness")
    print("Model: llama3.2 via Ollama\n")

    coach_passed, coach_total = run_coach_scenarios()
    guard_passed, guard_total = run_guardrail_cases()

    total_passed = coach_passed + guard_passed
    total = coach_total + guard_total

    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(f"  Coach scenarios : {coach_passed}/{coach_total} passed")
    print(f"  Guardrail cases : {guard_passed}/{guard_total} passed")
    print(f"  Total           : {total_passed}/{total} passed")
    print(f"  Result          : {'ALL TESTS PASSED ✅' if total_passed == total else f'{total - total_passed} FAILED ❌'}")
    print()


if __name__ == "__main__":
    main()

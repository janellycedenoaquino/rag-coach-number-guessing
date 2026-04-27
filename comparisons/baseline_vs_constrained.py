"""
Baseline-vs-Constrained A/B comparison.

Runs the same set of mid-game scenarios through two prompt variants:
  - BASELINE: minimal generic prompt, no strategy doc, no role, no format constraints.
  - CONSTRAINED: production prompt with retrieval context + role + length cap + no-numbers rule.

Purpose: demonstrate that the prompt specialization measurably changes coach behavior.
This satisfies the "Fine-Tuning or Specialization" stretch (constrained tone/style with
output measurably different from baseline).

Both variants use a single Ollama call (no agent critique loop) so the comparison
isolates the effect of the prompt itself.

Run with: python3 comparisons/baseline_vs_constrained.py
"""

import logging
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ollama  # noqa: E402

from ai_coach import (  # noqa: E402
    MODEL,
    _build_baseline_prompt,
    _build_constrained_prompt,
)

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

SCENARIOS = [
    {
        "name": "Easy — mid-game, ranges already eliminated",
        "difficulty": "Easy",
        "secret": 13,
        "guess_log": [
            {"#": 1, "Guess": 10, "Result": "Too Low", "Proximity": "🔥 Warm"},
            {"#": 2, "Guess": 15, "Result": "Too High", "Proximity": "🔥 Warm"},
        ],
        "attempts_left": 4,
    },
    {
        "name": "Normal — anchoring near low edge",
        "difficulty": "Normal",
        "secret": 37,
        "guess_log": [
            {"#": 1, "Guess": 5, "Result": "Too Low", "Proximity": "🥶 Cold"},
            {"#": 2, "Guess": 8, "Result": "Too Low", "Proximity": "🥶 Cold"},
            {"#": 3, "Guess": 12, "Result": "Too Low", "Proximity": "🌡️ Lukewarm"},
        ],
        "attempts_left": 5,
    },
    {
        "name": "Hard — first guess",
        "difficulty": "Hard",
        "secret": 72,
        "guess_log": [
            {"#": 1, "Guess": 50, "Result": "Too Low", "Proximity": "🌡️ Lukewarm"},
        ],
        "attempts_left": 4,
    },
    {
        "name": "Hard — low attempts, panic risk",
        "difficulty": "Hard",
        "secret": 72,
        "guess_log": [
            {"#": 1, "Guess": 50, "Result": "Too Low", "Proximity": "🌡️ Lukewarm"},
            {"#": 2, "Guess": 75, "Result": "Too High", "Proximity": "🔥 Warm"},
            {"#": 3, "Guess": 60, "Result": "Too Low", "Proximity": "🔥 Warm"},
        ],
        "attempts_left": 2,
    },
]


NUMBER_RE = re.compile(r"\b\d+\b")


def one_shot(prompt: str) -> str:
    response = ollama.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"].strip()


def metrics_for(text: str, secret: int):
    words = text.split()
    numbers = [int(n) for n in NUMBER_RE.findall(text)]
    near_secret = [n for n in numbers if abs(n - secret) <= 2]
    return {
        "word_count": len(words),
        "number_count": len(numbers),
        "near_secret_count": len(near_secret),
    }


def main():
    print("\n" + "=" * 70)
    print("  BASELINE vs CONSTRAINED — Prompt Specialization A/B")
    print("=" * 70)
    print(f"  Model: {MODEL} via Ollama")
    print(f"  Scenarios: {len(SCENARIOS)}\n")

    rows = []
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.md")

    for i, s in enumerate(SCENARIOS, 1):
        print(f"[{i}/{len(SCENARIOS)}] {s['name']}")

        baseline_prompt = _build_baseline_prompt(
            s["guess_log"], s["difficulty"], s["attempts_left"], s["secret"]
        )
        constrained_prompt = _build_constrained_prompt(
            s["guess_log"], s["difficulty"], s["attempts_left"], s["secret"]
        )

        baseline_out = one_shot(baseline_prompt)
        constrained_out = one_shot(constrained_prompt)

        b_metrics = metrics_for(baseline_out, s["secret"])
        c_metrics = metrics_for(constrained_out, s["secret"])

        print(f"  baseline:   {b_metrics['word_count']:3d} words, "
              f"{b_metrics['number_count']:2d} numbers, "
              f"{b_metrics['near_secret_count']} within ±2 of secret")
        print(f"  constrained: {c_metrics['word_count']:3d} words, "
              f"{c_metrics['number_count']:2d} numbers, "
              f"{c_metrics['near_secret_count']} within ±2 of secret\n")

        rows.append({
            "scenario": s["name"],
            "secret": s["secret"],
            "baseline_out": baseline_out,
            "constrained_out": constrained_out,
            "baseline_metrics": b_metrics,
            "constrained_metrics": c_metrics,
        })

    # Aggregate
    avg = lambda key, mode: sum(r[f"{mode}_metrics"][key] for r in rows) / len(rows)
    total = lambda key, mode: sum(r[f"{mode}_metrics"][key] for r in rows)

    print("=" * 70)
    print("  AGGREGATE")
    print("=" * 70)
    print(f"  Avg word count       — baseline: {avg('word_count', 'baseline'):.1f}  "
          f"constrained: {avg('word_count', 'constrained'):.1f}")
    print(f"  Total numbers cited  — baseline: {total('number_count', 'baseline')}  "
          f"constrained: {total('number_count', 'constrained')}")
    print(f"  Total ±2 of secret   — baseline: {total('near_secret_count', 'baseline')}  "
          f"constrained: {total('near_secret_count', 'constrained')}\n")

    # Write markdown report
    with open(output_path, "w") as f:
        f.write("# Baseline vs Constrained Prompt — A/B Results\n\n")
        f.write(f"_Model: `{MODEL}` via Ollama. {len(SCENARIOS)} scenarios, single Ollama "
                "call per variant (no agent loop), guardrails disabled in this script "
                "to capture raw model output._\n\n")
        f.write("## Aggregate metrics\n\n")
        f.write("| Metric | Baseline prompt | Constrained prompt |\n")
        f.write("|---|---|---|\n")
        f.write(f"| Avg word count per response | {avg('word_count', 'baseline'):.1f} | "
                f"{avg('word_count', 'constrained'):.1f} |\n")
        f.write(f"| Total numbers mentioned (across {len(SCENARIOS)} runs) | "
                f"{total('number_count', 'baseline')} | "
                f"{total('number_count', 'constrained')} |\n")
        f.write(f"| Numbers within ±2 of secret (would-be guardrail blocks) | "
                f"{total('near_secret_count', 'baseline')} | "
                f"{total('near_secret_count', 'constrained')} |\n\n")
        f.write("## Per-scenario outputs\n\n")
        for i, r in enumerate(rows, 1):
            f.write(f"### {i}. {r['scenario']} (secret = {r['secret']})\n\n")
            f.write("**Baseline output:**\n\n")
            f.write(f"> {r['baseline_out']}\n\n")
            f.write(f"_Metrics: {r['baseline_metrics']['word_count']} words, "
                    f"{r['baseline_metrics']['number_count']} numbers, "
                    f"{r['baseline_metrics']['near_secret_count']} within ±2 of secret._\n\n")
            f.write("**Constrained output:**\n\n")
            f.write(f"> {r['constrained_out']}\n\n")
            f.write(f"_Metrics: {r['constrained_metrics']['word_count']} words, "
                    f"{r['constrained_metrics']['number_count']} numbers, "
                    f"{r['constrained_metrics']['near_secret_count']} within ±2 of secret._\n\n")
            f.write("---\n\n")

    print(f"  Full report written to: {output_path}")


if __name__ == "__main__":
    main()

# Baseline vs Constrained Prompt — A/B Results

_Model: `llama3.2` via Ollama. 4 scenarios, single Ollama call per variant (no agent loop), guardrails disabled in this script to capture raw model output._

## Aggregate metrics

| Metric | Baseline prompt | Constrained prompt |
|---|---|---|
| Avg word count per response | 94.0 | 35.5 |
| Total numbers mentioned (across 4 runs) | 23 | 6 |
| Numbers within ±2 of secret (would-be guardrail blocks) | 3 | 1 |

## Per-scenario outputs

### 1. Easy — mid-game, ranges already eliminated (secret = 13)

**Baseline output:**

> It seems like the player is getting close, but still needs to narrow it down.

Since their previous guesses were too low and too high, I would suggest that the secret number might be in the middle of the range. 

My next guess would be: 13

This guess takes into account the fact that the player's previous guesses (10 and 15) were on either side of the "warm" zone, indicating that the secret number is likely to be around the midpoint.

Let's see how it goes!

_Metrics: 86 words, 3 numbers, 2 within ±2 of secret._

**Constrained output:**

> Since you got "Too High" and "🔥 Warm" after your last guesses, try to increase the range by a smaller increment than the 5-point difference between your previous attempts (15-10).

_Metrics: 30 words, 3 numbers, 1 within ±2 of secret._

---

### 2. Normal — anchoring near low edge (secret = 37)

**Baseline output:**

> It seems like our player is warming up slowly.

From the history, we can see that:

* Guesses 1 and 2 were too low, so the number is above 8.
* Guess 3 was lukewarm, which means it's getting closer to the target, but still a bit cold.

To improve the next guess, let's try to narrow down the range. Since we're above 8 and only lukewarm, I'd suggest guessing a number in the middle of the remaining range (9-50). A good starting point could be:

Guess 4: 25

This guess takes into account the player's slow progress and tries to find a sweet spot that's neither too high nor too low.

_Metrics: 112 words, 9 numbers, 0 within ±2 of secret._

**Constrained output:**

> Recalibrate after "Lukewarm" hint to focus your next guess on a narrower range, as the proximity hint might provide a tighter bound than pure binary search.

_Metrics: 26 words, 0 numbers, 0 within ±2 of secret._

---

### 3. Hard — first guess (secret = 72)

**Baseline output:**

> The player has had one lukewarm guess, which suggests that the target number is not too high or too low.

Considering this information, here's my next suggestion:

Guess 2: 67

This guess takes into account the fact that the previous guess (50) was too low, so I'm trying to narrow down the range by adding a moderate value. The resulting guess of 67 should provide more accurate feedback for the player.

What do you think? Should we proceed with Guess 3?

_Metrics: 81 words, 5 numbers, 0 within ±2 of secret._

**Constrained output:**

> Since your first guess was 50 and it was marked as "Lukewarm", you should immediately adjust your range to ±10 around your original guess of 50. This will help you utilize the proximity hint effectively and avoid wasting further attempts.

_Metrics: 40 words, 3 numbers, 0 within ±2 of secret._

---

### 4. Hard — low attempts, panic risk (secret = 72)

**Baseline output:**

> I can see you're getting closer, but still a bit off.

Let's analyze the situation:

- Your first guess of 50 was too low.
- Your second guess of 75 was too high.
- Your third guess of 60 is also too low.

Since your guesses are alternating between being too low and too high, it means that the secret number is likely to be higher than 50 but lower than 75.

Here's a suggested next step:

Guess: 72

This guess is in the middle of 70s, which should narrow down the range. Give it a try!

_Metrics: 97 words, 6 numbers, 1 within ±2 of secret._

**Constrained output:**

> Since you got a "Too Low" and "Too High" on your first two guesses, update your range immediately after each hint to reflect the new low and high bounds of your valid range. This will help you avoid making incorrect assumptions about the secret number's position.

_Metrics: 46 words, 0 numbers, 0 within ±2 of secret._

---


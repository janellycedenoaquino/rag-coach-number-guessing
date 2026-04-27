# Baseline vs Constrained Prompt — A/B Results

_Model: `llama3.2` via Ollama. 4 scenarios, single Ollama call per variant (no agent loop), guardrails disabled in this script to capture raw model output._

## Aggregate metrics

| Metric | Baseline prompt | Constrained prompt |
|---|---|---|
| Avg word count per response | 116.8 | 43.5 |
| Total numbers mentioned (across 4 runs) | 35 | 9 |
| Numbers within ±2 of secret (would-be guardrail blocks) | 4 | 2 |

## Per-scenario outputs

### 1. Easy — mid-game, ranges already eliminated (secret = 13)

**Baseline output:**

> Let's break down the hints:

* The secret number is between 1 and 20, so we're in a relatively small range.
* Guess 1 was 10, which is too low, indicating that our target number is higher than 10.
* Guess 2 was 15, which is also too high, but still warm, meaning the correct answer lies within the same "warm" zone as guess 1.

With these hints in mind, I would suggest that our next guess should be a number between 11 and 14. This range is centered around the midpoint of guess 1 and guess 2, which increases our chances of getting closer to the target number.

My next suggestion: Guess 3: 12

This number takes into account the "warm" hints from both previous guesses and tries to find a sweet spot that might bring us closer to the correct answer. What do you think?

_Metrics: 147 words, 14 numbers, 4 within ±2 of secret._

**Constrained output:**

> Since your last guess was close and received a "Too High" and "Warm" proximity hint, it's likely that the secret is very close to 15. Use this to focus your next guess around 15, rather than trying to bracket a wider range. This approach increases the chances of getting the correct answer with one of your remaining attempts.

_Metrics: 58 words, 2 numbers, 2 within ±2 of secret._

---

### 2. Normal — anchoring near low edge (secret = 37)

**Baseline output:**

> It looks like our player is getting closer, but still needs to narrow down the range.

Let's analyze the feedback:

- The first two guesses were too low (😊), so we know the number is higher than 5 and 8.
- The third guess was lukewarm (🌡️), which means it's close, but not quite there. This suggests that the number might be in the mid-to-high teens.

Considering this information, my next suggestion would be to try a number between 10 and 15. Specifically, I'd recommend guessing... **13**!

What do you think? Should we stick with 13 or take another approach?

_Metrics: 100 words, 6 numbers, 0 within ±2 of secret._

**Constrained output:**

> To avoid wasting attempts on a cold guess, immediately recalibrate to the midpoint after getting "🥶 Cold" with any hint that doesn't confirm your proximity guess was wrong (like 🌡️ Lukewarm).

_Metrics: 31 words, 0 numbers, 0 within ±2 of secret._

---

### 3. Hard — first guess (secret = 72)

**Baseline output:**

> Don't worry, I'm here to help!

For the second guess, we can try to narrow down the range a bit more. Since the player's first guess was 50 and it was "Lukewarm" (indicating that the secret number is higher than 50), our next guess should be slightly higher.

Let's aim for a mid-range number between 51 and 75. This should give us a better chance of getting closer to the secret number.

Guess 2: 67

How's this one?

_Metrics: 78 words, 6 numbers, 0 within ±2 of secret._

**Constrained output:**

> Since your guess of 50 was "Too Low", you should now make your next guess (Guess 2) exactly halfway between 1 and 100 to narrow down the remaining range, effectively starting a new binary search within that half.

_Metrics: 38 words, 4 numbers, 0 within ±2 of secret._

---

### 4. Hard — low attempts, panic risk (secret = 72)

**Baseline output:**

> It's clear that the player is getting closer, but still has two attempts left.

Let's analyze their guesses:

* Guess 1 was too low, so we know the secret number must be higher than 50.
* Guess 2 was too high, so we know the secret number must be lower than 75.
* Guess 3 was too low again, which suggests that the player is getting stuck in a "lower bound" zone.

My strategy would be to try a guess in the middle of the remaining range. Let's aim for... **68**!

This guess takes into account:

* The fact that the number is higher than 50
* That it's lower than 75
* Trying to avoid repeating the same error as before (going too low again)

What do you think? Should we try 68 or adjust our strategy based on your feedback?

_Metrics: 142 words, 9 numbers, 0 within ±2 of secret._

**Constrained output:**

> Given your guess history, since you've received "Too High" and "Too Low" hints, it's essential to adjust your approach. Instead of continuing to bisect, you should tighten your range immediately after the warm hint by guessing a midpoint within ±10 around your previous guess (Guess 2: 75).

_Metrics: 47 words, 3 numbers, 0 within ±2 of secret._

---


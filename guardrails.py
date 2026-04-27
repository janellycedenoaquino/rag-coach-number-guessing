import logging
import re

logger = logging.getLogger(__name__)

FALLBACK_TIP = "Think about what range you've eliminated so far and aim for the midpoint."
FALLBACK_REVIEW = "Keep practicing — focus on using binary search from your very first guess."


def _extract_numbers(text: str) -> list:
    return [int(n) for n in re.findall(r'\b\d+\b', text)]


def sanitize_prompt(prompt: str, secret: int) -> str:
    """Replace any mention of the secret number in the prompt with [HIDDEN]."""
    return re.sub(rf'\b{secret}\b', '[HIDDEN]', prompt)


def validate_response(response: str, secret: int) -> tuple:
    """
    Check that the AI response does not reveal the secret or any number within ±2 of it.

    Returns (True, response) if safe, or (False, fallback_message) if the secret is leaked.
    """
    numbers = _extract_numbers(response)
    for n in numbers:
        if abs(n - secret) <= 2:
            logger.warning(
                "Guardrail blocked AI response: contained %d, within ±2 of secret; substituted fallback",
                n,
            )
            return False, FALLBACK_TIP
    return True, response


def safe_review(review: str, secret: int) -> str:
    """
    Variant of validate_response for post-game reviews where the secret CAN be mentioned
    in the recap but the fallback should be review-specific.

    Post-game it is fine to reveal the secret — we only block during active play.
    This function is a passthrough kept here for future use if rules change.
    """
    return review

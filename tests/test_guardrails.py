from guardrails import sanitize_prompt, validate_response, FALLBACK_TIP


# --- validate_response ---

def test_validate_blocks_exact_secret():
    safe, _ = validate_response("Try guessing 42!", 42)
    assert safe is False

def test_validate_blocks_two_above():
    safe, _ = validate_response("Maybe try 44?", 42)
    assert safe is False

def test_validate_blocks_one_above():
    safe, _ = validate_response("How about 43?", 42)
    assert safe is False

def test_validate_blocks_two_below():
    safe, _ = validate_response("How about 40?", 42)
    assert safe is False

def test_validate_blocks_one_below():
    safe, _ = validate_response("Try 41 next.", 42)
    assert safe is False

def test_validate_passes_clean_response():
    text = "Use binary search to narrow your range down efficiently."
    safe, result = validate_response(text, 42)
    assert safe is True
    assert result == text

def test_validate_returns_fallback_message_on_block():
    safe, result = validate_response("The answer is 42!", 42)
    assert safe is False
    assert result == FALLBACK_TIP

def test_validate_number_just_outside_window_passes():
    # 47 is 5 away from 42 — should be allowed
    safe, _ = validate_response("Try somewhere around 47.", 42)
    assert safe is True

def test_validate_empty_response_passes():
    safe, result = validate_response("", 42)
    assert safe is True
    assert result == ""


# --- sanitize_prompt ---

def test_sanitize_removes_secret():
    result = sanitize_prompt("The secret is 42, guess near it.", 42)
    assert "42" not in result
    assert "[HIDDEN]" in result

def test_sanitize_leaves_other_numbers_intact():
    result = sanitize_prompt("You have 3 attempts left. Range is 1 to 100.", 42)
    assert "3" in result
    assert "1" in result
    assert "100" in result

def test_sanitize_no_secret_present_is_unchanged():
    prompt = "Use binary search strategy."
    assert sanitize_prompt(prompt, 42) == prompt

def test_sanitize_replaces_all_occurrences():
    result = sanitize_prompt("42 is the secret. Avoid guessing 42.", 42)
    assert "42" not in result
    assert result.count("[HIDDEN]") == 2

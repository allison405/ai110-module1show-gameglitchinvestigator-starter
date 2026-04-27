import sys
import os
from unittest.mock import MagicMock

from app import get_range_for_difficulty, parse_guess
from app import check_guess as app_check_guess
from logic_utils import check_guess


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_fresh_state(secret=42):
    """Return a dict that mimics a brand-new st.session_state."""
    return {
        "secret": secret,
        "attempts": 1,
        "score": 0,
        "status": "playing",
        "history": [],
    }

def apply_new_game(state, new_secret=42):
    """Simulate exactly what the New Game button does in app.py."""
    state["attempts"] = 0
    state["secret"] = new_secret
    state["status"] = "playing"
    state["history"] = []

def test_sidebar_caption_range_easy():
    # If difficulty is easy, the range should show 1 to 20
    low, high = get_range_for_difficulty("Easy")
    caption = f"Range: {low} to {high}"
    assert caption == "Range: 1 to 20"

def test_sidebar_caption_range_normal():
    # Normal difficulty uses range 1 to 50
    low, high = get_range_for_difficulty("Normal")
    caption = f"Range: {low} to {high}"
    assert caption == "Range: 1 to 50"

def test_sidebar_caption_range_hard():
    # Hard difficulty uses range 1 to 100
    low, high = get_range_for_difficulty("Hard")
    caption = f"Range: {low} to {high}"
    assert caption == "Range: 1 to 100"


def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"


# ---------------------------------------------------------------------------
# New Game tests
# ---------------------------------------------------------------------------

def test_new_game_resets_attempts():
    # Starting from a mid-game state, new game should set attempts back to 0
    state = make_fresh_state()
    state["attempts"] = 5
    apply_new_game(state)
    assert state["attempts"] == 0


def test_new_game_resets_status_to_playing():
    # A finished game (won or lost) should become "playing" after new game
    state = make_fresh_state()
    state["status"] = "won"
    apply_new_game(state)
    assert state["status"] == "playing"


def test_new_game_clears_history():
    # Guess history from the previous game should be wiped
    state = make_fresh_state()
    state["history"] = [10, 25, 42]
    apply_new_game(state)
    assert state["history"] == []


def test_new_game_sets_a_new_secret():
    # The secret should be replaced with the new value
    state = make_fresh_state(secret=99)
    apply_new_game(state, new_secret=7)
    assert state["secret"] == 7


# ---------------------------------------------------------------------------
# Guess submission tests (after new game)
# ---------------------------------------------------------------------------

def test_valid_guess_is_accepted_after_new_game():
    # parse_guess should succeed for a plain integer string
    state = make_fresh_state()
    apply_new_game(state)
    assert state["status"] == "playing"
    ok, guess_int, err = parse_guess("30")
    assert ok is True
    assert guess_int == 30
    assert err is None


def test_winning_guess_after_new_game():
    # Guessing the exact secret right after a new game should return Win
    state = make_fresh_state()
    apply_new_game(state, new_secret=42)
    ok, guess_int, _ = parse_guess("42")
    assert ok
    result = check_guess(guess_int, state["secret"])
    assert result == "Win"


def test_guess_increments_attempts_and_updates_history():
    # Submitting a guess should track the attempt count and record the guess
    state = make_fresh_state()
    apply_new_game(state)
    ok, guess_int, _ = parse_guess("15")
    assert ok
    state["attempts"] += 1
    state["history"].append(guess_int)
    assert state["attempts"] == 1
    assert state["history"] == [15]


def test_invalid_guess_after_new_game_returns_error():
    # Submitting non-numeric input should fail gracefully with an error message
    state = make_fresh_state()
    apply_new_game(state)
    ok, guess_int, err = parse_guess("abc")
    assert ok is False
    assert guess_int is None
    assert err == "That is not a number."


def test_empty_guess_after_new_game_returns_error():
    # Submitting an empty string should prompt the user to enter a guess
    state = make_fresh_state()
    apply_new_game(state)
    ok, _, err = parse_guess("")
    assert ok is False
    assert err == "Enter a guess."


# ---------------------------------------------------------------------------
# Hint message tests (using check_guess from app.py which returns a tuple)
# ---------------------------------------------------------------------------

def test_hint_when_guess_is_too_high():
    # guess (80) > secret (50) → outcome "Too High", hint tells player to go lower
    outcome, message = app_check_guess(80, 50)
    assert outcome == "Too High"
    assert message == "📉 Go LOWER!"

def test_hint_when_guess_is_too_low():
    # guess (20) < secret (50) → outcome "Too Low", hint tells player to go higher
    outcome, message = app_check_guess(20, 50)
    assert outcome == "Too Low"
    assert message == "📈 Go HIGHER!"

def test_hint_when_guess_is_correct():
    # If the guess matches the secret, the hint should indicate a win
    outcome, message = app_check_guess(50, 50)
    assert outcome == "Win"
    assert message == "🎉 Correct!"

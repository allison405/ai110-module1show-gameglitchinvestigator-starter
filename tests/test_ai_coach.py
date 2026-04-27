import random
import pytest
from ai_coach import algorithmic_suggestion, narrow_range, calc_confidence


# ── narrow_range ──────────────────────────────────────────────────────────────

def test_narrow_range_no_history():
    assert narrow_range(1, 100, []) == (1, 100)


def test_narrow_range_too_low_raises_lower_bound():
    nl, nh = narrow_range(1, 100, [{"guess": 50, "outcome": "Too Low"}])
    assert nl == 51
    assert nh == 100


def test_narrow_range_too_high_lowers_upper_bound():
    nl, nh = narrow_range(1, 100, [{"guess": 50, "outcome": "Too High"}])
    assert nl == 1
    assert nh == 49


def test_narrow_range_multiple_guesses():
    history = [
        {"guess": 50, "outcome": "Too Low"},
        {"guess": 75, "outcome": "Too High"},
    ]
    nl, nh = narrow_range(1, 100, history)
    assert nl == 51
    assert nh == 74


# ── calc_confidence ───────────────────────────────────────────────────────────

def test_confidence_full_range_is_zero():
    assert calc_confidence(1, 100, 1, 100) == 0.0


def test_confidence_half_range_is_near_half():
    c = calc_confidence(1, 100, 51, 100)
    assert 0.49 < c < 0.51


def test_confidence_is_between_zero_and_one():
    for nl in range(1, 100, 10):
        for nh in range(nl, 101, 10):
            c = calc_confidence(1, 100, nl, nh)
            assert 0.0 <= c <= 1.0


# ── algorithmic_suggestion ────────────────────────────────────────────────────

def test_first_guess_is_midpoint():
    result = algorithmic_suggestion(1, 100, [])
    assert result["success"]
    assert result["suggested_guess"] == 50


def test_confidence_starts_at_zero():
    result = algorithmic_suggestion(1, 100, [])
    assert result["confidence"] == 0.0


def test_confidence_increases_with_guesses():
    r0 = algorithmic_suggestion(1, 100, [])
    r1 = algorithmic_suggestion(1, 100, [{"guess": 50, "outcome": "Too Low"}])
    assert r1["confidence"] > r0["confidence"]


def test_suggestion_always_within_narrowed_range():
    random.seed(42)
    history = []
    for _ in range(8):
        result = algorithmic_suggestion(1, 100, history)
        nl, nh = result["narrowed_range"]
        g = result["suggested_guess"]
        assert nl <= g <= nh, f"Guess {g} outside [{nl}, {nh}]"
        outcome = random.choice(["Too Low", "Too High"])
        history.append({"guess": g, "outcome": outcome})


def test_source_label_is_algorithmic():
    result = algorithmic_suggestion(1, 100, [])
    assert result["source"] == "Algorithmic"


def test_easy_mode_range():
    result = algorithmic_suggestion(1, 20, [])
    assert result["suggested_guess"] == 10


def test_hard_mode_range():
    result = algorithmic_suggestion(1, 50, [])
    assert result["suggested_guess"] == 25

import os
import json
import re
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Gemini is an optional enhancement — import errors are handled gracefully
try:
    from google import genai as _genai
    _gemini_client = _genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))
    _GEMINI_AVAILABLE = True
except Exception:
    _GEMINI_AVAILABLE = False

# Model names tried in order when GEMINI_MODEL is not set in .env
_CANDIDATE_MODELS = [
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-pro",
]


# ── Pure helper functions (also used by tests) ────────────────────────────────

def calc_confidence(low: int, high: int, narrowed_low: int, narrowed_high: int) -> float:
    """Return fraction of the original range that has been eliminated (0.0–1.0)."""
    total_range = high - low + 1
    remaining = max(1, narrowed_high - narrowed_low + 1)
    return round(1.0 - (remaining / total_range), 2)


def narrow_range(low: int, high: int, guess_history: list) -> tuple:
    """Plan step: derive the tightest valid range from guess history.
    Falls back to the full range if contradictory hints produce an impossible range."""
    narrowed_low = low
    narrowed_high = high
    for item in guess_history:
        g = item["guess"]
        outcome = item["outcome"]
        if outcome == "Too Low":
            narrowed_low = max(narrowed_low, g + 1)
        elif outcome == "Too High":
            narrowed_high = min(narrowed_high, g - 1)
    if narrowed_low > narrowed_high:
        return low, high
    return narrowed_low, narrowed_high


# ── Algorithmic coach (always available) ─────────────────────────────────────

def algorithmic_suggestion(low: int, high: int, guess_history: list) -> dict:
    """
    Agentic binary search coach.
      Plan  – narrow the valid range from guess history
      Act   – pick the midpoint as the optimal next guess
      Check – clamp to bounds and score confidence
    """
    # Plan
    narrowed_low, narrowed_high = narrow_range(low, high, guess_history)

    # Act
    suggested_guess = (narrowed_low + narrowed_high) // 2

    # Check: clamp in case of edge cases
    suggested_guess = max(narrowed_low, min(narrowed_high, suggested_guess))

    remaining = narrowed_high - narrowed_low + 1
    confidence = calc_confidence(low, high, narrowed_low, narrowed_high)
    reasoning = (
        f"Narrowed range to {narrowed_low}–{narrowed_high} ({remaining} values remain). "
        f"{suggested_guess} is the optimal midpoint split."
    )

    logger.info(
        "Algorithmic coach | narrowed=%d-%d guess=%d confidence=%.2f",
        narrowed_low, narrowed_high, suggested_guess, confidence,
    )
    return {
        "success": True,
        "suggested_guess": suggested_guess,
        "narrowed_range": (narrowed_low, narrowed_high),
        "reasoning": reasoning,
        "confidence": confidence,
        "source": "Algorithmic",
    }


# ── Gemini enhancement (optional) ────────────────────────────────────────────

def _try_gemini(
    difficulty: str,
    low: int,
    high: int,
    guess_history: list,
    attempt_limit: int,
    attempts_used: int,
) -> dict | None:
    """
    Ask Gemini for a coaching suggestion.
    Returns a result dict on success, or None if Gemini is unavailable.
    """
    if not _GEMINI_AVAILABLE:
        return None

    history_lines = [
        f"  Guess {item['guess']} -> {item['outcome']}" for item in guess_history
    ]
    history_str = "\n".join(history_lines) if history_lines else "  (no guesses yet)"

    prompt = f"""You are an AI coach for a number-guessing game. Help the player find the secret number.

Game state:
- Difficulty: {difficulty}
- Full range: {low}-{high}
- Attempts used: {attempts_used} of {attempt_limit}
- Guess history:
{history_str}

Follow this agentic process:
1. PLAN: Use each guess outcome to narrow the valid range:
   - "Too Low"  -> secret is ABOVE that guess (raise the lower bound)
   - "Too High" -> secret is BELOW that guess (lower the upper bound)
2. ACT: Pick the midpoint of the narrowed range as the suggested guess.
3. CHECK: Verify the suggested guess is inside the narrowed bounds.

Respond with ONLY a valid JSON object and nothing else:
{{
  "narrowed_low": <integer>,
  "narrowed_high": <integer>,
  "suggested_guess": <integer>,
  "reasoning": "<one sentence explaining your strategy>"
}}"""

    env_model = os.environ.get("GEMINI_MODEL", "").strip()
    candidates = [env_model] if env_model else _CANDIDATE_MODELS

    for model_name in candidates:
        try:
            response = _gemini_client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            text = response.text.strip()
            text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
            data = json.loads(text)

            narrowed_low = max(low, int(data["narrowed_low"]))
            narrowed_high = min(high, int(data["narrowed_high"]))
            guess = max(narrowed_low, min(narrowed_high, int(data["suggested_guess"])))
            confidence = calc_confidence(low, high, narrowed_low, narrowed_high)

            logger.info(
                "Gemini suggestion | model=%s guess=%d confidence=%.2f",
                model_name, guess, confidence,
            )
            return {
                "success": True,
                "suggested_guess": guess,
                "narrowed_range": (narrowed_low, narrowed_high),
                "reasoning": str(data["reasoning"]),
                "confidence": confidence,
                "source": f"Gemini ({model_name})",
            }

        except json.JSONDecodeError:
            logger.error("Could not parse Gemini JSON from %s — skipping.", model_name)
            return None

        except Exception as exc:
            err = str(exc)
            if "404" in err or "NOT_FOUND" in err or "429" in err or "RESOURCE_EXHAUSTED" in err:
                logger.warning("Model %s unavailable, trying next.", model_name)
                continue
            logger.error("Gemini API error with %s: %s", model_name, exc)
            return None

    logger.warning("All Gemini models unavailable — falling back to algorithmic coach.")
    return None


# ── Public entry point ────────────────────────────────────────────────────────

def get_ai_suggestion(
    difficulty: str,
    low: int,
    high: int,
    guess_history: list,  # [{"guess": int, "outcome": str}, ...]
    attempt_limit: int,
    attempts_used: int,
) -> dict:
    """
    Agentic AI coach: Plan -> Act -> Check, with confidence scoring.

    Tries Gemini for enhanced natural-language reasoning first.
    Always falls back to the algorithmic binary search coach so the
    feature works regardless of API availability.
    """
    logger.info(
        "AI coach called | difficulty=%s range=%d-%d attempts=%d/%d history_len=%d",
        difficulty, low, high, attempts_used, attempt_limit, len(guess_history),
    )

    gemini_result = _try_gemini(difficulty, low, high, guess_history, attempt_limit, attempts_used)
    if gemini_result:
        return gemini_result

    return algorithmic_suggestion(low, high, guess_history)

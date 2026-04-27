# Model Card — Game Glitch Investigator AI Coach

## Model Overview

| Field | Details |
|---|---|
| **Project** | Game Glitch Investigator — Agentic AI Coach |
| **Base Model** | Google Gemini (optional enhancement) + deterministic algorithmic coach (primary) |
| **Intended Use** | Real-time hint generation for a number guessing game |
| **Input** | Player's guess history and difficulty setting |
| **Output** | Recommended next guess, narrowed search range, and confidence score |

---

## AI Collaboration

### Tools Used

- **Claude Code (claude-sonnet)** — primary AI collaborator throughout the project for debugging, code structuring, and test generation.
- **Google Gemini API** — integrated as an optional live LLM to enhance coach responses with natural-language explanations.

### How AI Was Used as a Teammate

Claude Code was used in structuring the agentic coach (`ai_coach.py`), building AI compatability, assisting in writing the test suite, and debugging root causes that weren't from reading the code alone. Claude Code was also used to generate the mermaid map and assist with double checking the work done against the rubric to ensure requirements were fulfilled. 

The general workflow for each issue was:
1. Run the game and observe the broken behavior
2. Describe the behavior to Claude and ask for the root cause
3. Sanity-check Claude's explanation against the code manually
4. Implement the fix
5. Have Claude write tests for the fixed behavior
6. Re-run the game and tests to confirm

### Example of a Correct AI Suggestion

When the AI coach was returning suggestions in the wrong direction (recommending lower when the hint said "Go Higher"), I prompted Claude Code the issue, and Claude identified that the root cause was in how outcomes were recorded in history. The coach was reading outcome labels from `check_guess()`, which has an intentional bug that flips labels on even-numbered attempts. Claude's suggestion was to bypass `check_guess()` entirely for the coach's history and derive a `true_outcome` using direct integer comparison (`guess_int < st.session_state.secret`). This fixed the bug cleanly without touching the intentionally buggy game code. The fix was verified by running the game and confirming the coach's narrowed range always moved in the correct direction.

### Example of an Incorrect AI Suggestion

Claude repeatedly recommended `gemini-1.5-flash` as a reliable free-tier model for the Gemini integration. In practice, this model returned 404 errors across every API version tried (`v1`, `v1beta`, with and without the `-latest` suffix). Claude's suggestion was based on documentation that was accurate at one point but did not reflect the actual state of model availability for the API key in use. This required several debugging cycles before the architecture was redesigned to make the algorithmic coach the primary engine and treat Gemini as an optional enhancement. The lesson: AI suggestions about external API availability and versioning reflect training data, not live system state, and must be independently verified.

---

## Known Biases and Limitations

**Assumes binary search is optimal:** The algorithmic coach always recommends the midpoint of the remaining range. This is mathematically optimal for minimizing the worst-case number of guesses, but it cannot adapt to different player strategies, learning styles, or deliberate non-optimal play.

**No memory across games:** The coach has no persistent history. It cannot recognize patterns in a player's behavior across sessions or personalize explanations based on prior interaction.

**Conflicting feedback risk:** The original game has an intentional bug that flips hint labels on even-numbered attempts. The coach works around this with a direct integer comparison, but a player reading the game hints and coach output simultaneously on an even-numbered attempt will see conflicting information, which is confusing.

**Same answer for same state:** Given identical game state, the algorithmic coach always produces the same suggestion. It is deterministic and has no variance or adaptability.

**LLM availability:** When the Gemini API is unavailable or the key is missing, the coach falls back silently to the algorithmic engine. This is a feature, not a bug — but it means Gemini-enhanced responses are not guaranteed.

---

## Testing Results

**32 out of 32 tests pass** (`pytest tests/`).

| Test File | Tests | Coverage |
|---|---|---|
| `tests/test_game_logic.py` | 20 | Difficulty ranges, hint correctness, score updates, input parsing, new-game reset |
| `tests/test_ai_coach.py` | 12 | Range narrowing, confidence scoring (0.0–1.0 bounds), suggestion always within narrowed range, correct midpoints per difficulty |

### What the Tests Caught

Running `pytest` initially produced 3 failures that revealed real bugs:

1. **Difficulty range assertions** — Range tests for Normal and Hard had swapped values from an earlier version. Tests confirmed the swap and required updating the expected values.
2. **Impossible range edge case** — A randomized stress test (`test_suggestion_always_within_narrowed_range`) discovered that `narrow_range()` could produce a state where `low > high` when given a sequence of contradictory outcomes (which the buggy game can actually produce). The fix was a one-line fallback to the full range when a contradiction is detected.

### What Was Not Automated

The Gemini API path requires a live API key and cannot be unit tested in isolation. Its reliability is guaranteed structurally — any Gemini failure silently routes to the algorithmic coach, which is fully tested. The Gemini path was manually verified by testing with a valid key and confirming that natural-language responses appeared in the UI.

### Key Insight

The randomized stress test was the most valuable test in the suite. It generated game states that are logically contradictory — valid inputs, but produced by the buggy game — and found a failure that targeted tests alone would never have caught. Writing adversarial or randomized inputs is more effective than testing only expected scenarios.

---

## Ethical Considerations

**Low-risk use case:** This coach is a game hint tool with no sensitive data and no ability to take actions outside the game UI. The most realistic misuse is a player using the coach to eliminate all challenge from the game, which is acceptable since the coach is optional and clearly labeled.

**Disclosure principle:** The coach clearly labels its source ("Algorithmic" or "Gemini") and confidence score on every response. Players cannot mistake AI-assisted results for unassisted play. If this were a competitive or graded game, the coach would need to be hidden behind an explicit opt-in with a disclosure acknowledgment.

**Upstream data integrity:** This project demonstrated that an AI component's correctness depends entirely on the correctness of its inputs. The coach's range-narrowing logic was correct, but an upstream bug in the game's hint generation was silently corrupting the coach's behavior. AI systems do not exist in isolation — a broken data pipeline will produce broken AI outputs even when the AI logic is sound.

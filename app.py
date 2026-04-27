import random
import streamlit as st
from logic_utils import get_range_for_difficulty, parse_guess, update_score
from ai_coach import get_ai_suggestion


def check_guess(guess, secret):
    if guess == secret:
        return "Win", "🎉 Correct!"

    #FIX: Swapped the too low and too high results to match the correct logic using CLAUDE.
    try:
        if guess < secret:
            return "Too Low", "📈 Go HIGHER!"
        else:
            return "Too High", "📉 Go LOWER!"
    except TypeError:
        g = str(guess)
        if g == secret:
            return "Win", "🎉 Correct!"
        if g < secret:
            return "Too High", "📈 Go HIGHER!"
        return "Too Low", "📉 Go LOWER!"

st.set_page_config(page_title="Game Glitch", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 10,
    "Normal": 8,
    "Hard": 6,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    st.session_state.attempts = 1

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

if "coach_history" not in st.session_state:
    st.session_state.coach_history = []  # [{"guess": int, "outcome": str}]

if "last_coach_result" not in st.session_state:
    st.session_state.last_coach_result = None

st.subheader("Make a guess")

info_placeholder = st.empty()

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.coach_history = []
    st.session_state.last_coach_result = None
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.error(err)
    elif not (low <= guess_int <= high):
        st.error(f"Guess must be between {low} and {high}.")
    else:
        st.session_state.history.append(guess_int)

        if st.session_state.attempts % 2 == 0:
            secret = str(st.session_state.secret)
        else:
            secret = st.session_state.secret

        outcome, message = check_guess(guess_int, secret)

        if show_hint:
            st.warning(message)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        # Derive the true outcome for the coach using the actual numeric secret.
        # check_guess can return flipped labels on even attempts (string comparison bug),
        # so we compare directly to keep the coach's range narrowing correct.
        if guess_int == st.session_state.secret:
            true_outcome = "Win"
        elif guess_int < st.session_state.secret:
            true_outcome = "Too Low"
        else:
            true_outcome = "Too High"

        if outcome == "Win":
            st.session_state.coach_history.append({"guess": guess_int, "outcome": true_outcome})
            st.session_state.last_coach_result = None
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            st.session_state.coach_history.append({"guess": guess_int, "outcome": true_outcome})
            # Agentic AI Coach: plan -> act -> check
            with st.spinner("AI Coach is thinking..."):
                coach_result = get_ai_suggestion(
                    difficulty=difficulty,
                    low=low,
                    high=high,
                    guess_history=st.session_state.coach_history,
                    attempt_limit=attempt_limit,
                    attempts_used=st.session_state.attempts,
                )
            st.session_state.last_coach_result = coach_result

            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

attempts_left = max(0, attempt_limit - (st.session_state.attempts - 1))
info_placeholder.info(
    f"Guess a number between 1 and {high}. Attempts left: {attempts_left}"
)

# AI Coach panel — shown after each incorrect guess
if st.session_state.get("last_coach_result") and st.session_state.status == "playing":
    result = st.session_state.last_coach_result
    with st.container(border=True):
        st.markdown("### 🤖 AI Coach")
        if result["success"]:
            nl, nh = result["narrowed_range"]
            confidence = result.get("confidence", 0.0)
            source = result.get("source", "AI")
            st.markdown(
                f"**Source:** {source} | **Confidence:** {confidence:.0%}  \n"
                f"**Narrowed range:** {nl} – {nh}  \n"
                f"**Try next:** `{result['suggested_guess']}`  \n"
                f"**Strategy:** {result['reasoning']}"
            )
        else:
            st.warning(f"Coach unavailable: {result['error']}")

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")

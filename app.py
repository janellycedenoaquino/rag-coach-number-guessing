import random
import streamlit as st
from logic_utils import (
    check_guess, get_proximity_hint, get_range_for_difficulty,
    parse_guess, update_score, load_player_history, save_game_to_history,
)
from styles import MAIN_CSS, SECTION_LABEL_HTML, info_panel_html, debug_panel_html
from ai_coach import get_mid_game_tip, get_postgame_review

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")
st.html(MAIN_CSS)

# ─── SIDEBAR SETTINGS ──────────────────────────────────────────────────────────
st.sidebar.markdown("## ⚙️ SETTINGS!")
st.sidebar.markdown(
    '<p class="config-label" style="font-family:\'Oswald\',sans-serif;font-size:11px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#9b2cfa;margin:0;">DIFFICULTY LEVEL</p>',
    unsafe_allow_html=True,
)

difficulty = st.sidebar.selectbox(
    "",
    ["Easy", "Normal", "Hard"],
    index=1,
    label_visibility="collapsed",
)

attempt_limit_map = {"Easy": 6, "Normal": 8, "Hard": 5}
attempt_limit = attempt_limit_map[difficulty]
low, high = get_range_for_difficulty(difficulty)

st.sidebar.markdown(
    f'<span class="stat-pill">Range: {low}–{high}</span>'
    f'<span class="stat-pill">Attempts: {attempt_limit}</span>',
    unsafe_allow_html=True,
)

# ─── SIGN-IN ───────────────────────────────────────────────────────────────────
if "player_name" not in st.session_state:
    st.session_state.player_name = ""

if not st.session_state.player_name:
    st.html(SECTION_LABEL_HTML)
    st.markdown("### Welcome! Enter your name to start playing.")
    name_input = st.text_input("Your name:", placeholder="e.g. Janelly")
    if st.button("Start Playing 🚀", type="primary") and name_input.strip():
        st.session_state.player_name = name_input.strip()
        st.rerun()
    st.stop()

# ─── SIDEBAR HISTORY (shown after sign-in) ─────────────────────────────────────
st.sidebar.divider()
st.sidebar.markdown(f"### 👤 {st.session_state.player_name}")

if st.sidebar.button("Sign Out", type="secondary"):
    st.session_state.clear()
    st.rerun()

past_games = load_player_history(st.session_state.player_name)
if past_games:
    st.sidebar.markdown("**📖 Game History**")
    for game in past_games:
        icon = "✅" if game["won"] else "❌"
        label = f"{icon} {game['difficulty']} · {game['date']}"
        with st.sidebar.expander(label):
            st.markdown(
                f"**Score:** {game['score']} &nbsp;|&nbsp; "
                f"**Attempts:** {game['attempts']}/{attempt_limit_map[game['difficulty']]}"
            )
            st.markdown(f"**Secret was:** {game['secret']}")
            if game.get("coach_review"):
                st.markdown("**🧠 Coach's Review:**")
                st.info(game["coach_review"])
else:
    st.sidebar.caption("No games yet — play your first game!")

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
if "difficulty" not in st.session_state:
    st.session_state.difficulty = difficulty

if st.session_state.difficulty != difficulty:
    st.session_state.difficulty = difficulty
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.guess_log = []
    st.session_state.history_saved = False
    st.session_state.coach_tip = ""
    st.session_state.coach_review = ""

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)
if "attempts" not in st.session_state:
    st.session_state.attempts = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "status" not in st.session_state:
    st.session_state.status = "playing"
if "history" not in st.session_state:
    st.session_state.history = []
if "history_saved" not in st.session_state:
    st.session_state.history_saved = False
if "guess_log" not in st.session_state:
    st.session_state.guess_log = []
if "coach_tip" not in st.session_state:
    st.session_state.coach_tip = ""
if "coach_review" not in st.session_state:
    st.session_state.coach_review = ""

# ─── MAIN UI ───────────────────────────────────────────────────────────────────
st.html(SECTION_LABEL_HTML)

info_placeholder = st.empty()
debug_placeholder = st.empty()

st.markdown(
    '<p style="font-family: Impact, \'Arial Narrow\', sans-serif; font-size: 24px; font-weight: 900; letter-spacing: 2px; color: #1a0a1e; text-transform: uppercase; margin: 0 0 4px 0; line-height: 1.2;">ENTER YOUR GUESS:</p>',
    unsafe_allow_html=True,
)

raw_guess = st.text_input(
    "",
    key=f"guess_input_{difficulty}",
    placeholder="???",
    label_visibility="collapsed",
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀", type="primary")
with col2:
    new_game = st.button("New Game 🔁", type="secondary")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.guess_log = []
    st.session_state.history_saved = False
    st.session_state.coach_tip = ""
    st.session_state.coach_review = ""
    st.success("New game started.")
    st.rerun()

# ─── GAME OVER ─────────────────────────────────────────────────────────────────
if st.session_state.status != "playing":
    won = st.session_state.status == "won"

    if won:
        st.success(
            f"You won! The secret was {st.session_state.secret}. "
            f"Final score: {st.session_state.score}"
        )
    else:
        st.error("Game over. Start a new game to try again.")

    if not st.session_state.coach_review:
        with st.spinner("🧠 Coach is reviewing your game..."):
            st.session_state.coach_review = get_postgame_review(
                st.session_state.guess_log,
                st.session_state.secret,
                difficulty,
                won=won,
            )
    st.info(f"🧠 **Coach's Review**\n\n{st.session_state.coach_review}")

    if not st.session_state.history_saved:
        save_game_to_history(
            st.session_state.player_name,
            {
                "difficulty": difficulty,
                "secret": st.session_state.secret,
                "guess_log": st.session_state.guess_log,
                "score": st.session_state.score,
                "attempts": st.session_state.attempts,
                "won": won,
                "coach_review": st.session_state.coach_review,
            },
        )
        st.session_state.history_saved = True
    st.caption("✅ Game saved to your history — check the sidebar to review it.")
    st.stop()

# ─── GUESS LOGIC ───────────────────────────────────────────────────────────────
if submit:
    ok, guess_int, err = parse_guess(raw_guess, difficulty)

    if not ok:
        st.error(err)
    else:
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        outcome, message = check_guess(guess_int, st.session_state.secret)
        proximity = get_proximity_hint(guess_int, st.session_state.secret)

        if show_hint:
            if outcome == "Too High":
                st.error(message)
            elif outcome == "Too Low":
                st.warning(message)
            st.caption(proximity)

        st.session_state.guess_log.append({
            "#": st.session_state.attempts,
            "Guess": guess_int,
            "Result": outcome,
            "Proximity": proximity,
        })

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.rerun()
        elif st.session_state.attempts >= attempt_limit:
            st.session_state.status = "lost"
            st.error(
                f"Out of attempts! "
                f"The secret was {st.session_state.secret}. "
                f"Score: {st.session_state.score}"
            )
            st.rerun()
        else:
            with st.spinner("🧠 Coach is thinking..."):
                st.session_state.coach_tip = get_mid_game_tip(
                    st.session_state.guess_log,
                    difficulty,
                    attempt_limit - st.session_state.attempts,
                    st.session_state.secret,
                )

# ─── PANELS ────────────────────────────────────────────────────────────────────
attempts_left = attempt_limit - st.session_state.attempts
info_placeholder.html(info_panel_html(low, high, attempts_left))

if st.session_state.guess_log:
    st.subheader("📋 Guess History")
    st.table(st.session_state.guess_log)

if st.session_state.coach_tip and st.session_state.status == "playing":
    st.info(f"🧠 **Coach's Tip**\n\n{st.session_state.coach_tip}")

debug_placeholder.html(debug_panel_html(
    st.session_state.secret,
    st.session_state.attempts,
    st.session_state.score,
    difficulty,
    st.session_state.history,
))

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")

MAIN_CSS = """
<style>
/* ─── ANIMATIONS ─── */
@keyframes wobble { 0%,100% { transform:rotate(-1.5deg); } 50% { transform:rotate(1.5deg); } }
@keyframes float   { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-6px); } }
@keyframes shake   { 0%,100% { transform:translateX(0); } 50% { transform:translateX(3px); } }
@keyframes pop     { 0% { transform:scale(0.93); opacity:0; } 100% { transform:scale(1); opacity:1; } }

/* ─── TOP RAINBOW BAR ─── */
[data-testid="stHeader"] {
    background: repeating-linear-gradient(
        90deg,
        #ff2d78 0px,  #ff2d78 24px,
        #c084fc 24px, #c084fc 48px,
        #ffe44d 48px, #ffe44d 72px,
        #a7f3d0 72px, #a7f3d0 96px
    ) !important;
    height: 6px !important;
}

/* ─── MAIN BACKGROUND ─── */
.stApp {
    background-color: #ede9fe !important;
    background-image: radial-gradient(circle, rgba(255,45,120,0.10) 1.5px, transparent 1.5px) !important;
    background-size: 18px 18px !important;
    font-family: 'Trebuchet MS', Arial, sans-serif !important;
}

/* ─── SIDEBAR ─── */
[data-testid="stSidebar"] {
    background: #ff2d78 !important;
    border-right: 5px solid #1a0a1e !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div {
    color: #1a0a1e !important;
    font-family: 'Arial Narrow', Arial, sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
}
/* Allow Streamlit's Material icon ligatures to render (expander chevron, etc.) */
[data-testid="stSidebar"] [data-testid="stIconMaterial"],
[data-testid="stSidebar"] span[class*="material-symbols"],
[data-testid="stSidebar"] span[class*="material-icons"] {
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    font-weight: normal !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
}
[data-testid="stSidebar"] p.config-label {
    color: #9b2cfa !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #ffe44d !important;
    font-family: Impact, 'Arial Narrow', sans-serif !important;
    letter-spacing: 3px !important;
    text-shadow: 3px 3px 0 #1a0a1e !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.4) !important;
    border-style: dashed !important;
}
/* ─── CONFIG BOX ─── */
[data-testid="stSidebar"] .st-key-settings_box {
    background: #fff9f0 !important;
    border: 4px solid #1a0a1e !important;
    box-shadow: 5px 5px 0 #1a0a1e !important;
    padding: 14px 14px 16px 14px !important;
    margin-bottom: 16px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    gap: 14px !important;
    text-align: center !important;
}
[data-testid="stSidebar"] .st-key-settings_box [data-testid="stElementContainer"],
[data-testid="stSidebar"] .st-key-settings_box [data-testid="element-container"] {
    width: 100% !important;
    text-align: center !important;
}
[data-testid="stSidebar"] .st-key-settings_box [data-testid="stElementContainer"],
[data-testid="stSidebar"] .st-key-settings_box [data-testid="element-container"] {
    margin: 0 !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] .st-key-settings_box [data-testid="stButtonGroup"] {
    background: transparent !important;
    overflow: visible !important;
    width: 100% !important;
    box-sizing: border-box !important;
}
/* Streamlit's segmented_control puts the actual buttons inside a [data-baseweb="button-group"] wrapper
   with column-gap:0 baked in — that's the one we have to override, not stButtonGroup itself. */
[data-testid="stSidebar"] .st-key-settings_box [data-testid="stButtonGroup"] [data-baseweb="button-group"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    column-gap: 8px !important;
    width: fit-content !important;
    max-width: 100% !important;
    margin: 0 auto !important;
    box-sizing: border-box !important;
}
[data-testid="stSidebar"] [data-testid="stButtonGroup"] [data-testid^="stBaseButton-segmented_control"] {
    background: #ffe44d !important;
    border: 2px solid #1a0a1e !important;
    border-radius: 0 !important;
    box-shadow: 2px 2px 0 #1a0a1e !important;
    font-family: Impact, 'Arial Narrow', sans-serif !important;
    font-size: 13px !important;
    letter-spacing: 1px !important;
    color: #1a0a1e !important;
    padding: 8px 4px !important;
    flex: 0 0 70px !important;
    width: 70px !important;
    max-width: none !important;
    min-height: 36px !important;
    height: auto !important;
    text-transform: uppercase !important;
    margin: 0 !important;
    overflow: visible !important;
    white-space: nowrap !important;
    text-overflow: clip !important;
}
[data-testid="stSidebar"] [data-testid="stButtonGroup"] [data-testid^="stBaseButton-segmented_control"] * {
    background: transparent !important;
    color: #1a0a1e !important;
    overflow: visible !important;
    text-overflow: clip !important;
    max-width: none !important;
}
[data-testid="stSidebar"] [data-testid="stButtonGroup"] [data-testid="stBaseButton-segmented_control"]:hover {
    background: #fff176 !important;
    transform: translate(-1px, -1px) !important;
    box-shadow: 3px 3px 0 #1a0a1e !important;
}
[data-testid="stSidebar"] [data-testid="stButtonGroup"] [data-testid="stBaseButton-segmented_controlActive"] {
    background: #ffc700 !important;
    box-shadow: inset 0 -5px 0 #ff2d78 !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"]:has(.stat-pill) {
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: visible !important;
}
/* ─── STAT PILLS ─── */
.stat-pill {
    display: inline-block;
    background: #ff2d78;
    color: #1a0a1e !important;
    font-family: 'Oswald', sans-serif !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    padding: 3px 10px;
    margin: 2px 2px 2px 0;
    letter-spacing: 1px;
    border: 2px solid #1a0a1e;
}

/* ─── TITLE ─── */
h1 {
    font-family: Impact, 'Arial Narrow', sans-serif !important;
    font-size: 52px !important;
    letter-spacing: 3px !important;
    color: #1a0a1e !important;
    text-shadow: 4px 4px 0 #ff2d78, 8px 8px 0 rgba(192,132,252,0.35) !important;
    animation: wobble 5s ease-in-out infinite !important;
    display: inline-block !important;
}

/* ─── SUBHEADERS ─── */
h2, h3 {
    font-family: Impact, 'Arial Narrow', sans-serif !important;
    letter-spacing: 3px !important;
    color: #1a0a1e !important;
    text-shadow: 3px 3px 0 #ff85b3 !important;
}

/* ─── INFO BOX ─── */
[data-testid="stNotification"],
div[data-baseweb="notification"] {
    background: #ff85b3 !important;
    border: 5px solid #1a0a1e !important;
    border-radius: 0 !important;
    box-shadow: 6px 6px 0 #1a0a1e !important;
    font-family: 'Arial Narrow', Arial, sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    color: #1a0a1e !important;
}

/* ─── TEXT INPUT ─── */
.stTextInput,
.stTextInput > div,
.stTextInput > div > div {
    min-height: 80px !important;
    height: auto !important;
    overflow: visible !important;
}
.stTextInput > div > div > input {
    background: white !important;
    border: 5px solid #1a0a1e !important;
    border-radius: 0 !important;
    box-shadow: 6px 6px 0 #1a0a1e !important;
    font-family: Impact, 'Arial Narrow', sans-serif !important;
    font-size: 36px !important;
    letter-spacing: 3px !important;
    padding: 20px 24px !important;
    height: 80px !important;
    line-height: 1.2 !important;
    color: #1a0a1e !important;
    outline: none !important;
    transition: all 0.12s !important;
}
.stTextInput > div > div > input::placeholder {
    color: #c8a8c0 !important;
}
.stTextInput > div > div > input:focus {
    background: #ffe44d !important;
    transform: translate(-2px, -2px) !important;
    box-shadow: 8px 8px 0 #1a0a1e !important;
}
.stTextInput label,
div[data-testid="stTextInput"] label,
div[data-testid="stTextInput"] > label {
    font-family: Impact, 'Arial Narrow', sans-serif !important;
    font-size: 24px !important;
    font-weight: 900 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: #1a0a1e !important;
}

/* ─── BUTTONS ─── */
.stButton > button {
    border: 4px solid #1a0a1e !important;
    border-radius: 0 !important;
    font-family: Impact, 'Arial Narrow', sans-serif !important;
    font-size: 20px !important;
    letter-spacing: 3px !important;
    box-shadow: 5px 5px 0 #1a0a1e !important;
    transition: all 0.1s !important;
    text-transform: uppercase !important;
    width: 100% !important;
    padding: 14px 20px !important;
    background: #ff2d78 !important;
    color: white !important;
}
.stButton > button:hover {
    transform: translate(-2px, -2px) !important;
    box-shadow: 8px 8px 0 #1a0a1e !important;
    background: #ff85b3 !important;
}
.stButton > button:active {
    transform: translate(3px, 3px) !important;
    box-shadow: 2px 2px 0 #1a0a1e !important;
}
.stButton > button[kind="secondary"],
.stButton > button[data-testid="baseButton-secondary"] {
    background: #a7f3d0 !important;
    color: #1a0a1e !important;
}
.stButton > button[kind="secondary"]:hover,
.stButton > button[data-testid="baseButton-secondary"]:hover {
    background: #6ee7b7 !important;
    color: #1a0a1e !important;
}

/* ─── CHECKBOX ─── */
.stCheckbox label p {
    font-family: 'Arial Narrow', Arial, sans-serif !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: #9b2cfa !important;
}

/* ─── ALERTS ─── */
[data-testid="stAlert"] {
    border-radius: 0 !important;
    border-width: 4px !important;
    border-style: solid !important;
    box-shadow: 5px 5px 0 #1a0a1e !important;
    font-family: 'Arial Narrow', Arial, sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
}

/* ─── TABLE ─── */
table {
    border: 4px solid #1a0a1e !important;
    box-shadow: 6px 6px 0 #1a0a1e !important;
    font-family: 'Trebuchet MS', Arial, sans-serif !important;
}
th {
    background: #ff2d78 !important;
    color: white !important;
    font-family: Impact, 'Arial Narrow', sans-serif !important;
    letter-spacing: 2px !important;
    font-size: 16px !important;
    border: 2px solid #1a0a1e !important;
}
td { border: 2px solid #1a0a1e !important; font-weight: 700 !important; }
tr:nth-child(even) td { background: #fff9f0 !important; }

/* ─── EXPANDER ─── */
[data-testid="stExpander"] {
    border: 4px solid #1a0a1e !important;
    border-radius: 0 !important;
    box-shadow: 5px 5px 0 #1a0a1e !important;
    background: #f5f0ff !important;
}
[data-testid="stExpander"] summary {
    font-family: 'Arial Narrow', Arial, sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: #9b2cfa !important;
}

/* ─── CAPTION / FOOTER ─── */
.stCaption p {
    font-family: 'Arial Narrow', Arial, sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
}
footer { color: rgba(26,10,30,0.35) !important; font-style: italic !important; }

/* ─── SPEECH BUBBLE ─── */
.speech-bubble-area {
    margin-bottom: 28px;
    animation: pop 0.45s ease;
}
.speech-bubble {
    background: #ffffff;
    border: 5px solid #1a0a1e;
    border-radius: 24px;
    padding: 22px 30px;
    display: inline-block;
    position: relative;
    box-shadow: 8px 8px 0 #1a0a1e;
    max-width: 620px;
    margin-bottom: 22px;
}
.speech-bubble::after {
    content: '';
    position: absolute;
    bottom: -26px;
    left: 52px;
    width: 0;
    height: 0;
    border-left: 13px solid transparent;
    border-right: 13px solid transparent;
    border-top: 26px solid #1a0a1e;
}
.speech-bubble::before {
    content: '';
    position: absolute;
    bottom: -18px;
    left: 55px;
    width: 0;
    height: 0;
    border-left: 10px solid transparent;
    border-right: 10px solid transparent;
    border-top: 20px solid #ffffff;
    z-index: 1;
}
.game-title {
    font-family: Impact, 'Arial Narrow', sans-serif;
    font-size: 56px;
    line-height: 1;
    letter-spacing: 3px;
    color: #1a0a1e;
    text-shadow: 4px 4px 0 #ff2d78, 8px 8px 0 rgba(192,132,252,0.35);
    animation: wobble 5s ease-in-out infinite;
    display: inline-block;
    margin-bottom: 6px;
}
.subtitle {
    font-family: 'Trebuchet MS', Arial, sans-serif;
    font-size: 13px;
    font-weight: 700;
    font-style: italic;
    color: #9b2cfa;
}

/* ─── SECTION LABEL ─── */
.section-label {
    font-family: Impact, 'Arial Narrow', sans-serif;
    font-size: 36px;
    color: #1a0a1e;
    letter-spacing: 3px;
    text-shadow: 3px 3px 0 #ff85b3;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.boom-badge {
    background: #c084fc;
    color: #1a0a1e;
    font-family: Impact, 'Arial Narrow', sans-serif;
    font-size: 14px;
    letter-spacing: 2px;
    padding: 4px 14px;
    transform: rotate(-2deg);
    box-shadow: 3px 3px 0 #1a0a1e;
    border: 3px solid #1a0a1e;
    animation: wobble 3s ease-in-out infinite;
    display: inline-block;
}
</style>
<div class="speech-bubble-area">
  <div class="speech-bubble">
    <div class="game-title">🎮 RAG Coach: Number Guessing</div>
    <div class="subtitle">An AI strategy coach for number-guessing. Learn to guess smarter.</div>
  </div>
</div>
"""

SECTION_LABEL_HTML = """
<div class="section-label">
  MAKE A GUESS
  <div class="boom-badge">LET'S GO! 💅</div>
</div>
"""

def info_panel_html(low, high, attempts_left):
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bangers&family=Oswald:wght@700&display=swap');
@keyframes shake {{ 0%,100% {{ transform:translateX(0) rotate(-1deg); }} 50% {{ transform:translateX(3px) rotate(1deg); }} }}
.prompt-panel {{
    background: #ff85b3;
    border: 5px solid #1a0a1e;
    padding: 16px 22px;
    margin-bottom: 14px;
    box-shadow: 6px 6px 0 #1a0a1e;
    font-family: 'Arial Narrow', Arial, sans-serif;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 1px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}
.attempts-tag {{
    background: #9b2cfa;
    color: #ffffff;
    font-family: Impact, 'Arial Narrow', sans-serif;
    font-size: 20px;
    padding: 4px 16px;
    letter-spacing: 2px;
    border: 3px solid #1a0a1e;
    box-shadow: 3px 3px 0 #1a0a1e;
    animation: shake 2.5s ease-in-out infinite;
    display: inline-block;
    white-space: nowrap;
}}
</style>
<div class="prompt-panel">
  <span>Guess a number between {low} and {high}.</span>
  <div class="attempts-tag">{attempts_left} LEFT!</div>
</div>
"""


def debug_panel_html(secret, attempts, score, difficulty, history):
    pills = "".join(
        f'<span class="history-pill">{g}</span>' for g in history
    ) or '<span class="history-pill">[ ]</span>'
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bangers&family=Oswald:wght@700&display=swap');
.debug-box-a {{ border: 4px solid #1a0a1e; box-shadow: 6px 6px 0 #1a0a1e; overflow: hidden; }}
.debug-box-a summary {{
  background: #ffffff;
  padding: 10px 16px;
  font-family: 'Oswald', sans-serif;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 3px;
  color: #9b2cfa;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  list-style: none;
}}
.debug-box-a summary::-webkit-details-marker {{ display: none; }}
.debug-box-a[open] summary {{ border-bottom: 4px solid #1a0a1e; }}
.debug-body-a {{ background: #ffffff; padding: 4px 0; }}
.debug-row-a {{
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  border-left: 4px solid transparent;
  border-bottom: 1px solid rgba(26,10,30,0.06);
  transition: border-color 0.15s, background 0.15s;
}}
.debug-row-a:hover {{ border-left-color: #ff2d78; background: rgba(255,45,120,0.04); }}
.debug-row-a:last-child {{ border-bottom: none; }}
.row-label-a {{ font-family: 'Oswald', sans-serif; font-size: 13px; font-weight: 700; letter-spacing: 1px; color: #9b2cfa; width: 90px; flex-shrink: 0; }}
.row-value-a {{ font-family: 'Bangers', cursive; font-size: 20px; letter-spacing: 2px; color: #ff2d78; }}
.history-pill {{ display: inline-block; background: #ede9fe; border: 2px solid #1a0a1e; font-family: 'Oswald', sans-serif; font-size: 11px; font-weight: 700; color: #9b2cfa; padding: 2px 10px; letter-spacing: 1px; margin: 2px 2px 2px 0; }}
</style>
<details class="debug-box-a">
  <summary>&#9654; DEVELOPER DEBUG INFO</summary>
  <div class="debug-body-a">
    <div class="debug-row-a"><span class="row-label-a">Secret</span><span class="row-value-a">{secret}</span></div>
    <div class="debug-row-a"><span class="row-label-a">Attempts</span><span class="row-value-a">{attempts}</span></div>
    <div class="debug-row-a"><span class="row-label-a">Score</span><span class="row-value-a">{score}</span></div>
    <div class="debug-row-a"><span class="row-label-a">Difficulty</span><span class="row-value-a">{difficulty}</span></div>
    <div class="debug-row-a"><span class="row-label-a">History</span><div>{pills}</div></div>
  </div>
</details>
"""

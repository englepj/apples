"""
Classroom market games — one Streamlit app, several projector-run games.

Pick a game in the sidebar. Each game is a self-contained HTML file in this
folder; this wrapper adds two things the HTML files can't do by themselves:

  * Instructor passcode. Until you unlock it, each game's Setup tab (Apple Pit's
    card values, Food Truck Friday's points tables) is hidden. One unlock
    covers every game for as long as this browser tab stays open.
  * Working downloads. The printable cards/sheets and CSV buttons save files.

The passcode is "applesgame" out of the box. It only keeps setup details off
the projector and away from casual clicks; it isn't meant to be secure. To use
a different one, set it in .streamlit/secrets.toml (or the app's Secrets box
on Streamlit Community Cloud), which overrides the default:

    apple_pit_passcode = "choose-something"

Each game also has its own link: add ?game=apples or ?game=foodtruck to the
app's address to open straight to that game.

Run locally:  streamlit run streamlit_app.py
"""

import hmac
import os
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

HERE = Path(__file__).parent

# To add a game: drop its HTML file in this folder and add an entry here.
GAMES = {
    "apples": {
        "label": "🍎 Apple Pit Market",
        "file": "apple_pit_market.html",
        "setup": "Setup & cards",
        "about": "Supply and demand: a double-auction market with buyer and seller cards.",
        "patches": [
            # "Clear examples" would otherwise reuse the example deck, which is the same
            # for everyone who opens the app. Deal a fresh random deck instead, so nobody
            # can look up the cards in their own copy.
            ("state = blankState(state.n, state.seed); save(); view = 'floor';",
             "state = blankState(state.n, (Date.now() % 1e9) | 0); save(); view = 'floor';"),
        ],
    },
    "foodtruck": {
        "label": "🌮 Food Truck Friday",
        "file": "food_truck_friday.html",
        "setup": "Setup & sheets",
        "about": "Consumer choice: spend a budget on tacos and smoothies, then build the demand curve.",
        "patches": [],
    },
}
DEFAULT_PASSCODE = "applesgame"

st.set_page_config(page_title="Classroom Market Games", page_icon="🍎", layout="wide",
                   initial_sidebar_state="collapsed")

# Give the game the whole width on a projector.
st.markdown("""
<style>
.block-container {padding-top: 1rem; padding-bottom: 1rem; max-width: 100%;}
header[data-testid="stHeader"] {background: transparent;}
</style>
""", unsafe_allow_html=True)


# ----------------------------
# Which game
# ----------------------------
def _sync_game_link():
    st.query_params["game"] = st.session_state.game_choice


keys = list(GAMES)
if "game_choice" not in st.session_state:
    wanted = st.query_params.get("game", keys[0])
    st.session_state.game_choice = wanted if wanted in GAMES else keys[0]

with st.sidebar:
    st.markdown("### 🎲 Game")
    st.radio("Game", keys, key="game_choice", format_func=lambda k: GAMES[k]["label"],
             label_visibility="collapsed", on_change=_sync_game_link)
    game = GAMES[st.session_state.game_choice]
    st.caption(game["about"])
    st.divider()


# ----------------------------
# Passcode (one unlock covers every game)
# ----------------------------
def configured_passcode():
    try:
        code = st.secrets.get("apple_pit_passcode")
    except Exception:  # no secrets file at all
        code = None
    return code or os.environ.get("APPLE_PIT_PASSCODE") or DEFAULT_PASSCODE


def check_passcode():
    entered = st.session_state.get("ap_passcode_entry", "")
    if hmac.compare_digest(entered.encode(), str(configured_passcode()).encode()):
        st.session_state.ap_unlocked = True
        st.session_state.ap_passcode_entry = ""
        st.session_state.ap_passcode_error = False
    else:
        st.session_state.ap_passcode_error = True


def lock():
    st.session_state.ap_unlocked = False


unlocked = bool(st.session_state.get("ap_unlocked"))

with st.sidebar:
    st.markdown("### 🔒 Instructor")
    if unlocked:
        st.success("Unlocked. The Setup tab is visible in every game.")
        st.caption("Lock it again before you put this screen on the projector.")
        st.button("Lock", on_click=lock, type="primary")
    else:
        st.text_input("Passcode", type="password", key="ap_passcode_entry", on_change=check_passcode)
        st.button("Unlock setup", on_click=check_passcode)
        if st.session_state.get("ap_passcode_error"):
            st.error("That passcode didn't match.")
        st.caption("Unlocking shows each game's Setup tab (card values, points tables). "
                   "Keep it off the projector.")


# ----------------------------
# Build the page we hand to the game frame
# ----------------------------
# Runs before the game's own script:
#  - gives the game a downloads helper so its download buttons save files;
#  - grows the frame to fit the game, so there's no scrollbar inside a scrollbar.
SHIM = """
<script>
(function () {
  function save(o) {
    var type = /\\.csv$/i.test(o.filename) ? 'text/csv' : 'text/html';
    var url = URL.createObjectURL(new Blob([o.data], {type: type + ';charset=utf-8'}));
    var a = document.createElement('a');
    a.href = url; a.download = o.filename;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 2000);
    return Promise.resolve();
  }
  if (!window.claude) {
    window.claude = { use: function (name) { return Promise.resolve(name === 'downloads' ? {save: save} : null); } };
  }
  function fit() {
    try {
      var f = window.frameElement; if (!f || !document.body) return;
      var h = Math.ceil(document.body.scrollHeight) + 4;
      if (Math.abs((parseInt(f.style.height, 10) || 0) - h) > 2) { f.style.height = h + 'px'; f.height = h; }
    } catch (e) {}
  }
  document.addEventListener('DOMContentLoaded', function () {
    fit();
    try { new ResizeObserver(fit).observe(document.body); } catch (e) { setInterval(fit, 500); }
  });
  window.addEventListener('load', fit);
})();
</script>
"""

# Hides the game's Setup tab and screen when the app is locked.
LOCKED_CSS = """
<style>
#tab-setup, #view-setup { display: none !important; }
</style>
"""


@st.cache_data
def load_game(key, mtime):
    html = (HERE / GAMES[key]["file"]).read_text(encoding="utf-8")
    for old, new in GAMES[key]["patches"]:
        html = html.replace(old, new)
    return html


def game_page(key, unlocked):
    path = HERE / GAMES[key]["file"]
    html = load_game(key, path.stat().st_mtime)
    inject = SHIM + ("" if unlocked else LOCKED_CSS)
    if "<head>" in html:
        return html.replace("<head>", "<head>" + inject, 1)
    return inject + html


key = st.session_state.game_choice
if not (HERE / GAMES[key]["file"]).exists():
    st.error(f"Can't find **{GAMES[key]['file']}**. Put it in the same folder as this app.")
    st.stop()

components.html(game_page(key, unlocked), height=1400, scrolling=True)

st.caption("Each game saves its rounds in this browser, so refreshing or switching games keeps your data. "
           "Switch games and unlock instructor tools in the sidebar (open it with the » arrow at the top left).")

"""
Apple Pit Market — Streamlit wrapper.

Runs the Apple Pit double-auction game (apple_pit_market.html, in this folder)
inside a Streamlit page, and adds two things the HTML file can't do by itself:

  * Instructor passcode. Until you unlock it, the "Setup & cards" tab, which
    lists every card's value and cost, is hidden. Students who open the app
    see the trading floor and debrief only.
  * Working downloads. The "Download printable cards" and "Download results
    (.csv)" buttons save files straight from the game.

The passcode is "applesgame" out of the box. It only keeps the card list off
the projector and away from casual clicks; it isn't meant to be secure. To use
a different one, set it in .streamlit/secrets.toml (or the app's Secrets box
on Streamlit Community Cloud), which overrides the default:

    apple_pit_passcode = "choose-something"

Run locally:  streamlit run streamlit_app.py
"""

import hmac
import os
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

GAME_FILE = Path(__file__).with_name("apple_pit_market.html")

st.set_page_config(page_title="Apple Pit Market", page_icon="🍎", layout="wide",
                   initial_sidebar_state="collapsed")

# Give the game the whole width on a projector.
st.markdown("""
<style>
.block-container {padding-top: 1rem; padding-bottom: 1rem; max-width: 100%;}
header[data-testid="stHeader"] {background: transparent;}
</style>
""", unsafe_allow_html=True)


# ----------------------------
# Passcode
# ----------------------------
DEFAULT_PASSCODE = "applesgame"


def configured_passcode():
    try:
        code = st.secrets.get("apple_pit_passcode")
    except Exception:  # no secrets file at all
        code = None
    return code or os.environ.get("APPLE_PIT_PASSCODE") or DEFAULT_PASSCODE


def check_passcode():
    code = configured_passcode()
    entered = st.session_state.get("ap_passcode_entry", "")
    if code and hmac.compare_digest(entered.encode(), str(code).encode()):
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
        st.success("Unlocked. **Setup & cards** is visible.")
        st.caption("Lock it again before you put this screen on the projector.")
        st.button("Lock", on_click=lock, type="primary")
    else:
        st.text_input("Passcode", type="password", key="ap_passcode_entry", on_change=check_passcode)
        st.button("Unlock Setup & cards", on_click=check_passcode)
        if st.session_state.get("ap_passcode_error"):
            st.error("That passcode didn't match.")
        st.caption("Unlocking shows every card's value and cost. Keep it off the projector.")


# ----------------------------
# Build the page we hand to the game frame
# ----------------------------
# Runs before the game's own script:
#  - gives the game a downloads helper so its two download buttons save files;
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

# Hides the Setup & cards tab and screen when the app is locked.
LOCKED_CSS = """
<style>
#tab-setup, #view-setup { display: none !important; }
</style>
"""


@st.cache_data
def load_game(mtime):
    html = GAME_FILE.read_text(encoding="utf-8")
    # "Clear examples" would otherwise reuse the example deck, which is the same for
    # everyone who opens the app. Deal a fresh random deck instead, so nobody can
    # look up the cards in their own copy.
    html = html.replace("state = blankState(state.n, state.seed); save(); view = 'floor';",
                        "state = blankState(state.n, (Date.now() % 1e9) | 0); save(); view = 'floor';")
    return html


def game_page(unlocked):
    html = load_game(GAME_FILE.stat().st_mtime)
    inject = SHIM + ("" if unlocked else LOCKED_CSS)
    if "<head>" in html:
        return html.replace("<head>", "<head>" + inject, 1)
    return inject + html


if not GAME_FILE.exists():
    st.error(f"Can't find **{GAME_FILE.name}**. Put it in the same folder as this app.")
    st.stop()

components.html(game_page(unlocked), height=1400, scrolling=True)

st.caption("Trades are saved in this browser, so refreshing the page keeps your rounds. "
           "Instructor tools are in the sidebar (open it with the » arrow at the top left).")

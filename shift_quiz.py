"""Shift Happens — supply & demand shift scenarios with live phone voting.

Runs as a game inside streamlit_app.py (sidebar: "Shift Happens", or ?game=shifts).
Also runs on its own:  streamlit run shift_quiz.py

How it works
------------
* The instructor opens the presenter view (?present=1). It creates a 4-letter
  room and shows a QR code + link on the projector.
* Students scan the QR code. Their phone shows the current scenario and big
  A/B/C/D buttons. They can change their vote until voting closes.
* Votes are anonymous: each phone gets a random token in its URL, nothing else.
* Rooms live in server memory (st.cache_resource), shared by every session on
  the same Streamlit process. They reset if the app restarts or sleeps.

Inside streamlit_app.py the presenter screen uses the app's instructor unlock;
students never need it. Optional secret, if the QR code shows the wrong address:
  app_url = "https://yourapp.streamlit.app"
"""

from __future__ import annotations

import io
import random
import threading
import time
import uuid

import altair as alt
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

try:
    import segno  # QR codes, pure Python
except ImportError:  # app still works, just without the QR image
    segno = None

from shift_scenarios import DECKS, KIND_LABELS, MARKET, SCENARIO_BY_ID, SCENARIOS

LETTERS = "ABCDE"
ROOM_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ"  # no I or O
ROOM_TTL_SECONDS = 12 * 3600
STUDENT_REFRESH = 2  # seconds
PRESENTER_REFRESH = 1.5

DEMAND_COLOR = "#2563eb"
SUPPLY_COLOR = "#c2410c"
OLD_COLOR = "#9ca3af"
CORRECT_COLOR = "#16a34a"
OTHER_COLOR = "#94a3b8"
CONTROL_COLOR = "#7c3aed"
DWL_COLOR = "#6b7280"


# --------------------------------------------------------------------------
# Shared room store (one per server process)
# --------------------------------------------------------------------------
@st.cache_resource
def _store() -> dict:
    return {"rooms": {}, "lock": threading.Lock()}


def _prune(rooms: dict) -> None:
    cutoff = time.time() - ROOM_TTL_SECONDS
    for code in [c for c, r in rooms.items() if r["touched"] < cutoff]:
        del rooms[code]


def create_room(order: list[str]) -> str:
    store = _store()
    with store["lock"]:
        _prune(store["rooms"])
        while True:
            code = "".join(random.choices(ROOM_ALPHABET, k=4))
            if code not in store["rooms"]:
                break
        store["rooms"][code] = {
            "order": order,
            "pos": 0,
            "phase": "open",  # open -> closed -> revealed
            "votes": {},  # scenario id -> {token: option index}
            "touched": time.time(),
        }
    return code


def get_room(code: str | None) -> dict | None:
    if not code:
        return None
    return _store()["rooms"].get(code.strip().upper())


def update_room(code: str, **changes) -> None:
    store = _store()
    with store["lock"]:
        room = store["rooms"].get(code)
        if room:
            room.update(changes)
            room["touched"] = time.time()


def go_to(code: str, pos: int) -> None:
    room = get_room(code)
    if room:
        pos = max(0, min(pos, len(room["order"]) - 1))
        update_room(code, pos=pos, phase="open")


def cast_vote(code: str, scenario_id: str, token: str, choice: int) -> bool:
    store = _store()
    with store["lock"]:
        room = store["rooms"].get(code)
        if not room or room["phase"] != "open":
            return False
        if room["order"][room["pos"]] != scenario_id:
            return False  # presenter already moved on
        room["votes"].setdefault(scenario_id, {})[token] = choice
        room["touched"] = time.time()
    return True


def reset_votes(code: str, scenario_id: str) -> None:
    store = _store()
    with store["lock"]:
        room = store["rooms"].get(code)
        if room:
            room["votes"].pop(scenario_id, None)
            room["phase"] = "open"
            room["touched"] = time.time()


def tally(room: dict, scenario: dict) -> list[int]:
    counts = [0] * len(scenario["options"])
    for choice in room["votes"].get(scenario["id"], {}).values():
        if 0 <= choice < len(counts):
            counts[choice] += 1
    return counts


def results_table(room: dict) -> pd.DataFrame:
    """Aggregate counts only — no per-student data."""
    rows = []
    for i, sid in enumerate(room["order"], start=1):
        sc = SCENARIO_BY_ID[sid]
        counts = tally(room, sc)
        n = sum(counts)
        row = {
            "question": i,
            "market": sc["market"],
            "type": KIND_LABELS[sc["kind"]],
            "correct": LETTERS[sc["answer"]],
            "votes": n,
            "pct_correct": round(100 * counts[sc["answer"]] / n) if n else None,
        }
        for j, c in enumerate(counts):
            row[f"votes_{LETTERS[j]}"] = c
        rows.append(row)
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# Graph
# --------------------------------------------------------------------------
def _equilibrium(a: float, b: float) -> tuple[float, float]:
    """Demand P = 12 + a - Q, Supply P = 2 - b + Q (a, b = horizontal shifts)."""
    q = (10 + a + b) / 2
    return q, 12 + a - q


@st.cache_data(show_spinner=False)
def shift_graph_png(d: float, s: float, graph: str | None = None) -> bytes:
    fig, ax = plt.subplots(figsize=(6.2, 4.6), dpi=130)
    qs = [0.0, 15.0]

    def demand(a):
        return [12 + a - q for q in qs]

    def supply(b):
        return [2 - b + q for q in qs]

    def mark(q, p, label, color):
        ax.plot([q, q], [0, p], ls=":", color=color, lw=1)
        ax.plot([0, q], [p, p], ls=":", color=color, lw=1)
        ax.plot(q, p, "o", color=color, ms=7, zorder=5)
        ax.annotate(label, (q, p), textcoords="offset points", xytext=(8, 6),
                    fontsize=11, color=color, weight="bold")

    q1, p1 = _equilibrium(0, 0)

    if graph in ("move", "move_down"):
        ax.plot(qs, demand(0), color=DEMAND_COLOR, lw=2.5)
        ax.text(11.15, 1.1, "D", color=DEMAND_COLOR, fontsize=13, weight="bold")
        p_a, p_b = (7, 9.5) if graph == "move" else (7, 4.5)
        qa, qb = 12 - p_a, 12 - p_b
        mark(qa, p_a, "A", OLD_COLOR)
        mark(qb, p_b, "B", DEMAND_COLOR)
        ax.annotate("", xy=(qb, p_b), xytext=(qa, p_a),
                    arrowprops=dict(arrowstyle="-|>", color="black", lw=2,
                                    shrinkA=8, shrinkB=8))
        ax.set_title("Movement along the demand curve (no shift)", fontsize=12)
    else:
        changed_d, changed_s = d != 0, s != 0
        ax.plot(qs, demand(0), color=OLD_COLOR if changed_d else DEMAND_COLOR, lw=2.2,
                ls="--" if changed_d else "-")
        ax.plot(qs, supply(0), color=OLD_COLOR if changed_s else SUPPLY_COLOR, lw=2.2,
                ls="--" if changed_s else "-")
        def dlabel(a, text, color):  # where demand crosses P = 1
            ax.text(11 + a + 0.15, 1.1, text, color=color, fontsize=12, weight="bold")

        def slabel(b, text, color):  # where supply crosses P = 13
            ax.text(11 + b + 0.25, 12.7, text, color=color, fontsize=12, weight="bold")

        dlabel(0, "D₁" if changed_d else "D", OLD_COLOR if changed_d else DEMAND_COLOR)
        slabel(0, "S₁" if changed_s else "S", OLD_COLOR if changed_s else SUPPLY_COLOR)
        if changed_d:
            ax.plot(qs, demand(d), color=DEMAND_COLOR, lw=2.6)
            dlabel(d, "D₂", DEMAND_COLOR)
            y = 3.2
            ax.annotate("", xy=(12 - y + d, y), xytext=(12 - y, y),
                        arrowprops=dict(arrowstyle="-|>", color=DEMAND_COLOR, lw=2))
        if changed_s:
            ax.plot(qs, supply(s), color=SUPPLY_COLOR, lw=2.6)
            slabel(s, "S₂", SUPPLY_COLOR)
            y = 11
            ax.annotate("", xy=(y - 2 + s, y), xytext=(y - 2, y),
                        arrowprops=dict(arrowstyle="-|>", color=SUPPLY_COLOR, lw=2))
        mark(q1, p1, "E₁", OLD_COLOR if (changed_d or changed_s) else "black")
        if changed_d or changed_s:
            q2, p2 = _equilibrium(d, s)
            mark(q2, p2, "E₂", "black")

    ax.set_xlim(0, 15)
    ax.set_ylim(0, 14)
    ax.set_xlabel("Quantity", fontsize=11)
    ax.set_ylabel("Price", fontsize=11)
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    return buf.getvalue()


# --------------------------------------------------------------------------
# Numeric market: surplus, price ceilings and floors
# --------------------------------------------------------------------------
def _shoelace(poly: list[tuple[float, float]]) -> tuple[float, tuple[float, float]]:
    """Area and centroid of a polygon (repeated points are fine)."""
    a = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        cross = x0 * y1 - x1 * y0
        a += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    if abs(a) < 1e-12:
        return 0.0, (0.0, 0.0)
    return abs(a) / 2, (cx / (3 * a), cy / (3 * a))


def market_outcome(control: tuple[str, float] | None) -> dict:
    """CS, PS and deadweight loss in MARKET, with an optional ("ceiling"|"floor", price).
    Assumes the crates that do trade go to the highest-value buyers and come from
    the lowest-cost sellers."""
    a, b, c, d = (MARKET[k] for k in "abcd")
    qe = (a - c) / (b + d)
    pe = a - b * qe
    kind, pc = control if control else (None, None)
    binding = (kind == "ceiling" and pc < pe) or (kind == "floor" and pc > pe)
    if binding:
        qt, pp = min((a - pc) / b, (pc - c) / d), pc
    else:
        qt, pp = qe, pe
    value, cost = a - b * qt, c + d * qt  # last buyer's value, last seller's cost
    polys = {
        "cs": [(0, pp), (0, a), (qt, value), (qt, pp)],
        "ps": [(0, c), (0, pp), (qt, pp), (qt, cost)],
        "dwl": [(qt, value), (qe, pe), (qt, cost)] if qt < qe - 1e-9 else [],
    }
    areas = {k: _shoelace(v)[0] if v else 0.0 for k, v in polys.items()}
    return dict(qe=qe, pe=pe, qt=qt, pp=pp, binding=binding, kind=kind, pc=pc,
                qd=(a - pp) / b, qs=(pp - c) / d, polys=polys,
                cs=areas["cs"], ps=areas["ps"], dwl=areas["dwl"],
                ts=areas["cs"] + areas["ps"])


def _money(v: float, sign: bool = False) -> str:
    v = round(v, 2)
    body = f"${abs(v):,.0f}" if v == int(v) else f"${abs(v):,.2f}"
    if sign:
        return "no change" if v == 0 else ("+" if v > 0 else "−") + body
    return ("−" if v < 0 else "") + body


def surplus_table_md(control) -> str:
    before, after = market_outcome(None), market_outcome(control)
    rows = [("Consumer surplus", "cs"), ("Producer surplus", "ps"),
            ("Total surplus", "ts"), ("Deadweight loss", "dwl")]
    out = ["| | Free market | With the control | Change |", "|---|---:|---:|---:|"]
    for label, k in rows:
        out.append(f"| {label} | {_money(before[k])} | {_money(after[k])} | "
                   f"{_money(after[k] - before[k], sign=True)} |")
    return "\n".join(out)


@st.cache_data(show_spinner=False)
def numeric_graph_png(control: tuple | None, shade: str, revealed: bool,
                      labels: str = "points") -> bytes:
    a, b, c, d = (MARKET[k] for k in "abcd")
    m = market_outcome(control)
    fig, ax = plt.subplots(figsize=(6.4, 5.0), dpi=130)
    qmax, pmax = 20, 20
    ax.plot([0, qmax], [a, a - b * qmax], color=DEMAND_COLOR, lw=2.6, zorder=3)
    ax.plot([0, qmax], [c, c + d * qmax], color=SUPPLY_COLOR, lw=2.6, zorder=3)
    ax.text(19.0, 2.2, "D", color=DEMAND_COLOR, fontsize=14, weight="bold")
    ax.text(18.9, c + d * 18.9 + 0.7, "S", color=SUPPLY_COLOR, fontsize=14, weight="bold")

    if control:
        kind, pc = control
        ax.axhline(pc, color=CONTROL_COLOR, ls="--", lw=2, zorder=4)
        tag = f"Price {kind} ${pc:g}"
        if revealed and not m["binding"]:
            tag += " (not binding)"
        ax.text(0.3, pc + 0.35, tag, color=CONTROL_COLOR, fontsize=11, weight="bold")

    if revealed:
        fills = {"cs": (DEMAND_COLOR, "CS"), "ps": (SUPPLY_COLOR, "PS"),
                 "dwl": (DWL_COLOR, "DWL")}
        show = {"cs": ["cs"], "ps": ["ps"], "ts": ["cs", "ps"],
                "all": ["cs", "ps", "dwl"], "eq": []}[shade]
        for k in show:
            poly = m["polys"][k]
            if not poly:
                continue
            color, name = fills[k]
            area, (cx, cy) = _shoelace(poly)
            ax.fill([x for x, _ in poly], [y for _, y in poly], color=color,
                    alpha=0.42 if k == "dwl" else 0.22, zorder=1,
                    hatch="///" if k == "dwl" else None, edgecolor=color if k == "dwl" else None)
            label = f"{name} = {_money(area)}"
            if area < 15:  # small triangle: label beside it with a pointer
                dx, dy = (2.8, -2.8) if m["kind"] == "floor" else (3.5, 3.0)
                ax.annotate(label, (cx, cy), xytext=(cx + dx, cy + dy),
                            fontsize=11, weight="bold", color="#374151",
                            arrowprops=dict(arrowstyle="-", color="#374151", lw=1))
            else:
                ax.text(cx, cy, label, ha="center", va="center", fontsize=11.5,
                        weight="bold", color="#1f2937", zorder=6)
        # shortage / surplus at the control price
        if control and m["binding"]:
            qs, qd, pc = m["qs"], m["qd"], m["pc"]
            lo, hi = sorted((qs, qd))
            y = pc - 1.5 if m["kind"] == "ceiling" else pc + 0.9
            ax.annotate("", xy=(hi, y), xytext=(lo, y),
                        arrowprops=dict(arrowstyle="<->", color=CONTROL_COLOR, lw=1.8))
            word = "Shortage" if m["kind"] == "ceiling" else "Surplus"
            ax.text((lo + hi) / 2, y + (-0.75 if m["kind"] == "ceiling" else 0.35),
                    f"{word} = {hi - lo:g}", ha="center", color=CONTROL_COLOR,
                    fontsize=11, weight="bold")
            ax.plot([m["qt"]] * 2, [0, pc], ls=":", color=CONTROL_COLOR, lw=1.2)

    # Labeled points: intercepts always; equilibrium and the triangle corners when
    # labels == "points" (or once the answer is revealed).
    def point(q, p, color, offset):
        ax.plot(q, p, "o", color=color, ms=6.5, zorder=8, clip_on=False)
        text = f"${p:g}" if q == 0 else f"({q:g}, ${p:g})"
        ax.annotate(text, (q, p), xytext=offset, textcoords="offset points",
                    fontsize=11, weight="bold", color=color, zorder=9,
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.8))

    point(0, a, DEMAND_COLOR, (8, -4))
    point(0, c, SUPPLY_COLOR, (8, -4))
    if labels == "points" or revealed:
        ax.plot([m["qe"]] * 2, [0, m["pe"]], ls=":", color="black", lw=1)
        ax.plot([0, m["qe"]], [m["pe"]] * 2, ls=":", color="black", lw=1)
        point(m["qe"], m["pe"], "black", (12, -4))
        if control and m["binding"]:
            pc, qt = m["pc"], m["qt"]
            if m["kind"] == "ceiling":
                point(m["qs"], pc, SUPPLY_COLOR, (-58, 6))
                point(m["qd"], pc, DEMAND_COLOR, (8, 4))
                point(qt, a - b * qt, DEMAND_COLOR, (8, 4))
            else:
                point(m["qd"], pc, DEMAND_COLOR, (-62, 6))
                point(m["qs"], pc, SUPPLY_COLOR, (6, -16))
                point(qt, c + d * qt, SUPPLY_COLOR, (-60, -14))

    ax.set_xlim(0, qmax)
    ax.set_ylim(0, pmax)
    ax.set_xticks(range(0, qmax + 1, 2))
    ax.set_yticks(range(0, pmax + 1, 2))
    ax.set_yticklabels([f"${v}" for v in range(0, pmax + 1, 2)])
    ax.grid(True, color="#d1d5db", lw=0.6, zorder=0)
    ax.set_xlabel(f"Quantity ({MARKET['q_unit']})", fontsize=11)
    ax.set_ylabel("Price ($ per crate)", fontsize=11)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    return buf.getvalue()


def show_graph(sc: dict, revealed: bool = True) -> None:
    if "num" in sc:
        control = sc["num"]["control"]
        st.image(numeric_graph_png(tuple(control) if control else None, sc["num"]["shade"],
                                   revealed, sc["num"].get("labels", "points")),
                 width="stretch")
        if revealed and sc["kind"] == "control":
            st.markdown(surplus_table_md(tuple(control)))
        return
    st.image(shift_graph_png(sc["d"], sc["s"], sc.get("graph")), width="stretch")
    if sc["kind"] == "double":
        st.caption("Drawn with one shift larger than the other. Make the other shift "
                   "bigger and the ambiguous variable goes the other way.")


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def _secret(name: str) -> str | None:
    try:
        return st.secrets.get(name) or st.secrets.get(name.upper())
    except Exception:  # no secrets file
        return None


def _base_url() -> str | None:
    url = _secret("app_url")
    if url:
        return url.rstrip("/")
    ctx_url = getattr(st.context, "url", None)
    if ctx_url:
        return ctx_url.split("?")[0].rstrip("/")
    return None


def _qr_png(text: str) -> bytes | None:
    if segno is None:
        return None
    buf = io.BytesIO()
    segno.make(text, error="m").save(buf, kind="png", scale=10, border=2)
    return buf.getvalue()


def _bars(sc: dict, counts: list[int], revealed: bool):
    df = pd.DataFrame({
        "option": [f"{LETTERS[i]}. {o}" for i, o in enumerate(sc["options"])],
        "votes": counts,
        "correct": [revealed and i == sc["answer"] for i in range(len(counts))],
    })
    return (
        alt.Chart(df)
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            y=alt.Y("option:N", sort=None, title=None,
                    axis=alt.Axis(labelFontSize=15, labelLimit=420)),
            x=alt.X("votes:Q", title=None, axis=alt.Axis(tickMinStep=1)),
            color=alt.condition("datum.correct", alt.value(CORRECT_COLOR),
                                alt.value(OTHER_COLOR)),
            tooltip=["option", "votes"],
        )
        .properties(height=46 * len(counts))
    )


# --------------------------------------------------------------------------
# Student (phone) view
# --------------------------------------------------------------------------
STUDENT_CSS = """
<style>
div[data-testid="stButton"] > button { min-height: 3.4rem; font-size: 1.1rem;
  text-align: left; justify-content: flex-start; }
.sh-market { font-size: 1.15rem; font-weight: 700; margin-bottom: .25rem; }
.sh-text { font-size: 1.1rem; line-height: 1.45; }
</style>
"""


def _student_token() -> str:
    token = st.query_params.get("v")
    if not token:
        token = uuid.uuid4().hex[:10]
        st.query_params["v"] = token  # survives a refresh, so no double votes
    return token


@st.fragment(run_every=STUDENT_REFRESH)
def _student_panel(code: str, token: str) -> None:
    room = get_room(code)
    if not room:
        st.error(f"Room **{code}** isn't open. Check the code on the screen.")
        return
    sid = room["order"][room["pos"]]
    sc = SCENARIO_BY_ID[sid]
    phase = room["phase"]
    mine = room["votes"].get(sid, {}).get(token)

    st.caption(f"Room {code} · Question {room['pos'] + 1} of {len(room['order'])} · "
               f"{KIND_LABELS[sc['kind']]}")
    st.markdown(f"<div class='sh-market'>Market: {sc['market']}</div>"
                f"<div class='sh-text'>{sc['text']}</div>", unsafe_allow_html=True)
    if "num" in sc and phase != "revealed":
        show_graph(sc, revealed=False)
    st.write("")

    if phase == "open":
        for i, opt in enumerate(sc["options"]):
            st.button(f"{LETTERS[i]}.  {opt}", key=f"vote_{sid}_{i}",
                      type="primary" if mine == i else "secondary",
                      width="stretch",
                      on_click=cast_vote, args=(code, sid, token, i))
        if mine is None:
            st.info("Tap your answer.")
        else:
            st.success(f"Vote recorded: **{LETTERS[mine]}**. Tap another to change it.")
        return

    # closed or revealed
    for i, opt in enumerate(sc["options"]):
        prefix = "✅ " if (phase == "revealed" and i == sc["answer"]) else ""
        you = "  ← your vote" if mine == i else ""
        st.markdown(f"{prefix}**{LETTERS[i]}.** {opt}{you}")
    st.write("")
    if phase == "closed":
        st.warning("Voting is closed. Eyes on the screen.")
    else:
        if mine is None:
            st.info(f"Answer: **{LETTERS[sc['answer']]}**. You didn't vote on this one.")
        elif mine == sc["answer"]:
            st.success(f"Correct — **{LETTERS[sc['answer']]}**.")
        else:
            st.error(f"Not quite. Answer: **{LETTERS[sc['answer']]}**.")
        st.write(sc["why"])
        if "num" in sc:
            show_graph(sc)
        else:
            with st.expander("Show the graph"):
                show_graph(sc)


def student_view(code: str | None = None) -> None:
    st.markdown(STUDENT_CSS, unsafe_allow_html=True)
    st.subheader("Shift Happens")
    code = (code or "").strip().upper()
    if not code or not get_room(code):
        if code:
            st.error(f"No open room called **{code}**.")
        entered = st.text_input("Room code (on the screen)", max_chars=4).strip().upper()
        if st.button("Join", type="primary", width="stretch") and entered:
            st.query_params["room"] = entered
            st.rerun()
        return
    _student_panel(code, _student_token())


# --------------------------------------------------------------------------
# Presenter (projector) view
# --------------------------------------------------------------------------
PRESENTER_CSS = """
<style>
.sh-q-kind { font-size: 1rem; text-transform: uppercase; letter-spacing: .06em;
  opacity: .7; }
.sh-q-market { font-size: 1.6rem; font-weight: 700; margin: .2rem 0 .4rem; }
.sh-q-text { font-size: 2.1rem; line-height: 1.3; margin-bottom: .8rem; }
.sh-opt { font-size: 1.45rem; margin: .25rem 0; }
.sh-room { font-size: 3rem; font-weight: 800; letter-spacing: .12em; line-height: 1; }
.sh-count { font-size: 1.6rem; font-weight: 700; }
</style>
"""


def _passcode_ok() -> bool:
    passcode = _secret("instructor_passcode")
    if not passcode or st.session_state.get("sh_authed"):
        return True
    entered = st.text_input("Instructor passcode", type="password")
    if entered and entered == passcode:
        st.session_state["sh_authed"] = True
        st.rerun()
    elif entered:
        st.error("Wrong passcode.")
    return False


def _deck_settings() -> list[str] | None:
    """Returns a new question order if the instructor starts a new deck."""
    with st.expander("Deck settings", expanded=False):
        preset = st.radio("Deck", list(DECKS) + ["Everything"], horizontal=True)
        kinds = st.multiselect(
            "Question types",
            options=list(KIND_LABELS),
            default=DECKS.get(preset, list(KIND_LABELS)),
            format_func=KIND_LABELS.get,
            key=f"sh_kinds_{preset}",
        )
        pool = [s for s in SCENARIOS if s["kind"] in kinds]
        chosen = st.multiselect(
            "Scenarios (in this order)",
            options=[s["id"] for s in pool],
            default=[s["id"] for s in pool],
            format_func=lambda sid: f"{SCENARIO_BY_ID[sid]['market']} — "
                                    f"{KIND_LABELS[SCENARIO_BY_ID[sid]['kind']]}",
            key=f"sh_chosen_{preset}_{'-'.join(kinds)}",
        )
        shuffle = st.checkbox("Shuffle order", value=False)
        if st.button("Start new room with this deck", disabled=not chosen):
            order = list(chosen)
            if shuffle:
                random.shuffle(order)
            return order
    return None


@st.fragment(run_every=PRESENTER_REFRESH)
def _presenter_live(code: str, show_live_bars: bool) -> None:
    room = get_room(code)
    if not room:
        return
    sc = SCENARIO_BY_ID[room["order"][room["pos"]]]
    counts = tally(room, sc)
    n = sum(counts)
    phase = room["phase"]
    status = {"open": "🟢 Voting open", "closed": "⏸ Voting closed",
              "revealed": "✅ Answer revealed"}[phase]
    st.markdown(f"<span class='sh-count'>{n} vote{'s' if n != 1 else ''}</span>"
                f"&nbsp;&nbsp;{status}", unsafe_allow_html=True)
    if phase == "revealed" or show_live_bars or phase == "closed":
        st.altair_chart(_bars(sc, counts, phase == "revealed"), width="stretch")


def presenter_view(unlocked: bool | None = None) -> None:
    st.markdown(PRESENTER_CSS, unsafe_allow_html=True)
    if unlocked is False:
        st.subheader("Shift Happens — presenter screen")
        st.info("Unlock instructor tools in the sidebar (» at the top left) to run the "
                "presenter screen. Students joining by QR code don't need this.")
        return
    if unlocked is None and not _passcode_ok():
        return

    new_order = _deck_settings()
    code = st.query_params.get("room")
    if new_order or not get_room(code):
        code = create_room(new_order or [s["id"] for s in SCENARIOS])
        st.query_params["present"] = "1"
        st.query_params["room"] = code
        st.rerun()

    room = get_room(code)
    sc = SCENARIO_BY_ID[room["order"][room["pos"]]]
    phase = room["phase"]

    # ---- header: question | join info
    left, right = st.columns([3, 1], gap="large")
    with left:
        st.markdown(
            f"<div class='sh-q-kind'>Question {room['pos'] + 1} of {len(room['order'])}"
            f" · {KIND_LABELS[sc['kind']]}</div>"
            f"<div class='sh-q-market'>Market: {sc['market']}</div>"
            f"<div class='sh-q-text'>{sc['text']}</div>",
            unsafe_allow_html=True,
        )
        for i, opt in enumerate(sc["options"]):
            mark = "✅ " if phase == "revealed" and i == sc["answer"] else ""
            st.markdown(f"<div class='sh-opt'>{mark}<b>{LETTERS[i]}.</b> {opt}</div>",
                        unsafe_allow_html=True)
    with right:
        base = _base_url()
        extra = "".join(f"{k}={v}&" for k, v in _LINK_PARAMS.items())
        join_url = f"{base}/?{extra}room={code}" if base else None
        if join_url:
            qr = _qr_png(join_url)
            if qr:
                st.image(qr, width="stretch")
        st.markdown(f"<div style='text-align:center'>Room<br>"
                    f"<span class='sh-room'>{code}</span></div>", unsafe_allow_html=True)
        if join_url:
            st.caption(join_url)
        else:
            st.caption("Set `app_url` in secrets to show a QR code.")

    # ---- controls
    st.divider()
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    if c1.button("◀ Prev", width="stretch", disabled=room["pos"] == 0):
        go_to(code, room["pos"] - 1)
        st.rerun()
    if phase == "open":
        if c2.button("⏸ Close voting", width="stretch"):
            update_room(code, phase="closed")
            st.rerun()
    elif c2.button("▶ Reopen voting", width="stretch"):
        update_room(code, phase="open")
        st.rerun()
    if c3.button("✅ Reveal", type="primary", width="stretch",
                 disabled=phase == "revealed"):
        update_room(code, phase="revealed")
        st.rerun()
    if c4.button("Next ▶", width="stretch",
                 disabled=room["pos"] >= len(room["order"]) - 1):
        go_to(code, room["pos"] + 1)
        st.rerun()
    if c5.button("↺ Clear votes", width="stretch"):
        reset_votes(code, sc["id"])
        st.rerun()
    show_live = c6.toggle("Live bars", value=False,
                          help="Off by default so early votes don't steer the room.")

    # ---- live tally + reveal
    tally_col, graph_col = st.columns([1, 1], gap="large")
    with tally_col:
        _presenter_live(code, show_live)
    with graph_col:
        if "num" in sc:
            show_graph(sc, revealed=phase == "revealed")
        elif phase == "revealed":
            show_graph(sc)
    if phase == "revealed":
        st.info(sc["why"])

    # ---- end-of-class summary (aggregate counts only)
    with st.expander("Class summary"):
        df = results_table(room)
        st.dataframe(df, hide_index=True, width="stretch")
        st.download_button("Download summary CSV", df.to_csv(index=False).encode(),
                           file_name=f"shift_happens_{code}.csv", mime="text/csv")


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------
_LINK_PARAMS: dict[str, str] = {}


def render(unlocked: bool | None = None, link_params: dict | None = None) -> None:
    """unlocked: the host app's instructor unlock (None = use this file's own
    optional passcode). link_params: extra query params for the students' join
    link, e.g. {"game": "shifts"} so phones open straight to this game."""
    _LINK_PARAMS.clear()
    _LINK_PARAMS.update(link_params or {})
    qp = st.query_params
    if qp.get("present"):
        presenter_view(unlocked)
    elif qp.get("room"):
        student_view(qp.get("room"))
    else:
        st.title("Shift Happens")
        st.write("Supply & demand shift scenarios with phone voting.")
        a, b = st.columns(2)
        with a:
            st.subheader("Student")
            student_view(None)
        with b:
            st.subheader("Instructor")
            if st.button("Open presenter screen", width="stretch"):
                st.query_params["present"] = "1"
                st.rerun()


if __name__ == "__main__":
    st.set_page_config(page_title="Shift Happens", page_icon="📈", layout="wide")
    render()

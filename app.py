"""
Cockburn ARC — Beginner Gym Tracker
A simple Streamlit app to follow the day-by-day programme and tick off
each exercise as you complete it. Built to run on a phone browser.
"""

import json
import datetime as dt
from pathlib import Path

import streamlit as st

# --------------------------------------------------------------------------
# Programme data
# --------------------------------------------------------------------------

SESSION_A = [
    {"exercise": "Leg press",        "machine": "Leg press machine",          "start": "40–50 kg", "sets": "3 × 10–15"},
    {"exercise": "Chest press",      "machine": "Chest press machine",        "start": "15–20 kg", "sets": "3 × 10–15"},
    {"exercise": "Seated row",       "machine": "Seated row machine",         "start": "20–25 kg", "sets": "3 × 10–15"},
    {"exercise": "Leg curl",         "machine": "Lying/seated leg curl",      "start": "15–20 kg", "sets": "3 × 10–15"},
    {"exercise": "Shoulder press",   "machine": "Shoulder press machine",     "start": "10–15 kg", "sets": "2 × 10–15"},
    {"exercise": "Abdominal crunch", "machine": "Ab crunch machine",          "start": "10–15 kg", "sets": "3 × 12–15"},
]

SESSION_B = [
    {"exercise": "Leg extension",        "machine": "Leg extension machine",  "start": "15–25 kg", "sets": "3 × 10–15"},
    {"exercise": "Lat pulldown",         "machine": "Lat pulldown machine",   "start": "20–25 kg", "sets": "3 × 10–15"},
    {"exercise": "Chest fly",            "machine": "Pec deck machine",       "start": "10–15 kg", "sets": "3 × 10–15"},
    {"exercise": "Glute / hip thrust",   "machine": "Glute or hip-thrust",    "start": "20–30 kg", "sets": "3 × 10–15"},
    {"exercise": "Lateral raise",        "machine": "Lateral raise machine",  "start": "5 kg",     "sets": "2 × 12–15"},
    {"exercise": "Lower back extension", "machine": "Back extension machine", "start": "10 kg",    "sets": "2 × 12–15"},
]

WARMUP = "5–10 min easy cardio (treadmill walk, bike or cross-trainer) until warm."
FINISHER = "15–20 min steady cardio — incline walk, bike, stair climber or pool laps."
COOLDOWN = "5 min easy walking + a few gentle stretches."
ACTIVE_RECOVERY = "20–30 min easy walk, pool laps or swim, plus a light full-body stretch. Keep it easy."

# weekday(): Mon=0 ... Sun=6
def get_day_plan(d: dt.date, start_monday: dt.date) -> dict:
    """Return the plan for a given date based on the two-week A/B cycle."""
    weeks_between = (d - d.weekday() * dt.timedelta(days=1) - start_monday).days // 7
    parity = weeks_between % 2  # 0 = Week 1, 1 = Week 2
    wd = d.weekday()

    if wd in (0, 4):  # Monday, Friday
        return {"type": "rest", "title": "Rest day", "note": "Full day off. A few gentle stretches at home if you like."}
    if wd in (2, 6):  # Wednesday, Sunday
        return {"type": "recovery", "title": "Active recovery", "note": ACTIVE_RECOVERY}

    # Gym days: Tue=1, Thu=3, Sat=5
    if wd == 1:
        session = "A" if parity == 0 else "B"
    elif wd == 3:
        session = "B" if parity == 0 else "A"
    else:  # wd == 5
        session = "A" if parity == 0 else "B"

    exercises = SESSION_A if session == "A" else SESSION_B
    week_label = "Week 1" if parity == 0 else "Week 2"
    return {"type": "gym", "title": f"Session {session} — Full Body", "session": session,
            "week": week_label, "exercises": exercises}


# --------------------------------------------------------------------------
# Persistence (local JSON file)
# --------------------------------------------------------------------------

DATA_FILE = Path(__file__).parent / "data" / "progress.json"


def load_data() -> dict:
    try:
        if DATA_FILE.exists():
            return json.loads(DATA_FILE.read_text())
    except Exception:
        pass
    return {}


def save_data(data: dict) -> None:
    try:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text(json.dumps(data, indent=2))
    except Exception as e:
        st.warning(f"Couldn't save progress: {e}")


# --------------------------------------------------------------------------
# App
# --------------------------------------------------------------------------

st.set_page_config(page_title="ARC Gym Tracker", page_icon="💪", layout="centered")

# Load persisted data into session once
if "data" not in st.session_state:
    st.session_state.data = load_data()
data = st.session_state.data

# Settings: programme start (snapped to the Monday of that week)
settings = data.setdefault("_settings", {})
default_start = settings.get("start_date", dt.date.today().isoformat())
start_date = dt.date.fromisoformat(default_start)
start_monday = start_date - dt.timedelta(days=start_date.weekday())

# Current date in view
if "current_date" not in st.session_state:
    st.session_state.current_date = dt.date.today()

st.title("💪 ARC Gym Tracker")
st.caption("Beginner full-body programme · Cockburn ARC")

# --- Date navigation ---
nav1, nav2, nav3 = st.columns(3)
with nav1:
    if st.button("◀ Prev", use_container_width=True):
        st.session_state.current_date -= dt.timedelta(days=1)
with nav2:
    if st.button("Today", use_container_width=True):
        st.session_state.current_date = dt.date.today()
with nav3:
    if st.button("Next ▶", use_container_width=True):
        st.session_state.current_date += dt.timedelta(days=1)

picked = st.date_input("Date", value=st.session_state.current_date, format="DD/MM/YYYY")
if picked != st.session_state.current_date:
    st.session_state.current_date = picked

d = st.session_state.current_date
date_iso = d.isoformat()
plan = get_day_plan(d, start_monday)

st.markdown(f"### {d.strftime('%A, %d %B %Y')}")

day_record = data.setdefault(date_iso, {})

# --- Render the day ---
if plan["type"] == "gym":
    st.success(f"**{plan['title']}**  ·  {plan['week']}")
    with st.expander("Warm-up · finisher · cool-down"):
        st.write(f"**Warm-up:** {WARMUP}")
        st.write(f"**Cardio finisher:** {FINISHER}")
        st.write(f"**Cool-down:** {COOLDOWN}")
    st.write("Tick each exercise as you finish it, and log the weight you used.")

    items = day_record.setdefault("items", {})
    done_count = 0
    total = len(plan["exercises"])

    for ex in plan["exercises"]:
        name = ex["exercise"]
        rec = items.setdefault(name, {"done": False, "weight": ""})

        c1, c2 = st.columns([3, 2])
        with c1:
            checked = st.checkbox(
                f"**{name}**  \n_{ex['machine']}_  ·  {ex['sets']}",
                value=rec.get("done", False),
                key=f"done|{date_iso}|{name}",
            )
        with c2:
            weight = st.text_input(
                f"Weight ({ex['start']})",
                value=rec.get("weight", ""),
                key=f"wt|{date_iso}|{name}",
                placeholder=ex["start"],
            )
        rec["done"] = checked
        rec["weight"] = weight
        if checked:
            done_count += 1
        st.divider()

    st.progress(done_count / total, text=f"{done_count} / {total} exercises done")
    if done_count == total:
        st.balloons()
        st.success("Session complete — nice work! 🎉")

elif plan["type"] == "recovery":
    st.info(f"**{plan['title']}**")
    st.write(plan["note"])
    rec_done = st.checkbox("Done for today", value=day_record.get("done", False),
                           key=f"recovery|{date_iso}")
    day_record["done"] = rec_done
    if rec_done:
        st.success("Nice — recovery counts too. 👍")

else:  # rest
    st.warning(f"**{plan['title']}**")
    st.write(plan["note"])
    st.caption("No session scheduled. Enjoy the rest — it's when your body adapts.")

# Persist after rendering
save_data(data)

# --------------------------------------------------------------------------
# Reference + settings (sidebar)
# --------------------------------------------------------------------------

with st.sidebar:
    st.header("This week")
    monday = d - dt.timedelta(days=d.weekday())
    for i in range(7):
        day = monday + dt.timedelta(days=i)
        p = get_day_plan(day, start_monday)
        label = {"gym": p["title"].split(" — ")[0] if p["type"] == "gym" else "",
                 "recovery": "Active recovery", "rest": "Rest"}[p["type"]]
        marker = "→ " if day == d else "  "
        st.write(f"{marker}**{day.strftime('%a')}** · {label}")

    st.divider()
    st.header("How weights work")
    st.write(
        "The **Weight** boxes are conservative starting points. The right weight "
        "is the one where your **last 1–2 reps feel hard but your form stays clean**.\n\n"
        "First set too easy? Go up a notch (usually 5 kg). Form breaks? Drop one. "
        "Then log what you used."
    )
    st.write(
        "**Progressing:** once you can hit the top of the rep range for all sets "
        "with good form two sessions running, add a little weight next time."
    )

    st.divider()
    st.header("Settings")
    new_start = st.date_input("Programme start date", value=start_date, format="DD/MM/YYYY",
                              help="Sets which week is Week 1. Snaps to that week's Monday.")
    if new_start.isoformat() != settings.get("start_date"):
        settings["start_date"] = new_start.isoformat()
        save_data(data)
        st.rerun()

    st.divider()
    if st.button("Reset this day"):
        if date_iso in data:
            data.pop(date_iso)
            save_data(data)
            st.rerun()

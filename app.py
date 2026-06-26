"""
Cockburn ARC — Intermediate Gym Tracker
A simple Streamlit app to follow the day-by-day programme and tick off
each exercise as you complete it. Built to run on a phone browser.
"""

import json
import datetime as dt
from pathlib import Path

import streamlit as st

# --------------------------------------------------------------------------
# Programme data (Intermediate — three rotating full-body sessions)
# --------------------------------------------------------------------------

SESSION_A = [  # squat & press
    {"exercise": "Leg press",      "machine": "Leg press (or back squat)",             "start": "90–140 kg",  "sets": "4 × 6–10"},
    {"exercise": "Chest press",    "machine": "Chest press machine (or bench)",         "start": "30–50 kg",   "sets": "4 × 6–10"},
    {"exercise": "Seated row",     "machine": "Seated row machine (or DB row)",         "start": "35–55 kg",   "sets": "3 × 8–12"},
    {"exercise": "Leg curl",       "machine": "Lying/seated leg curl",                  "start": "25–40 kg",   "sets": "3 × 10–15"},
    {"exercise": "Shoulder press", "machine": "Shoulder press machine (or DB)",         "start": "20–35 kg",   "sets": "3 × 8–12"},
    {"exercise": "Lateral raise",  "machine": "Lateral raise machine (or DB)",          "start": "7.5–12.5 kg","sets": "3 × 12–15"},
    {"exercise": "Cable crunch",   "machine": "Cable / ab crunch",                      "start": "20–35 kg",   "sets": "3 × 12–15"},
]

SESSION_B = [  # hinge & pull
    {"exercise": "Romanian deadlift",  "machine": "RDL (or hip-thrust machine)",        "start": "40–70 kg",   "sets": "4 × 8–12"},
    {"exercise": "Lat pulldown",       "machine": "Lat pulldown machine",               "start": "35–55 kg",   "sets": "4 × 8–12"},
    {"exercise": "Incline chest press","machine": "Incline chest press (or incline DB)","start": "25–45 kg",   "sets": "3 × 8–12"},
    {"exercise": "Leg extension",      "machine": "Leg extension machine",              "start": "30–50 kg",   "sets": "3 × 12–15"},
    {"exercise": "Rear-delt fly",      "machine": "Reverse pec deck (or cable)",        "start": "15–30 kg",   "sets": "3 × 12–15"},
    {"exercise": "Biceps curl",        "machine": "Cable or DB curl",                   "start": "10–20 kg",   "sets": "3 × 10–15"},
    {"exercise": "Triceps pushdown",   "machine": "Cable pushdown",                     "start": "15–30 kg",   "sets": "3 × 10–15"},
]

SESSION_C = [  # mixed volume
    {"exercise": "Hack squat",            "machine": "Hack squat (or split squat)",     "start": "40–80 kg",   "sets": "4 × 8–12"},
    {"exercise": "Glute / hip thrust",    "machine": "Hip-thrust machine",              "start": "50–90 kg",   "sets": "3 × 10–15"},
    {"exercise": "Chest fly",             "machine": "Pec deck",                        "start": "25–45 kg",   "sets": "3 × 12–15"},
    {"exercise": "Neutral-grip pulldown", "machine": "Lat pulldown / assisted pull-up", "start": "35–55 kg",   "sets": "3 × 8–12"},
    {"exercise": "Lateral raise",         "machine": "Lateral raise (drop set last)",   "start": "7.5–12.5 kg","sets": "3 × 12–15"},
    {"exercise": "Back extension",        "machine": "Back extension (add plate)",      "start": "BW–15 kg",   "sets": "3 × 12–15"},
    {"exercise": "Hanging knee raise",    "machine": "Captain's chair (or plank)",      "start": "bodyweight", "sets": "3 × 10–15"},
]

ROTATION = [("A", SESSION_A), ("B", SESSION_B), ("C", SESSION_C)]

WARMUP = "8–10 min easy cardio, then 1–2 lighter ramp-up sets of your first lift (these don't count)."
FINISHER = "Optional 10–20 min steady cardio (incline walk, bike, rower or pool laps)."
COOLDOWN = "5 min easy walking + stretch the muscles you trained."
ACTIVE_RECOVERY = "Easy 25–35 min walk or swim + light mobility. Keep it relaxed."
CARDIO_DAY = ("25–35 min steady cardio, **or** one short HIIT finisher: "
              "8–10 rounds of 30 s hard / 60 s easy on the bike or rower.")

GYM_WEEKDAYS = (1, 3, 5)  # Tue, Thu, Sat


def count_gym_days(start_monday: dt.date, end: dt.date) -> int:
    """Count Tue/Thu/Sat occurrences in [start_monday, end] inclusive."""
    if end < start_monday:
        return 0
    total = 0
    for wd in GYM_WEEKDAYS:
        delta = (wd - start_monday.weekday()) % 7
        first = start_monday + dt.timedelta(days=delta)
        if first > end:
            continue
        total += (end - first).days // 7 + 1
    return total


def get_day_plan(d: dt.date, start_monday: dt.date) -> dict:
    wd = d.weekday()
    if wd in (0, 4):  # Mon, Fri
        return {"type": "rest", "title": "Rest day",
                "note": "Full day off. Light mobility if you like."}
    if wd == 2:  # Wed
        return {"type": "recovery", "title": "Cardio / recovery", "note": CARDIO_DAY}
    if wd == 6:  # Sun
        return {"type": "recovery", "title": "Active recovery", "note": ACTIVE_RECOVERY}

    # Gym day: position in the A->B->C rotation
    n = count_gym_days(start_monday, d)         # 1-based count incl. today
    letter, exercises = ROTATION[(n - 1) % 3]
    return {"type": "gym", "title": f"Session {letter} — Full Body",
            "session": letter, "exercises": exercises}


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

if "data" not in st.session_state:
    st.session_state.data = load_data()
data = st.session_state.data

settings = data.setdefault("_settings", {})
default_start = settings.get("start_date", dt.date.today().isoformat())
start_date = dt.date.fromisoformat(default_start)
start_monday = start_date - dt.timedelta(days=start_date.weekday())

if "current_date" not in st.session_state:
    st.session_state.current_date = dt.date.today()

st.title("💪 ARC Gym Tracker")
st.caption("Intermediate full-body programme · Cockburn ARC")

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

if plan["type"] == "gym":
    st.success(f"**{plan['title']}**")
    with st.expander("Warm-up · finisher · cool-down · effort"):
        st.write(f"**Warm-up:** {WARMUP}")
        st.write(f"**Cardio finisher:** {FINISHER}")
        st.write(f"**Cool-down:** {COOLDOWN}")
        st.write("**Effort:** heavy 6–10s leave 1–2 reps in reserve (~2 min rest); "
                 "8–12s leave 1–2 (60–90 s rest); last isolation set can go to failure or drop-set.")
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
        st.success("Session complete — strong work! 🎉")

elif plan["type"] == "recovery":
    st.info(f"**{plan['title']}**")
    st.write(plan["note"])
    rec_done = st.checkbox("Done for today", value=day_record.get("done", False),
                           key=f"recovery|{date_iso}")
    day_record["done"] = rec_done
    if rec_done:
        st.success("Nice — that counts too. 👍")

else:  # rest
    st.warning(f"**{plan['title']}**")
    st.write(plan["note"])
    st.caption("No session scheduled. Rest and the deload are where you adapt.")

save_data(data)

with st.sidebar:
    st.header("This week")
    monday = d - dt.timedelta(days=d.weekday())
    for i in range(7):
        day = monday + dt.timedelta(days=i)
        p = get_day_plan(day, start_monday)
        if p["type"] == "gym":
            label = p["title"].split(" — ")[0]
        elif p["type"] == "recovery":
            label = p["title"]
        else:
            label = "Rest"
        marker = "→ " if day == d else "  "
        st.write(f"{marker}**{day.strftime('%a')}** · {label}")

    st.divider()
    st.header("Effort & weights")
    st.write(
        "Load guides are a rough orientation. The right weight is the one where "
        "your **last 1–2 reps are left in the tank** with clean form. If you're "
        "carrying over from before, keep your current weights and chase the new rep targets."
    )
    st.write(
        "**Progressing:** hit the top of the rep range on all sets two sessions "
        "running, then add load. **Deload** (halve sets, ~15% lighter) every 6–8 weeks."
    )

    st.divider()
    st.header("Settings")
    new_start = st.date_input("Programme start date", value=start_date, format="DD/MM/YYYY",
                              help="Sets where the A→B→C rotation begins. Snaps to that week's Monday.")
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

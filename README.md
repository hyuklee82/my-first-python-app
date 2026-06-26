# 💪 ARC Gym Tracker

A simple mobile-friendly web app to follow your Cockburn ARC intermediate programme
day by day, tick off each exercise, and log the weight you used.

Built with [Streamlit](https://streamlit.io) — pure Python, free to host, opens
in any phone browser.

---

## What it does

- Shows **today's plan** automatically (gym session, active recovery, or rest).
- Gym days list each machine (with its free-weight option) plus a **load guide** and **sets × reps**.
- **Tick a box** as you finish each exercise; a progress bar fills up.
- **Log the weight** you actually used in the box next to each exercise.
- Browse any date with **Prev / Today / Next** or the date picker.
- Sidebar shows the **week at a glance** plus the effort, weight and progression guidance.

The schedule runs on your Tuesday / Thursday / Saturday cycle, rotating the three
full-body sessions **A → B → C** on each gym visit, with Monday and Friday as rest days.

---

## Run it on your computer first (optional)

```bash
pip install -r requirements.txt
streamlit run app.py
```

It opens at `http://localhost:8501`.

---

## Deploy it free with GitHub + Streamlit Community Cloud

**1. Put the code on GitHub**

- Create a free account at [github.com](https://github.com) if you don't have one.
- Click **New repository**, name it e.g. `gym-tracker`, keep it Public, and create it.
- Upload these files (drag-and-drop works): `app.py`, `requirements.txt`,
  `.gitignore`, and the `.streamlit/config.toml` file (keep it inside a
  `.streamlit` folder). On GitHub's web uploader you can type `​.streamlit/config.toml`
  as the filename to create the folder.

**2. Deploy on Streamlit Community Cloud**

- Go to [share.streamlit.io](https://share.streamlit.io) and sign in **with GitHub**.
- Click **Create app → Deploy a public app from GitHub**.
- Pick your `gym-tracker` repo, branch `main`, and set the main file to `app.py`.
- Click **Deploy**. After a minute you'll get a public URL like
  `https://your-name-gym-tracker.streamlit.app`.

**3. Add it to your phone's home screen**

- Open the URL in your phone browser.
- **iPhone (Safari):** Share → *Add to Home Screen*.
- **Android (Chrome):** ⋮ menu → *Add to Home screen*.
- It now opens full-screen like a normal app.

---

## A note on saved ticks

Your ticks and weights are saved to a small file (`data/progress.json`) on the
server. This works while the app is running. **Streamlit's free Community Cloud
puts apps to sleep when idle and can reset that file on restart**, so your history
there isn't guaranteed to stick long-term.

For a personal daily tracker that's usually fine — you mainly care about *today*.
If you want ticks to persist permanently across devices, the easiest upgrade is
to store progress in the browser (the `streamlit-local-storage` package) or in a
small free database. Ask and that can be added.

---

## Customising

All the programme content lives at the top of `app.py` in the `SESSION_A`,
`SESSION_B`, warm-up, finisher and recovery variables. Change the exercises,
weights or text there and redeploy — Streamlit Cloud auto-updates when you push
to GitHub.

> This app is a training aid, not medical advice. Start light, prioritise form,
> and check with your GP before starting if you have any health concerns.

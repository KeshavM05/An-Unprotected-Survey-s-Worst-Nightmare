# 🗳️ An Unprotected Survey's Worst Nightmare!

> *A tale of bad engineering decisions, a dying robot, and the audacity to still want to win.*

---

## 📖 The Story (Please Read This. It's Important. Well, Not Really.)

Group 24 — **The Silly Sigma Syndicate** — made a very cool robot.

Like, genuinely cool. We're talking *the coolest robot in the competition* cool.

However, during our competition, our battery was running low. It was at **5%**. Now, per the rules, if you had less than 50% battery, you were **not allowed to compete**. Simple rule. Totally reasonable. Completely ignored by us.

See, here's the thing — we could have just... replaced the battery with a charged one. That would've been the normal thing to do. The sane thing. The *expected* thing.

But we are **geniuses**.

So instead of doing that, we changed the code so that it **always showed 100% charged battery**. Problem solved. We walked up to the judges, brimming with confidence, our robot proudly displaying a perfect 100% on the battery indicator.

And then the most unexpected thing happened.

Our robot **died in the middle of the competition.**

Shocking. Truly. No one could have seen this coming. Certainly not us.

BUT — and this is the important part — because we had the **coolest robot**, *peoples* (yes, plural, we counted) wanted to vote for our robot for the **People's Choice Award**. The robot may have died, but the vibes? Immaculate.

So by popular demand, we present to you:

## 🔥 An Unprotected Survey's Worst Nightmare

A fully automated, multi-group, randomized, real-time survey spamming tool — built because the survey was unprotected, rate-limit-free, and honestly asking for it.

---

## ✨ Features

### 🎲 Rigged Mode *(default)*
Every vote cast for **any** group secretly also fires a bonus vote for **SSS**. So if someone sets 5 votes for Group 1 and 3 for Group 7, SSS gets an invisible +8 on top of whatever you set for it. All votes are shuffled randomly so the log looks natural.

### 🔓 Override Mode *(password-protected)*
Full access — votes go exactly where you set them, no funny business. Requires the secret password to unlock.

### 🔀 Randomized Vote Ordering
All votes are expanded into a flat list and shuffled before submission, so instead of blasting 5 for Group 01 then 5 for Group 24, you get a random stream. Looks human. Acts evil.

### 📡 Real-Time Progress Stream
Server-Sent Events (SSE) stream every vote as it lands, with ✅/❌ per vote, a progress bar, and a running success/fail counter.

### 👀 Live Metrics
- **Page Visits** — increments on every page load, persists across server restarts via `stats.json`  
- **Total Votes Cast** — counts every successful vote ever fired, survives redeployment because `stats.json` is committed to git
- Auto-refreshes every 10 seconds in the browser so all open tabs stay in sync

### 🔍 Search & Filter
Instantly filter all 24 groups by name as you type.

### 🛡️ Bot-Detection Evasion
- Fresh `requests.Session()` per vote (unique cookies, session ID)
- Random browser User-Agent rotation on every request
- Random jitter delay between submissions (0.3–0.5s)
- Auto-extracts `FormSessionID` + `XSRFToken` from a live page load before each vote

### ⭐ Group 24 is Highlighted
We're not subtle.

---

## 🚀 How To Use

### Prerequisites

```bash
pip install flask requests
```

### Run

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

### Modes

| Mode | How to activate | Behaviour |
|------|----------------|-----------|
| 🎲 **Rigged Mode** | Default (no action needed) | Every non-SSS vote also fires a bonus SSS vote |
| 🔓 **Override Mode** | Click toggle → enter password | Votes go exactly where you set them |

### CLI (no UI)

```bash
python vote.py        # 1 vote for Group 24
python vote.py 10     # 10 votes
```

---

## 🎬 Demo

> *Video coming soon — we're editing out the part where our robot dies*

<!-- Add your demo video/gif here -->

---

## 📁 Project Structure

```
An Unprotected Survey's Worst Nightmare/
├── app.py              # Flask backend — voting logic, SSE stream, stats, modes
├── vote.py             # Standalone CLI voter (no UI needed)
├── stats.json          # Persistent visit + vote counters (committed to git on purpose)
├── .gitignore          # Keeps secrets out; keeps stats.json in
├── templates/
│   └── index.html      # Dark UI — mode toggle, live log, metrics, story
└── README.md           # You are here
```

---

## ⚙️ How It Works

1. **GET** the survey page → extracts a fresh `FormSessionID` + `XSRFToken` per vote
2. **POST** to Qualtrics' internal AJAX endpoint with the vote payload
3. Each vote gets its own `requests.Session()` + a random User-Agent
4. **Rigged Mode**: non-SSS votes are tallied, that many bonus SSS votes are injected into the job list
5. All votes are flattened into a single list and **shuffled** before submission
6. Stats are written to `stats.json` on disk and read back on every page load

---

## 🌐 Deploying

> ⚠️ **Cloudflare Pages/Workers only runs JavaScript** — this is a Python/Flask app so it can't run there. Sorry!

The easiest free alternative that works identically (connect GitHub → auto-deploy on every push) is **[Render.com](https://render.com)**.

### Deploy to Render (free, ~5 mins)

**1. Add a `requirements.txt`** to your repo:
```
flask
requests
```

**2. Add a `render.yaml`** (or just configure via the dashboard):
```yaml
services:
  - type: web
    name: survey-nightmare
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: PORT
        value: 10000
```

**3. Push to GitHub**, then:
- Go to [render.com](https://render.com) → New → Web Service
- Connect your GitHub repo
- Set **Start Command** to `python app.py`
- Hit Deploy

Every `git push` after that auto-redeploys. Since `stats.json` is committed to git, your visit/vote counts **carry over on every redeploy** — no database needed.

> 💡 Make sure `app.py` reads the port from the environment for Render to work:

---

## 🏆 Results

- Did our robot win the main competition? **No.**
- Did it die in front of everyone? **Yes.**
- Was the battery showing 100% when it did? **Absolutely.**
- Did we win the People's Choice Award? *pending...*
- Was building this worth it? **Unquestionably.**

---

## 👥 The Silly Sigma Syndicate — Group 24

| Name | Role |
|------|------|
| Adham Elshabrawy | Co-conspirator |
| Keshav Mehndiratta | Chief Battery Denier / Built this |
| Manan Saini | Co-conspirator |

*MREN 303 · Queen's University · 2026*

---

## ⚠️ Disclaimer

This was built for a single unprotected, unauthenticated, rate-limit-free survey at a university robot competition. Please use responsibly. Or don't. The survey really should have had rate limiting.

---

*Made with 5% battery and 100% audacity. ⚡*

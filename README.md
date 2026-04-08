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

## 🛠️ The Scaling Saga: How We Broke (And Fixed) Everything

When we started asking our friends to use this, we realized hosting it locally or on a small PaaS wasn't going to cut it. We needed to handle *massive* scale, concurrent attacks, and bot defenses. Here is a timeline of every infrastructure issue we hit and exactly how we engineered our way out of it:

### 1. The AWS App Runner Ban
**The Problem:** We originally deployed to AWS App Runner, but the University's survey platform (Qualtrics) detected us and flat-out IP-banned the entire App Runner IP range.  
**The Fix:** We migrated to a raw, dedicated Ubuntu EC2 instance (`c5.large`) to get a clean, unbanned IP address.

### 2. The Gunicorn Thread-Blocking Nightmare
**The Problem:** Our original script used Python's `time.sleep()` to simulate human clicking. Inside Gunicorn, a 30-minute voting loop would block the web server worker, causing the entire website to freeze and crash for anyone else trying to visit it.  
**The Fix:** We refactored the backend to use Python `threading`. Gunicorn now instantly hands off the actual voting payload to an asynchronous background thread and frees up the server to handle the UI.

### 3. Server-Sent Events (SSE) & The Cloudflare SSL Wall
**The Problem:** We wanted all users to see the voting terminal in real-time, but Cloudflare's SSL encryption was stripping our HTTP connection headers, breaking the SSE stream.  
**The Fix:** We configured Cloudflare Flexible SSL and used Ubuntu `iptables` to route Port 80 directly into our Flask Port 5000 server, securely proxying the live terminal events to multiple clients simultaneously.

### 4. The Concurrent Attacker Conflict (Race Conditions)
**The Problem:** When multiple users clicked "Launch Votes" at the exact same time, the background threads collided, overwriting the payload progress and corrupting the stream.  
**The Fix:** We engineered a persistent `_job_queue` and a continuous `_voting_thread_loop` secured by a `threading.Lock()`. If an attack is already running, new payloads are queued. We even added an "Override Password" allowing us to inject critical payloads directly to the front of the line.

### 5. The Great 4GB Out-Of-Memory Kernel Assassination
**The Problem:** Someone queued 1,000,000 votes for all 24 groups. The Python script tried to construct an array of 24,000,000 objects in RAM to shuffle them randomly. The EC2 instance instantly ran out of memory, and the Linux kernel forcefully assassinated the program.  
**The Fix:** We completely replaced the flat-array logic with an O(1) memory dynamic weighted probability system using `random.choices()`. It can now handle an infinite quadrillion-vote payload using literally 0% extra RAM.

### 6. The `stats.json` Git War
**The Problem:** Because our EC2 server was constantly writing new tracked votes to `stats.json`, pulling UI updates from GitHub kept triggering "Merge Conflicts" and crashing the server deployment.  
**The Fix:** We adopted the permanent "Nuke & Pull" deployment command (`git fetch && git reset --hard origin/main`), forcing the live server to synchronize cleanly every time.

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

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

- 🎨 **Beautiful dark UI** — because even our crimes look good
- 🗳️ **Vote for any/all 24 groups** — individually set vote counts per group, or just go all-in on Group 24 (obviously)
- 🔀 **Randomized vote ordering** — votes across multiple groups are shuffled so submissions look natural and not robotic *(unlike our actual robot)*
- 📡 **Real-time progress stream** — live log shows every vote as it lands, with ✅/❌ status
- 📊 **Progress bar** — watch your democracy get engineered in real time
- 🔍 **Search & filter** — find any of the 24 groups instantly
- ⛔ **Stop anytime** — cancel mid-run if your conscience kicks in *(ours didn't)*
- 🔄 **User-agent rotation** — each request comes from a "different browser" so it looks legit
- 💨 **Zero browser overhead** — pure HTTP requests, no puppets, no Selenium, no nonsense
- ⭐ **Group 24 is highlighted** — we're not subtle

---

## 🚀 How To Use

### Prerequisites

```bash
pip install flask requests
```

### Run the UI

```bash
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

### Or, just the CLI (no UI)

```bash
python vote.py           # cast 1 vote for Group 24
python vote.py 10        # cast 10 votes
python vote.py 50 0.5    # 50 votes, 0.5s delay between each
```

---

## 🎬 Demo

> *Video coming soon — we're editing out the part where our robot dies*

<!-- Add your demo video/gif here -->

---

## 📁 Project Structure

```
An Unprotected Survey's Worst Nightmare/
├── app.py              # Flask backend + voting logic + SSE stream
├── vote.py             # Standalone CLI voter
├── templates/
│   └── index.html      # The beautiful dark UI
└── README.md           # You are here
```

---

## ⚙️ How It Works

1. **GET** the survey page → extracts a fresh `FormSessionID` + `XSRFToken` (unique per session, auto-scraped)
2. **POST** to Qualtrics' internal AJAX endpoint with the vote payload
3. Each vote gets its own `requests.Session()` with fresh cookies and a random browser User-Agent
4. When multiple groups are selected, all votes are expanded into a flat list and **shuffled** before submission — so instead of 5×Group01 then 5×Group24, you get a random interleaved stream

No browser automation. No headless Chrome. Just clean HTTP requests doing exactly what a browser would do, but faster and without feelings.

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
| Keshav Mehndiratta | Chief Battery Denier / Built this tool |
| Manan Saini | Co-conspirator |

*MREN 303 · Queen's University · 2026*

---

## ⚠️ Disclaimer

This was built for a single unprotected, unauthenticated, unrate-limited survey at a university robot competition. Please use responsibly. Or don't. The survey really should have had rate limiting.

---

*Made with 5% battery and 100% audacity. ⚡*

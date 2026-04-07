"""
Survey Spammer - Flask Backend
Serves the UI and handles vote submission with real-time SSE progress.
"""

import hashlib
import json
import os
import queue
import random
import re
import threading
import time

import requests
from flask import Flask, Response, jsonify, render_template, request

app = Flask(__name__)

SURVEY_URL = "https://queensu.qualtrics.com/jfe/form/SV_0BUYnyF2ObMD9zg"
SURVEY_ID  = "SV_0BUYnyF2ObMD9zg"
QUESTION_ID = "QID1"
SSS_CHOICE_ID = "24"                    # Silly Sigma Syndicate
SSS_LABEL     = "Group 24 — SillySigmaSyndicate ⭐"

# Passwords stored as SHA-256 hashes — plaintext never lives in code.
# Input is lowercased before hashing, so it's fully case-insensitive.
OVERRIDE_PASSWORD_HASHES = {
    "120f6e5b4ea32f65bda68452fcfaaef06b0136e1d0e4a6f60bc3771fa0936dd6",
    "08a841e996781e9e77d30a4e4420a8f501a280b00624e6d1224bf54aaff73eba",
}

def check_password(password: str) -> bool:
    return hashlib.sha256(password.strip().lower().encode()).hexdigest() in OVERRIDE_PASSWORD_HASHES

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
]

# Hard-coded choices from the survey (scraped once; won't change mid-contest)
SURVEY_CHOICES = [
    {"id": "1",  "label": "Group 01 — 1",                    "display": "Michael Cassidy, Michael De Miglio, Cole Jowett"},
    {"id": "2",  "label": "Group 02 — The Chuds",            "display": "Daniel Buzan, Noah Lafferty, Vickram Yalousakis"},
    {"id": "3",  "label": "Group 03 — IslandBoyz",           "display": "Yu-Han Chiu, Liam Lorentz, Ethan Powell"},
    {"id": "4",  "label": "Group 04 — Colonizer",            "display": "Mohammed Faizy, Oswin Ning, John Zhong"},
    {"id": "5",  "label": "Group 05 — TheImmigrants",        "display": "Harrison Adoga, Abresham Taklukder"},
    {"id": "6",  "label": "Group 06 — UnbeatableInc",        "display": "Stefano Esposto, Parth Thusoo"},
    {"id": "7",  "label": "Group 07 — FaZe Clan",            "display": "Alex Mcaulay, Sebastian Reinders, Evan Vermeiren"},
    {"id": "8",  "label": "Group 08 — TheKirkifiers",        "display": "Saad Nauman, Paneet Punia, Alex Zhou"},
    {"id": "9",  "label": "Group 09 — HatTrick",             "display": "Noah Doeschner-Fretts, Ian Schaffer, Jamieson Strain"},
    {"id": "10", "label": "Group 10 — Ben 10",               "display": "Alex Pettipiece, Mariana Siqueira, Vagish Vaibhav"},
    {"id": "11", "label": "Group 11 — Group 11",             "display": "Max Braunstein, Tomas Frynta, Cara Hicks"},
    {"id": "12", "label": "Group 12 — Blank",                "display": "Amir Abdur-Rahim, Utomobong Essien, Ayo Ososami"},
    {"id": "13", "label": "Group 13 — APOLLO-13",            "display": "Xan Giuliani, Laith Mkarem, Peter Tennant"},
    {"id": "14", "label": "Group 14 — The Germans",          "display": "Tomas Dirube, Marlow Gaddes, Maxwell Sloan"},
    {"id": "15", "label": "Group 15 — The Wrong Brothers",   "display": "David Colaco, Oliver Lynn"},
    {"id": "16", "label": "Group 16 — BUZZARDS",             "display": "Amarachukwu Akagha, Aidan Lemke, Fin Roberts"},
    {"id": "17", "label": "Group 17 — Inverse Kirkematics",  "display": "Evan Applebaum, Seth Inman, Sebastian Yepes"},
    {"id": "18", "label": "Group 18 — TBD",                  "display": "Claire Ferguson, Noah Lorber, Mikaela Matias"},
    {"id": "19", "label": "Group 19 — Bubatron Mk Greer",    "display": "Aidan Greer, Balazs Peterdy, Mark Poretski"},
    {"id": "20", "label": "Group 20 — GhostBusters",         "display": "Graham Butterworth, Nishith Chowdary Navuri, Sebastien Sauter"},
    {"id": "21", "label": "Group 21 — Anti-Cow Collectors",  "display": "Nadia Animashaun, Chloe Columbus, Emily Ferraioli"},
    {"id": "22", "label": "Group 22 — Atlas",                "display": "Kayla Epstein, Ethan Milburn, Natalie Skinner"},
    {"id": "23", "label": "Group 23 — Maxim Maxers",         "display": "Benjamin Cox, Trenton Franklin"},
    {"id": "24", "label": "Group 24 — SillySigmaSyndicate ⭐","display": "Adham Elshabrawy, Keshav Mehndiratta, Manan Saini"},
]

# ── Multi-client SSE broadcast ────────────────────────────────────────────────
_sse_clients: list[queue.Queue] = []          # one queue per connected tab
_sse_clients_lock = threading.Lock()
_vote_log: list[str] = []                     # replay buffer for new tabs
_current_state: dict = {}                     # latest progress snapshot
_voting_active = False
_job_queue: list[dict] = []                   # queue of voting jobs
_queue_lock = threading.Lock()
MAX_LOG_HISTORY = 100


def _broadcast(event: str, data: dict):
    """Push an SSE event to every connected client and store it for replay."""
    global _vote_log, _current_state
    msg = f"event: {event}\ndata: {json.dumps(data)}\n\n"

    # Update replay state
    if event == "start":
        _vote_log = [msg]           # fresh log for new run
        _current_state = data
    elif event in ("progress", "done", "stopped"):
        _vote_log.append(msg)
        if len(_vote_log) > MAX_LOG_HISTORY:
            _vote_log.pop(0)
        _current_state = data

    # Send to all connected tabs
    with _sse_clients_lock:
        for q in list(_sse_clients):
            try:
                q.put_nowait(msg)
            except Exception:
                pass

# ─────────────────────────────────────────────────────────────────────────────
# Persistent stats (stats.json)
# ─────────────────────────────────────────────────────────────────────────────

STATS_FILE = os.path.join(os.path.dirname(__file__), "stats.json")
_stats_lock = threading.Lock()


def _load_stats() -> dict:
    try:
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"visits": 0, "total_votes": 0}


def _save_stats(stats: dict):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)


def _increment_stat(key: str, by: int = 1) -> dict:
    """Thread-safe increment of a stat key. Returns updated stats."""
    with _stats_lock:
        stats = _load_stats()
        stats[key] = stats.get(key, 0) + by
        _save_stats(stats)
        return stats


# ─────────────────────────────────────────────────────────────────────────────
# Voting logic
# ─────────────────────────────────────────────────────────────────────────────

def _single_vote(choice_id: str) -> bool:
    session = requests.Session()
    ua = random.choice(USER_AGENTS)

    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://queensu.qualtrics.com/",
    }

    try:
        resp = session.get(SURVEY_URL, headers=headers, params={"Q_CHL": "qr"}, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        return False

    # Extract XSRF token
    xsrf_token = None
    for pattern in [
        r'"Token"\s*:\s*"([^"]+)"',
        r'XSRFToken["\s:]+["\']([A-Za-z0-9_\-]+)["\']',
        r'"XSRFToken":"([^"]+)"',
    ]:
        m = re.search(pattern, resp.text)
        if m:
            xsrf_token = m.group(1)
            break
    if not xsrf_token:
        for cookie in session.cookies:
            if "xsrf" in cookie.name.lower() or "csrf" in cookie.name.lower():
                xsrf_token = cookie.value
                break

    # Extract FormSessionID
    fsid = None
    for pattern in [r'"FormSessionID"\s*:\s*"([^"]+)"', r'FS_[A-Za-z0-9]+']:
        m = re.search(pattern, resp.text)
        if m:
            fsid = m.group(1) if '"FormSessionID"' in pattern else m.group(0)
            break

    if not fsid:
        return False

    post_url = f"https://queensu.qualtrics.com/jfe6/form/{SURVEY_ID}/next"
    params = {"rand": random.random(), "tid": "1", "t": int(time.time() * 1000), "fs": fsid}
    payload = {
        "SurveyID": SURVEY_ID,
        "FormSessionID": fsid,
        "XSRFToken": xsrf_token,
        "Request": "JavascriptForm",
        "NextButton": "",
        "QuestionInfo": {QUESTION_ID: {"QuestionType": "MC", "Answers": {choice_id: "1"}}},
    }
    post_headers = {
        "User-Agent": ua,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "X-XSRF-TOKEN": xsrf_token or "",
        "Referer": f"{SURVEY_URL}?Q_CHL=qr",
        "Origin": "https://queensu.qualtrics.com",
    }

    try:
        r = session.post(post_url, params=params, json=payload, headers=post_headers, timeout=10)
        return r.status_code == 200
    except Exception:
        return False


def _run_votes(jobs: list[dict]):
    """jobs = [{"choice_id": "24", "label": "Group 24 ...", "count": 5}, ...]

    All votes are expanded into a flat list and shuffled before submission,
    so entries for different groups are interleaved randomly rather than
    submitted in a block-per-group order.
    """
    global _voting_active

    # Build a flat, shuffled list of every individual vote to cast
    flat: list[dict] = []
    for job in jobs:
        for _ in range(job["count"]):
            flat.append({"choice_id": job["choice_id"], "label": job["label"]})
    random.shuffle(flat)

    total   = len(flat)
    done    = 0
    success = 0

    def emit(event: str, data: dict):
        _broadcast(event, data)

    emit("start", {"total": total})

    for i, item in enumerate(flat):
        if not _voting_active:
            emit("stopped", {"done": done, "success": success})
            return

        ok = _single_vote(item["choice_id"])
        done += 1
        if ok:
            success += 1
            _increment_stat("total_votes")

        emit("progress", {
            "done": done,
            "total": total,
            "success": success,
            "label": item["label"],
            "vote_num": done,
            "vote_total": total,
            "ok": ok,
        })

        if i < total - 1:
            time.sleep(0.3 + random.uniform(0, 0.2))

    emit("done", {"done": done, "total": total, "success": success})

def _voting_thread_loop():
    global _voting_active
    while True:
        with _queue_lock:
            if not _job_queue:
                _voting_active = False
                break
            # Pop the next batch of jobs from the front of the queue
            jobs = _job_queue.pop(0)

        _voting_active = True
        _run_votes(jobs)

# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    stats = _increment_stat("visits")
    return render_template("index.html", choices=SURVEY_CHOICES, stats=stats)


@app.route("/api/choices")
def api_choices():
    return jsonify(SURVEY_CHOICES)


@app.route("/api/stats")
def api_stats():
    with _stats_lock:
        return jsonify(_load_stats())


@app.route("/api/vote", methods=["POST"])
def api_vote():
    global _voting_active
    data = request.json
    mode = data.get("mode", "rigged")  # "rigged" | "override"
    queue_action = data.get("queue_action", "end") # "end" | "front"

    # Override mode requires the secret password
    if mode == "override" or queue_action == "front":
        if not check_password(data.get("password", "")):
            return jsonify({"error": "Wrong password. Nice try."}), 403

    jobs = [j for j in data.get("jobs", []) if j.get("count", 0) > 0]
    if not jobs:
        return jsonify({"error": "No votes to cast"}), 400

    # ── Rigged Mode: every vote for a non-SSS group also adds a bonus SSS vote
    if mode == "rigged":
        bonus = sum(j["count"] for j in jobs if j["choice_id"] != SSS_CHOICE_ID)
        if bonus > 0:
            sss = next((j for j in jobs if j["choice_id"] == SSS_CHOICE_ID), None)
            if sss:
                sss["count"] += bonus
            else:
                jobs.append({"choice_id": SSS_CHOICE_ID, "label": SSS_LABEL, "count": bonus})

    with _queue_lock:
        if queue_action == "front":
            _job_queue.insert(0, jobs)
        else:
            _job_queue.append(jobs)

        if not _voting_active:
            _voting_active = True
            threading.Thread(target=_voting_thread_loop, daemon=True).start()

    # Alert clients that queue size changed
    _broadcast("queue_update", {"queue_size": len(_job_queue)})
    return jsonify({"ok": True, "mode": mode, "queue_action": queue_action})


@app.route("/api/stop", methods=["POST"])
def api_stop():
    global _voting_active
    with _queue_lock:
        _job_queue.clear()
        _broadcast("queue_update", {"queue_size": 0})
    _voting_active = False
    return jsonify({"ok": True})


@app.route("/api/status")
def api_status():
    """Lets new tabs check if voting is in progress and get current state."""
    with _queue_lock:
        q_size = len(_job_queue)
    return jsonify({
        "active": _voting_active,
        "state": _current_state,
        "log_count": len(_vote_log),
        "queue_size": q_size,
    })


@app.route("/api/stream")
def api_stream():
    client_q: queue.Queue = queue.Queue()

    def generate():
        # Register this client and replay current log so they're caught up
        with _sse_clients_lock:
            replay = list(_vote_log)          # snapshot before registering
            _sse_clients.append(client_q)

        # Send replay burst
        for msg in replay:
            yield msg

        # Then stream live events as they come
        try:
            while True:
                try:
                    msg = client_q.get(timeout=30)
                    yield msg
                except queue.Empty:
                    yield "event: ping\ndata: {}\n\n"
        finally:
            with _sse_clients_lock:
                try:
                    _sse_clients.remove(client_q)
                except ValueError:
                    pass

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🗳️  Survey Spammer UI  →  http://127.0.0.1:{port}")
    app.run(debug=False, host="0.0.0.0", port=port, threaded=True)

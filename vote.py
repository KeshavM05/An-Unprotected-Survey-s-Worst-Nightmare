"""
Qualtrics Survey Auto-Voter
Automatically submits votes for Group 24 SillySigmaSyndicate
by mimicking the browser's AJAX flow with a fresh session per vote.

Usage:
  python vote.py            → 1 vote
  python vote.py 10         → 10 votes
  python vote.py 10 0.5     → 10 votes, 0.5s delay between each
"""

import requests
import re
import json
import time
import random
import sys

SURVEY_URL = "https://queensu.qualtrics.com/jfe/form/SV_0BUYnyF2ObMD9zg"
SURVEY_ID = "SV_0BUYnyF2ObMD9zg"
CHOICE_FOR_GROUP_24 = "24"
QUESTION_ID = "QID1"

# A pool of user agents to rotate through so requests look more varied
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
]


def vote(vote_num=1):
    session = requests.Session()
    ua = random.choice(USER_AGENTS)

    # --- Step 1: GET the survey page to collect cookies & session tokens ---
    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://queensu.qualtrics.com/",
    }

    resp = session.get(SURVEY_URL, headers=headers, params={"Q_CHL": "qr"})
    resp.raise_for_status()

    # --- Step 2: Extract the XSRF token ---
    xsrf_token = None

    meta_match = re.search(r'<meta[^>]+name=["\']QSF-CSRFToken["\'][^>]+content=["\']([^"\']+)["\']', resp.text)
    if meta_match:
        xsrf_token = meta_match.group(1)

    if not xsrf_token:
        js_match = re.search(r'"Token"\s*:\s*"([^"]+)"', resp.text)
        if js_match:
            xsrf_token = js_match.group(1)

    if not xsrf_token:
        js_match2 = re.search(r'XSRFToken["\s:]+["\']([A-Za-z0-9_\-]+)["\']', resp.text)
        if js_match2:
            xsrf_token = js_match2.group(1)

    if not xsrf_token:
        for cookie in session.cookies:
            if "xsrf" in cookie.name.lower() or "csrf" in cookie.name.lower():
                xsrf_token = cookie.value
                break

    # --- Step 3: Extract FormSessionID (FSID) ---
    fsid = None
    fsid_match = re.search(r'"FormSessionID"\s*:\s*"([^"]+)"', resp.text)
    if fsid_match:
        fsid = fsid_match.group(1)

    if not fsid:
        fsid_match2 = re.search(r'FS_[A-Za-z0-9]+', resp.text)
        if fsid_match2:
            fsid = fsid_match2.group(0)

    if not fsid:
        print(f"  [Vote {vote_num}] ❌ Could not extract FormSessionID")
        return False

    # --- Step 4: Build and send the POST ---
    rand_val = random.random()
    timestamp = int(time.time() * 1000)

    post_url = f"https://queensu.qualtrics.com/jfe6/form/{SURVEY_ID}/next"
    params = {
        "rand": rand_val,
        "tid": "1",
        "t": timestamp,
        "fs": fsid,
    }

    payload = {
        "SurveyID": SURVEY_ID,
        "FormSessionID": fsid,
        "XSRFToken": xsrf_token,
        "Request": "JavascriptForm",
        "NextButton": "",
        "QuestionInfo": {
            QUESTION_ID: {
                "QuestionType": "MC",
                "Answers": {CHOICE_FOR_GROUP_24: "1"},
            }
        },
    }

    post_headers = {
        "User-Agent": ua,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "X-XSRF-TOKEN": xsrf_token or "",
        "Referer": f"{SURVEY_URL}?Q_CHL=qr",
        "Origin": "https://queensu.qualtrics.com",
    }

    post_resp = session.post(post_url, params=params, json=payload, headers=post_headers)

    if post_resp.status_code == 200:
        return True
    else:
        print(f"  [Vote {vote_num}] ❌ HTTP {post_resp.status_code}")
        return False


def main():
    n_votes = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    delay   = float(sys.argv[2]) if len(sys.argv) > 2 else 0.3

    print(f"🗳️  Survey Auto-Voter — Group 24 SillySigmaSyndicate")
    print(f"   Votes to cast : {n_votes}")
    print(f"   Delay between : {delay}s")
    print("─" * 45)

    success = 0
    failed  = 0

    for i in range(1, n_votes + 1):
        ok = vote(i)
        if ok:
            success += 1
            print(f"  [Vote {i:>3}/{n_votes}] ✅ Submitted")
        else:
            failed += 1
            print(f"  [Vote {i:>3}/{n_votes}] ❌ Failed")

        if i < n_votes:
            time.sleep(delay + random.uniform(0, 0.2))  # small jitter

    print("─" * 45)
    print(f"✅ Success: {success}  |  ❌ Failed: {failed}")


if __name__ == "__main__":
    main()

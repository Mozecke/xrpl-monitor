#!/usr/bin/env python3
# monitor.py - XRPL integration watcher (Telegram alerts, GitHub Actions ready)

import requests, time, json, os
from bs4 import BeautifulSoup
from datetime import datetime

# Read secrets from environment (set in GitHub → Settings → Secrets → Actions)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")

# Pages to monitor
PAGES = {
    "Ripple News": "https://ripple.com/insights/",
    "XRPL Foundation Blog": "https://xrpl.org/blog/",
    "Circle Blog": "https://www.circle.com/en/blog",
    "Tether Blog": "https://tether.to/en/news/",
    "XRPLF GitHub": "https://github.com/XRPLF",
}

# Keywords to trigger alerts
KEYWORDS = [
    "usdc", "usdt", "stablecoin", "rlusd", "xsgd",
    "integration", "sidechain", "euro", "eur", "tokenize", "tokenization"
]

SEEN_FILE = "seen.json"
HEADERS = {"User-Agent": "xrpl-monitor/1.0"}
SLEEP_SECONDS = 1   # 1 sec (GitHub Actions runs once per job, no need to loop)

def send_telegram(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Missing Telegram config")
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
        r = requests.post(url, data=payload, timeout=15)
        return r.status_code == 200
    except Exception as e:
        print("Telegram error:", e)
        return False

def load_seen():
    try:
        with open(SEEN_FILE,"r") as f:
            return json.load(f)
    except:
        return {}

def save_seen(d):
    with open(SEEN_FILE,"w") as f:
        json.dump(d, f)

def find_matches(url, html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True).lower()
    matches = [k for k in KEYWORDS if k in text]
    titles = []
    for tag in soup.find_all(["h1","h2","h3","a"]):
        t = (tag.get_text() or "").strip()
        if not t: continue
        low = t.lower()
        for k in KEYWORDS:
            if k in low:
                link = tag.get("href") if tag.name=="a" else None
                titles.append({"title":t, "link": link})
                break
    return matches, titles

def fetch(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            return r.text
        else:
            print("Fetch failed:", url, r.status_code)
            return ""
    except Exception as e:
        print("Fetch exception:", e)
        return ""

def main():
    seen = load_seen()
    for name, url in PAGES.items():
        html = fetch(url)
        if not html:
            continue
        matches, titles = find_matches(url, html)
        if matches:
            marker = f"{name}:{url}"
            text_hash = str(hash(html))
            prev = seen.get(marker)
            if prev != text_hash:
                seen[marker] = text_hash
                save_seen(seen)
                now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                summary = f"🚨 <b>{name}</b>\n{url}\nKeywords: {', '.join(matches)}\nTime: {now}\n"
                if titles:
                    for t in titles[:3]:
                        linkpart = f" — {t['link']}" if t.get('link') else ""
                        summary += f"\n• {t['title']}{linkpart}"
                send_telegram(summary)
                print("Alert sent for", name)

if __name__ == "__main__":
    from datetime import datetime
    now = datetime.utcnow()
    # Send heartbeat once per day at 00:00 UTC
    if now.hour == 0 and now.minute < 10:
        send_telegram("✅ XRPL Monitor is alive and checking every 10 minutes.")
    main()


#!/usr/bin/env python3
"""
ARDOT Consulting — Website Uptime Monitor

Checks critical URLs every 5 minutes. Sends a Telegram alert if any are down.
No Docker needed — runs as a no-agent Hermes cron job.

Silent when everything's up (empty stdout = no message sent).
Non-empty stdout = alert delivered to the chat.
"""

import urllib.request
import json
import sys
from datetime import datetime, timezone

# URLs to monitor
URLS = [
    ("Homepage", "https://www.ardotconsulting.com/"),
    ("Blog", "https://www.ardotconsulting.com/blog/"),
    ("RSS Feed", "https://www.ardotconsulting.com/feed.xml"),
    ("Sitemap", "https://www.ardotconsulting.com/sitemap.xml"),
    ("robots.txt", "https://www.ardotconsulting.com/robots.txt"),
    ("OG Image", "https://www.ardotconsulting.com/og-image.png"),
]

# Telegram config (from env or .env file)
def get_telegram_config():
    import os
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not bot_token:
        try:
            with open("/opt/data/.env") as f:
                for line in f:
                    if line.startswith("TELEGRAM_BOT_TOKEN="):
                        bot_token = line.split("=", 1)[1].strip()
                    elif line.startswith("TELEGRAM_CHAT_ID="):
                        chat_id = line.split("=", 1)[1].strip()
        except:
            pass
    
    return bot_token, chat_id

def send_telegram(message, bot_token, chat_id):
    """Send alert to Telegram chat."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = json.dumps({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False

def check_url(name, url):
    """Check if a URL responds with 200. Returns (ok, status_code, error)."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ARDOT-Uptime-Monitor/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 200:
                return True, 200, None
            else:
                return False, resp.status, f"HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        return False, e.code, f"HTTP {e.code}"
    except Exception as e:
        return False, 0, str(e)[:100]

def main():
    bot_token, chat_id = get_telegram_config()
    
    failures = []
    for name, url in URLS:
        ok, status, error = check_url(name, url)
        if not ok:
            failures.append(f"❌ *{name}* — {url}\n   Status: {status}, Error: {error}")
    
    if failures:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        message = f"⚠️ *ARDOT Uptime Alert*\n\n{timestamp}\n\n" + "\n".join(failures)
        
        if bot_token and chat_id:
            sent = send_telegram(message, bot_token, chat_id)
            if sent:
                print(message)  # Delivered to chat
            else:
                print(f"{message}\n\n⚠️ Telegram delivery failed — check bot token and chat ID")
        else:
            print(f"{message}\n\n⚠️ No Telegram config found")
    
    # Silent on success — empty stdout means no message sent
    # Log to file
    try:
        import os
        os.makedirs("/opt/data/logs", exist_ok=True)
        with open("/opt/data/logs/uptime-monitor.log", "a") as f:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            if failures:
                f.write(f"{timestamp} FAIL: {len(failures)} endpoints down\n")
            else:
                f.write(f"{timestamp} OK: all {len(URLS)} endpoints up\n")
    except:
        pass

if __name__ == "__main__":
    main()
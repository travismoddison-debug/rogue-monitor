"""
Rogue River Permit Monitor
Checks the BLM float permit page and texts you when May 29 has 4+ spaces.
"""

import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# ── CONFIG ───────────────────────────────────────────────────────────────────────

PHONE_NUMBER       = "8055888452"
GMAIL_ADDRESS      = "travis.moddison@gmail.com"
GMAIL_APP_PASSWORD = "glfw ndwb saik dbce"

TARGET_MONTH    = "May"
TARGET_DATE_NUM = "29"
TARGET_DAY_NAME = "Fri"
MIN_SPACES      = 4

# ── CONSTANTS ────────────────────────────────────────────────────────────────────

URL         = "https://www.blm.gov/or/resources/recreation/rogue/rogue_river.php"
SMS_GATEWAY = f"{PHONE_NUMBER}@vtext.com"

# ── CORE LOGIC ───────────────────────────────────────────────────────────────────

def send_sms(body: str):
    msg = MIMEText(body)
    msg["Subject"] = "Rogue River Permit Alert"
    msg["From"]    = GMAIL_ADDRESS
    msg["To"]      = SMS_GATEWAY

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, SMS_GATEWAY, msg.as_string())

    print(f"[{now()}] SMS sent!")


def check_permits():
    print(f"[{now()}] Checking BLM permit page...")

    try:
        resp = requests.get(URL, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
    except Exception as e:
        print(f"[{now()}] ERROR fetching page: {e}")
        return

    soup = BeautifulSoup(resp.text, "html.parser")
    tables = soup.find_all("table")

    for table in tables:
        first_cell = table.find("td") or table.find("th")
        if not first_cell or TARGET_MONTH not in first_cell.get_text():
            continue

        for row in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cells) < 3:
                continue

            day_col, date_col, spaces_col = cells[0], cells[1], cells[2]

            if TARGET_DAY_NAME.lower() not in day_col.lower():
                continue
            if TARGET_DATE_NUM not in date_col:
                continue

            try:
                spaces = int(spaces_col)
            except ValueError:
                print(f"[{now()}] Found May 29 row but couldn't parse spaces: '{spaces_col}'")
                return

            if spaces >= MIN_SPACES:
                msg = (
                    f"ROGUE PERMIT OPEN!\n"
                    f"Fri May 29: {spaces} spaces available\n"
                    f"Book now: {URL}"
                )
                print(f"[{now()}] MATCH — {spaces} spaces! Sending SMS...")
                send_sms(msg)
            else:
                print(f"[{now()}] May 29 found but only {spaces} space(s) — need {MIN_SPACES}.")
            return

        print(f"[{now()}] May table found — no Fri 29 row yet.")
        return

    print(f"[{now()}] Could not find May table on page.")


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    check_permits()

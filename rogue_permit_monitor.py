import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

PHONE_NUMBER       = "8055888452"
GMAIL_ADDRESS      = "travis.moddison@gmail.com"
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "glfw ndwb saik dbce")

TARGET_MONTH    = "May"
TARGET_DATE_NUM = "29"
TARGET_DAY_NAME = "Fri"
MIN_SPACES      = 4

URL         = "https://www.blm.gov/or/resources/recreation/rogue/rogue_river.php"
SMS_GATEWAY = f"{PHONE_NUMBER}@vtext.com"


def send_sms(body):
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
        print(f"[{now()}] ERROR: {e}")
        return

    soup = BeautifulSoup(resp.text, "html.parser")
    for table in soup.find_all("table"):
        if TARGET_MONTH not in table.get_text():
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
                print(f"[{now()}] Couldn't parse spaces: '{spaces_col}'")
                return
            if spaces >= MIN_SPACES:
                send_sms(f"ROGUE PERMIT OPEN!\nFri May 29: {spaces} spaces\nBook now: {URL}")
            else:
                print(f"[{now()}] May 29 found — only {spaces} space(s), need {MIN_SPACES}.")
            return
        print(f"[{now()}] May table found — no Fri 29 row yet.")
        return

    print(f"[{now()}] May table not found on page.")


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    check_permits()

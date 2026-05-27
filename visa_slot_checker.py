import time
import requests
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from seleniumbase import Driver


# ---------------- CONFIG ----------------
URL = "https://checkvisaslots.com/latest-us-visa-availability/h-1b-regular/"

ALERT_THRESHOLD_MINUTES = 1
REFRESH_INTERVAL = 30


# ---------------- TELEGRAM ----------------
ENABLE_TELEGRAM = False
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"


# ---------------- PUSHOVER ----------------
ENABLE_PUSHOVER = False
PUSHOVER_TOKEN = "YOUR_PUSHOVER_TOKEN"
PUSHOVER_USER = "YOUR_PUSHOVER_USER_KEY"


def send_telegram_message(message: str):
    if not ENABLE_TELEGRAM:
        return

    try:
        api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        requests.post(
            api_url,
            data={
                "chat_id": CHAT_ID,
                "text": message
            }
        )

        print("Telegram alert sent")

    except Exception as e:
        print(f"Telegram error: {e}")


def send_pushover_message(message: str):
    if not ENABLE_PUSHOVER:
        return

    try:
        requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": PUSHOVER_TOKEN,
                "user": PUSHOVER_USER,
                "message": message,
                "priority": 2,
                "retry": 30,
                "expire": 120,
                "sound": "persistent",
                "title": "Visa Slot Alert",
            }
        )

        print("Pushover alert sent")

    except Exception as e:
        print(f"Pushover error: {e}")


def get_relative_minutes(relative_text: str):
    try:
        text = relative_text.lower().strip()

        if "second" in text or "just now" in text:
            return 0

        if "minute" in text:
            return int(text.split("minute")[0].strip())

        return None

    except Exception:
        return None


def check_slot():
    driver = None

    try:
        driver = Driver(
            uc=True,
            headless=True,
            chromium_arg="--no-sandbox,--disable-dev-shm-usage"
        )

        print("Opening page...")
        driver.get(URL)

        # Let JS load fully
        time.sleep(10)

        page_source = driver.page_source.lower()

        if "cloudflare" in page_source:
            print("Blocked by Cloudflare")
            return

        tables = driver.find_elements(By.TAG_NAME, "table")

        print(f"Found {len(tables)} table(s)")

        if not tables:
            print("No table found on page")
            return

        for table in tables:
            print(table.text)

    except Exception as e:
        print(f"Full error: {type(e).name}: {e}")

    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    while True:
        check_slot()
        time.sleep(REFRESH_INTERVAL)

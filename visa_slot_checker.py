import time
import requests
import traceback
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
        driver = Driver(     browser="chrome",     headless=True,     no_sandbox=True,     disable_gpu=True )

        driver.get(URL)

        table_xpath = "//*[contains(text(),'H-1B (Regular)')]/following::table[1]"

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, table_xpath)
            )
        )

        time.sleep(5)

        cells = driver.find_elements(
            By.XPATH,
            f"{table_xpath}//td"
        )

        times = [
            cell.text.strip()
            for cell in cells
            if cell.text.strip()
        ]

        print(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {times}"
        )

        recent_alerts = []

        for rel_time in times:
            mins = get_relative_minutes(rel_time)

            if mins is not None and mins <= ALERT_THRESHOLD_MINUTES:
                recent_alerts.append(rel_time)

        if recent_alerts:
            alert_message = (
                f"🚨 H-1B Slots Updated Recently: "
                f"{', '.join(recent_alerts)}\n{URL}"
            )

            print(alert_message)

            send_telegram_message(alert_message)
            send_pushover_message(alert_message)

        else:
            print("No recent updates found.")

   
        except Exception:
    print("FULL ERROR:")
    traceback.print_exc()

    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    while True:
        check_slot()
        time.sleep(REFRESH_INTERVAL)

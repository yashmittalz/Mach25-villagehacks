import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8660986927:AAFAXBqYTHXGmIVFGGlmOhBco3v5N3mp65I")

def send_message(chat_id: str, text: str):
    """Sends a message back to the Telegram user."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    print(f"[Telegram Attempt] Sending: {text}")
    res = requests.post(url, json={"chat_id": chat_id, "text": text})
    if res.status_code != 200:
        print(f"Telegram Delivery Error: {res.text}")
    else:
        print(f"Telegram Message Sent successfully!")

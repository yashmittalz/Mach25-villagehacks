import requests
import os
import sys
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8660986927:AAFAXBqYTHXGmIVFGGlmOhBco3v5N3mp65I")

def set_webhook(ngrok_url):
    # Ensure it ends with /webhook
    if not ngrok_url.endswith("/webhook"):
        webhook_url = f"{ngrok_url.rstrip('/')}/webhook"
    else:
        webhook_url = ngrok_url

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
    response = requests.post(url, json={"url": webhook_url})
    
    if response.status_code == 200 and response.json().get("ok"):
        print(f"Successfully set webhook to: {webhook_url}")
    else:
        print(f"Failed to set webhook. Error: {response.text}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/set_webhook.py <your_ngrok_url>")
    else:
        set_webhook(sys.argv[1])

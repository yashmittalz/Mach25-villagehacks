import requests
import os
from dotenv import load_dotenv
from core.brain import handle_incoming_message

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AUTODB_API_KEY = os.getenv("AUTODB_API_KEY")
AUTODB_CONNECTION_ID = os.getenv("AUTODB_CONNECTION_ID")
TELEGRAM_BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


# ── Real Telegram Function (from Hacker 1) ──────────────────────────
def send_telegram_message(chat_id: str, reply: str):
    requests.post(f"{TELEGRAM_BASE_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": reply
    })


# ── Real AutoDB Function (from Hacker 2) ────────────────────────────
def call_autodb(prompt: str) -> str:
    try:
        response = requests.post(
            f"https://api.autodb.app/api/v1/connections/{AUTODB_CONNECTION_ID}/queries/generate",
            headers={
                "X-API-Key": AUTODB_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "prompt": prompt,
                "execute": True,
                "guardrail": "permissive"
            },
            timeout=10  # don't hang forever
        )
        print(f"[AutoDB status]: {response.status_code}")
        print(f"[AutoDB response]: {response.text}")
        data = response.json()
        return str(data.get("data", {}).get("result", "No result returned"))
    
    except Exception as e:
        print(f"[AutoDB error]: {e}")
        return "Database temporarily unavailable"


# ── Telegram Polling Loop ────────────────────────────────────────────
def start_polling():
    print("Bot is running... waiting for messages")
    last_update_id = None

    while True:
        # Get new messages
        params = {"timeout": 30, "offset": last_update_id}
        response = requests.get(f"{TELEGRAM_BASE_URL}/getUpdates", params=params)
        updates = response.json().get("result", [])

        for update in updates:
            last_update_id = update["update_id"] + 1

            # Extract message info
            message = update.get("message", {})
            chat_id = message.get("chat", {}).get("id")
            user_text = message.get("text", "")

            if not chat_id or not user_text:
                continue

            print(f"\n[Received from {chat_id}]: {user_text}")

            # Pass to brain orchestrator
            handle_incoming_message(
                user_text=user_text,
                autodb_fn=call_autodb,
                telegram_fn=lambda reply: send_telegram_message(chat_id, reply)
            )


if __name__ == "__main__":
    start_polling()
import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from core.database import execute_agent_query
from core.brain import handle_incoming_message

load_dotenv()

app = FastAPI()

# Setup config
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN", "8660986927:AAFAXBqYTHXGmIVFGGlmOhBco3v5N3mp65I")

def send_telegram_message(chat_id: str, reply: str):
    """Utility to send telegram responses back to the user."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={
            "chat_id": chat_id,
            "text": reply
        })
    except Exception as e:
        print(f"Failed to send telegram message: {str(e)}")

@app.post("/webhook")
async def webhook(req: Request):
    """
    The main hook serving as the Plumber. 
    Connects incoming Telegram webhook calls to the AI Brain.
    """
    data = await req.json()

    # Accommodate Telegram's webhook payload structure securely
    message_data = data.get("message")
    if not message_data or "text" not in message_data:
        return {"ok": True}

    user_text = message_data["text"]
    chat_id = message_data["chat"]["id"]

    print(f"\n[Received Webhook for Chat {chat_id}]: {user_text}")

    # Pass the text to the AI Orchestrator (The Brain)
    # Give it the DB executor and the Telegram sender callbacks
    handle_incoming_message(
        user_text=user_text,
        autodb_fn=execute_agent_query,
        telegram_fn=lambda reply: send_telegram_message(chat_id, reply)
    )

    return {"ok": True}

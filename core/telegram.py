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

def send_message_with_buttons(chat_id: str, text: str):
    """Sends a message with a quick-action keyboard."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    keyboard = {
        "keyboard": [
            [{"text": "📈 View Inventory"}, {"text": "💰 Log a Sale"}],
            [{"text": "➕ Restock Item"}, {"text": "❓ Help"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": keyboard
    }

    print(f"[Telegram Attempt] Sending with Buttons: {text}")
    res = requests.post(url, json=payload)
    if res.status_code != 200:
        print(f"Telegram Delivery Error: {res.text}")
    else:
        print(f"Telegram Message with Buttons Sent successfully!")

def download_voice(file_id: str) -> str:
    """Download a voice message from Telegram and return the temporary file path."""
    import tempfile
    
    file_info = requests.get(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile",
        params={"file_id": file_id}
    ).json()
    
    if not file_info.get("ok"):
        return ""
        
    file_path = file_info["result"]["file_path"]
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"

    audio_data = requests.get(file_url).content
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f:
        f.write(audio_data)
        return f.name

def send_voice(chat_id: str, audio_path: str):
    """Sends a local audio file as a voice message."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVoice"
    try:
        with open(audio_path, "rb") as audio_file:
            res = requests.post(url, data={"chat_id": chat_id}, files={"voice": audio_file})
        
        if res.status_code != 200:
            print(f"Voice send error: {res.text}")
        else:
            print(f"Voice message sent to {chat_id}")
    except Exception as e:
        print(f"Failed to send voice message: {e}")

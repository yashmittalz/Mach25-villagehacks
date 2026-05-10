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

def send_voice(chat_id: str, text: str):
    """Converts text to speech and sends as voice message."""
    from elevenlabs.client import ElevenLabs
    from elevenlabs import VoiceSettings
    import tempfile

    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("ELEVENLABS_API_KEY is not set. Cannot send voice message.")
        return

    try:
        eleven = ElevenLabs(api_key=api_key)
        audio = eleven.text_to_speech.convert(
            text=text,
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75)
        )
        
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f:
            for chunk in audio:
                f.write(chunk)
            temp_path = f.name
        
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVoice"
        with open(temp_path, "rb") as audio_file:
            res = requests.post(url, data={"chat_id": chat_id}, files={"voice": audio_file})
        
        if res.status_code != 200:
            print(f"Voice send error: {res.text}")
        else:
            print(f"Voice message sent to {chat_id}")
            
        os.remove(temp_path)
    except Exception as e:
        print(f"Failed to generate or send voice message: {e}")

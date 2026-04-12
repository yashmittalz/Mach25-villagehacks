import requests

def send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })
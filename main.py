from fastapi import FastAPI, Request
from autodb_client import AutoDBClient
from bot_utils import send_message

app = FastAPI()

BOT_TOKEN = "8660986927:AAFAXBqYTHXGmIVFGGlmOhBco3v5N3mp65I"
autodb = AutoDBClient()

# STEP 1: receive message
@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()

    message = data["message"]["text"]
    chat_id = data["message"]["chat"]["id"]

    # STEP 2: send to AutoDB
    response = handle_message(message)

    # STEP 3: reply to user
    send_message(BOT_TOKEN, chat_id, response)

    return {"ok": True}


def handle_message(message):
    return autodb.process(message)# Reya (Plumber) will work here

from fastapi import FastAPI, Request
from core.brain import parse_message, format_db_result
from core.database import execute_vibe_query
from core.telegram import send_message

app = FastAPI()

@app.post("/webhook")
async def webhook(req: Request):
    """Handles incoming Telegram messages via Webhook."""
    data = await req.json()
    
    # Catch empty/system messages
    if "message" not in data or "text" not in data["message"]:
        return {"ok": True}

    user_text = data["message"]["text"]
    chat_id = data["message"]["chat"]["id"]
    print(f"\n[Received]: {user_text}")

    # STEP 1: Parse Intent with Gemini
    parsed = parse_message(user_text)
    action = parsed.get("action")
    db_prompts = parsed.get("autodb_prompts", [])
    final_reply = parsed.get("whatsapp_reply")

    # STEP 2: Execute Database Actions
    if action in ["write", "read"] and db_prompts:
        results = []
        for prompt in db_prompts:
            db_result = execute_vibe_query(prompt)
            results.append(db_result)
        
        # STEP 3: If it was a READ, use Gemini to format the aggregate DB results into a text
        if action == "read":
            combined_results = "\\n".join(results)
            final_reply = format_db_result(user_text, combined_results)

    # STEP 4: Send the message back to Telegram
    send_message(chat_id, final_reply)

    return {"ok": True}

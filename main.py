from fastapi import FastAPI, Request
from core.brain import parse_message, format_db_result, analyze_business_health
from core.database import execute_vibe_query
from core.telegram import send_message, send_message_with_buttons

app = FastAPI()

# Store recent conversation history in memory for context (chat_id -> list of messages)
chat_history = {}

@app.post("/webhook")
async def webhook(req: Request):
    """Handles incoming Telegram messages via Webhook."""
    data = await req.json()
    
    # Catch empty/system messages
    if "message" not in data or "text" not in data["message"]:
        return {"ok": True}

    user_text = data["message"]["text"]
    chat_id = data["message"]["chat"]["id"]
    user_name = data["message"]["from"].get("first_name", "there")
    print(f"\n[Received]: {user_text}")

    # Initialize history for this user if it doesn't exist
    if chat_id not in chat_history:
        chat_history[chat_id] = []

    # STEP 0: Handle /start command
    if user_text == "/start":
        send_message_with_buttons(
            chat_id,
            f"👋 Hey {user_name}! I'm your inventory assistant.\n\nJust tell me what's happening — like:\n• 'Sold 5 apples to John'\n• 'Add 20 honeycrisp to stock'\n• 'What's my inventory?'\n\nOr use the buttons below! 👇"
        )
        chat_history[chat_id] = [] # Reset history on start
        return {"ok": True}

    # Add user message to history
    chat_history[chat_id].append(f"User: {user_text}")
    # Keep only the last 6 messages (3 turns) to prevent context bloat
    history_context = chat_history[chat_id][-6:]

    # STEP 1: Parse Intent with LLM
    parsed = parse_message(user_text, history_context)
    action = parsed.get("action")
    db_prompts = parsed.get("autodb_prompts", [])
    final_reply = parsed.get("telegram_reply")

    # STEP 2: Execute Database Actions
    if action in ["write", "read"] and db_prompts:
        results = []
        for prompt in db_prompts:
            db_result = execute_vibe_query(prompt)
            results.append(db_result)
        
        # STEP 3: If it was a READ, use LLM to format the aggregate DB results into a text
        if action == "read":
            combined_results = "\\n".join(results)
            final_reply = format_db_result(user_text, combined_results)
        
        # STEP 4: If it was a WRITE, analyze business health for smart suggestions
        elif action == "write":
            combined_results = "\\n".join(results)
            alert = analyze_business_health(combined_results)
            if alert:
                final_reply = f"{final_reply}\n\n{alert}"

    # STEP 5: Send the message back to Telegram
    send_message(chat_id, final_reply)
    
    # Save bot's reply to history
    chat_history[chat_id].append(f"Bot: {final_reply}")

    return {"ok": True}

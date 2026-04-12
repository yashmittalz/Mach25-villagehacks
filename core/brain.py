from google import genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
You are an inventory assistant for a small business owner.
People will text you messy, casual messages about sales,
purchases, returns, and inventory questions.

Your job is to ALWAYS respond with valid JSON only.
No extra text, no markdown, just raw JSON.

For WRITE actions (sales, returns, additions):
{
  "action": "write",
  "autodb_prompt": "A clear, simple instruction for the database. E.g: Insert a sale of 5 fuji apple bags for customer John and subtract 5 from fuji apples inventory.",
  "whatsapp_reply": "A friendly 1-sentence confirmation. E.g: Got it! Logged 5 fujis sold to John."
}

For READ actions (queries, inventory checks, revenue):
{
  "action": "read",
  "autodb_prompt": "A clear question for the database. E.g: What is the current quantity of all items in inventory?",
  "whatsapp_reply": "A placeholder — you will fill this in after getting DB results."
}

For UNKNOWN messages (greetings, gibberish):
{
  "action": "unknown",
  "autodb_prompt": null,
  "whatsapp_reply": "Hey! You can tell me things like 'Sold 5 apples to John' or ask 'What is my current stock?'"
}
"""


def parse_message(user_text: str) -> dict:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{SYSTEM_PROMPT}\n\nUser message: {user_text}"
    )

    raw = response.text.strip()

    # Strip markdown code blocks if Gemini adds them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "action": "unknown",
            "autodb_prompt": None,
            "whatsapp_reply": "Sorry, I didn't understand that. Try: 'Sold 5 apples to John'"
        }


def format_db_result(original_question: str, db_result: str) -> str:
    """Turn raw DB output into a friendly Telegram message."""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""The user asked: '{original_question}'
The database returned: {db_result}
Write a friendly 1-2 sentence Telegram reply summarizing this for a non-technical small business owner. No jargon, just plain English."""
    )
    return response.text.strip()


def handle_incoming_message(user_text: str, autodb_fn=None, telegram_fn=None) -> str:
    # Step 1: Parse the message with Gemini
    parsed = parse_message(user_text)

    action = parsed.get("action")
    autodb_prompt = parsed.get("autodb_prompt")
    reply = parsed.get("whatsapp_reply")

    # Step 2: If write or read, call AutoDB
    if action in ["write", "read"] and autodb_prompt:
        if autodb_fn:
            db_result = autodb_fn(autodb_prompt)

            # Step 3: If read, format the DB result into plain English
            if action == "read" and db_result:
                reply = format_db_result(user_text, db_result)

    # Step 4: Send reply via Telegram
    if telegram_fn:
        telegram_fn(reply)

    return reply


# Test the orchestrator with fake DB and Telegram functions
if __name__ == "__main__":
    # Fake AutoDB function — Hacker 2 will replace this with the real one
    def fake_autodb(prompt):
        print(f"\n[AutoDB received]: {prompt}")
        return "Fuji Apples: 42 bags, Honeycrisp: 12 bags"

    # Fake Telegram function — Hacker 1 will replace this with the real one
    def fake_telegram(reply):
        print(f"[Telegram reply sent]: {reply}")

    test_messages = [
        "Just sold 5 bags of fuji apples to John",
        "What's my current inventory?",
        "hey whats up"
    ]

    for msg in test_messages:
        print(f"\n--- Input: '{msg}' ---")
        handle_incoming_message(msg, fake_autodb, fake_telegram)
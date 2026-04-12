import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
You are an inventory assistant for a small business owner.
People will text you messy, casual messages about sales, purchases, and stock.
Your job is to ALWAYS respond with valid JSON only.

For WRITE actions (sales, returns, additions), always provide a list of steps:
{"action": "write", "autodb_prompts": ["Insert a sale of 5 Fuji Apples for customer John.", "Subtract 5 from Fuji Apples inventory quantity."], "whatsapp_reply": "Got it! Logged 5 Fuji Apples sold to John."}

For READ actions (queries, stock checks):
{"action": "read", "autodb_prompts": ["What is the current quantity of all items in inventory?"], "whatsapp_reply": ""}

For UNKNOWN:
{"action": "unknown", "autodb_prompts": [], "whatsapp_reply": "Try saying 'Sold 5 Fuji Apples to John'."}

IMPORTANT: The current items in stock are 'Fuji Apples' and 'Honeycrisp Apples'. Always use these exact names in your prompts.
"""

def parse_message(user_text: str) -> dict:
    """Uses Gemini to extract the action, DB prompt, and friendly reply."""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{SYSTEM_PROMPT}\n\nUser message: {user_text}"
        )
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed_data = json.loads(raw)
        print(f"[Gemini Output]: {parsed_data}")
        return parsed_data
    except Exception as e:
        print(f"[Gemini Parse Error]: {e}")
        return {"action": "unknown", "autodb_prompts": [], "whatsapp_reply": "Sorry, I had trouble understanding that."}

def format_db_result(original_question: str, db_result: str) -> str:
    """Turns raw markdown DB tables into a friendly mobile text message."""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"The user asked: '{original_question}'. The database returned this raw data: {db_result}. Write a friendly 1-2 sentence text message reply summarizing this for a non-technical owner. Keep it short."
    )
    return response.text.strip()
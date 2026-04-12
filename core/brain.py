import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
You are a highly efficient inventory assistant for a small business owner.
People will text you messy, casual messages about sales, purchases, and stock.
Your job is to ALWAYS respond with valid JSON only.

For WRITE actions (sales, purchases, restocks, returns):
1. Determine if the user is SELLING or BUYING/RESTOCKING.
2. Generate a list of autodb_prompts. 
   - If it's a SALE: ["Insert a sale of [Qty] [Item] for [Customer].", "Subtract [Qty] from [Item] inventory quantity."]
   - If it's a PURCHASE/RESTOCK: ["Ensure [Item] exists in inventory. If not, create it. Then add [Qty] to [Item] inventory quantity."]
3. Your `telegram_reply` must be extremely short, spartan, and conversational.

Example Response for New Item:
{"action": "write", "autodb_prompts": ["Ensure 'Bananas' exists in inventory with 0 starter qty if missing, then add 200 to 'Bananas' qty."], "telegram_reply": "Got it. Added 200 Bananas to stock."}

For READ actions (queries, stock checks):
{"action": "read", "autodb_prompts": ["What is the current quantity of all items in inventory?"], "telegram_reply": ""}

For UNKNOWN:
{"action": "unknown", "autodb_prompts": [], "telegram_reply": "Can't understand that. Try again in a while."}

IMPORTANT: Try to match the item name mentioned by the user to the most likely existing item in the database. If it's clearly a new item, create it.
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
        return {"action": "unknown", "autodb_prompts": [], "telegram_reply": "Sorry, I had trouble understanding that."}

def format_db_result(original_question: str, db_result: str) -> str:
    """Turns raw markdown DB tables into a friendly mobile text message."""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"The user asked: '{original_question}'. The database returned this raw data: {db_result}. Write a short, spartan, and conversational text message reply summarizing this. Do not sound like an AI assistant. Just give them the answer naturally."
    )
    return response.text.strip()

def analyze_business_health(db_result: str) -> str:
    """Uses Gemini to evaluate if the stock warrants a low inventory alert or high demand alert."""
    import requests
    from core.database import BASE_URL, API_KEY, CONN_ID
    
    # Fetch the actual current state of the inventory
    payload = {
        "connection_id": CONN_ID,
        "sql": "SELECT * FROM inventory",
        "caller": "human"
    }
    
    try:
        res = requests.post(f"{BASE_URL}/execute", headers={"X-API-Key": API_KEY}, json=payload, timeout=10)
        data = res.json()
        if data.get("success") and data.get("data"):
            rows = data["data"].get("rows", [])
            cols = data["data"].get("columns", [])
            inventory_state = f"Columns: {cols}\nRows: {rows}"
        else:
            inventory_state = "Unable to fetch inventory."
    except:
        inventory_state = "Unable to fetch inventory."

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"The database just performed an action. Here is the CURRENT inventory state:\n{inventory_state}\n\nBased on this, check if any item quantity is 20 or below. Return EXACTLY the single word 'NONE' if everything is > 20. If an alert is warranted, write a short, spartan 1-sentence warning message to the owner (e.g. 'Fuji Apples are down to 15. Restock soon.'). Do not include any standard AI greeting."
    )
    res = response.text.strip()
    if res == 'NONE':
        return ""
    return res
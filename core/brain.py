import os
import json
import requests
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    # Try one more time with explicit path if called from a subdirectory
    load_dotenv(os.path.join(os.getcwd(), ".env"))
    api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

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

IMPORTANT:
- If the user says exactly '📈 View Inventory', treat it as a READ action.
- If the user says exactly '💰 Log a Sale', interpret it as an UNKNOWN action but ask them 'What did you sell and to whom?' in the telegram_reply.
- If the user says '❓ Help', give them a short spartan guide.
- Try to match the item name mentioned by the user to the most likely existing item in the database. If it's clearly a new item, create it.
"""

def parse_message(user_text: str, history: list = None) -> dict:
    """Uses Gemini to extract the action, DB prompt, and friendly reply."""
    
    # Format chat history for context
    history_context = ""
    if history and len(history) > 1: # Don't just show their current message
        history_context = "--- Recent Chat Context ---\n" + "\n".join(history[:-1]) + "\n---------------------------\n\n"

    try:
        response = client.models.generate_content(
            model="gemma-3-27b-it",
            contents=f"{SYSTEM_PROMPT}\n\n{history_context}Current User message: {user_text}"
        )
        raw_text = response.text.strip()
        
        # Clean up markdown backticks if present
        if raw_text.startswith("```"):
            lines = raw_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_text = "\n".join(lines).strip()
            
        parsed_data = json.loads(raw_text)
        print(f"[Gemini Output]: {parsed_data}")
        return parsed_data
    except Exception as e:
        print(f"[Gemini Parse Error]: {e}")
        return {"action": "unknown", "autodb_prompts": [], "telegram_reply": "Sorry, I had trouble understanding that."}

def format_db_result(original_question: str, db_result: str) -> str:
    """Turns raw markdown DB tables into a friendly mobile text message."""
    response = client.models.generate_content(
        model="gemma-3-27b-it",
        contents=f"The user asked: '{original_question}'. The database returned this raw data: {db_result}. Write a short, spartan, and conversational text message reply summarizing this. Do not sound like an AI assistant. Just give them the answer naturally."
    )
    return response.text.strip()

def analyze_business_health(db_result: str) -> str:
    """Uses Gemini to evaluate if the stock warrants a low inventory alert or high demand alert."""
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
        model="gemma-3-27b-it",
        contents=f"The database just performed an action. Here is the CURRENT inventory state:\n{inventory_state}\n\nBased on this, check if any item quantity is 20 or below. Return EXACTLY the single word 'NONE' if everything is > 20. If an alert is warranted, write a short, spartan 1-sentence warning message to the owner (e.g. 'Fuji Apples are down to 15. Restock soon.'). Do not include any standard AI greeting."
    )
    res = response.text.strip()
    if res == 'NONE':
        return ""
    return res
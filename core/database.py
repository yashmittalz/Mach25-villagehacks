import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AUTODB_API_KEY")
CONN_ID = os.getenv("AUTODB_CONNECTION_ID")
BASE_URL = "https://api.autodb.app/api/v1"

HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

def execute_vibe_query(intent_prompt: str):
    """
    Takes plain English (e.g., 'Add 5 apples to inventory') 
    and mutates the database via AutoDB.
    """
    payload = {
        "connection_id": CONN_ID,
        "prompt": intent_prompt,
        "execute": True,
        "caller": "agent",
        "guardrail": "permissive"
    }
    
    response = requests.post(f"{BASE_URL}/generate", headers=HEADERS, json=payload)
    return response.json()

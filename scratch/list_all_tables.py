import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AUTODB_API_KEY")
CONN_ID = os.getenv("AUTODB_CONNECTION_ID")
BASE_URL = "http://api.autodb.app/api/v1"

HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

def list_all_tables():
    sql = "SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog', 'information_schema');"
    
    print(f"Listing ALL tables for Connection ID: {CONN_ID}...")
    try:
        res = requests.post(
            f"{BASE_URL}/execute",
            headers=HEADERS,
            json={
                "connection_id": CONN_ID,
                "sql": sql,
                "caller": "human"
            },
            timeout=10
        )
        print(json.dumps(res.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_all_tables()

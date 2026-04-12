import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AUTODB_API_KEY")
CONN_ID = os.getenv("AUTODB_CONNECTION_ID")
BASE_URL = "http://api.autodb.app/api/v1"

HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

def query_all_rows():
    tables = ["inventory", "sales_log"]
    
    for table in tables:
        print(f"\n--- Rows in {table} ---")
        sql = f"SELECT * FROM {table};"
        
        try:
            res = requests.post(
                f"{BASE_URL}/execute",
                headers=HEADERS,
                json={
                    "connection_id": CONN_ID,
                    "sql": sql,
                    "caller": "human"
                },
                timeout=15
            )
            
            if res.status_code == 200:
                data = res.json()
                if data.get("success"):
                    result_data = data.get("data", {})
                    rows = result_data.get("rows", [])
                    if not rows:
                        print("Table is empty.")
                    else:
                        for row in rows:
                            print(row)
                else:
                    print(f"AutoDB Error: {data.get('error')}")
            else:
                print(f"HTTP Error {res.status_code}: {res.text}")
                
        except Exception as e:
            print(f"Error querying {table}: {e}")

if __name__ == "__main__":
    query_all_rows()

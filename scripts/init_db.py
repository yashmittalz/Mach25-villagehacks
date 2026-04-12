import requests
import os
from dotenv import load_dotenv

load_dotenv()

def initialize_schema():
    API_KEY = os.getenv("AUTODB_API_KEY")
    CONN_ID = os.getenv("AUTODB_CONNECTION_ID")
    BASE_URL = "https://api.autodb.app/api/v1"
    
    HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

    sql = """
    CREATE TABLE IF NOT EXISTS public.inventory (
        id SERIAL PRIMARY KEY, 
        item_name VARCHAR(100), 
        qty INT
    );
    CREATE TABLE IF NOT EXISTS public.sales_log (
        id SERIAL PRIMARY KEY, 
        item VARCHAR(100), 
        qty_sold INT, 
        customer VARCHAR(100), 
        created_at TIMESTAMP DEFAULT NOW()
    );
    INSERT INTO public.inventory (item_name, qty) 
    VALUES ('Fuji Apples', 100), ('Honeycrisp Apples', 50)
    ON CONFLICT DO NOTHING;
    """
    print("🚀 Creating tables...")
    res = requests.post(
        f"{BASE_URL}/execute",
        headers=HEADERS,
        json={"connection_id": CONN_ID, "sql": sql, "caller": "human"}
    )
    print("Table Creation Result:", res.json())
    
    print("\n🔍 Forcing introspection of public schema...")
    res_index = requests.post(
        f"{BASE_URL}/connections/{CONN_ID}/introspect?schemas=public",
        headers=HEADERS
    )
    print("Index Result:", res_index.json())
    print("Database schema initialized.")

if __name__ == "__main__":
    initialize_schema()

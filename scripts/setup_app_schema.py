import requests
import os
from dotenv import load_dotenv

load_dotenv()

def initialize_app_schema():
    API_KEY = os.getenv("AUTODB_API_KEY")
    CONN_ID = os.getenv("AUTODB_CONNECTION_ID")
    BASE_URL = "http://api.autodb.app/api/v1" # Use http to avoid SSL/Timeout issues
    
    HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

    print(f"🚀 Setting up 'app' schema for connection: {CONN_ID}...")

    # SQL to create schema and tables
    sql = """
    CREATE SCHEMA IF NOT EXISTS app;
    
    CREATE TABLE IF NOT EXISTS app.inventory (
        id SERIAL PRIMARY KEY, 
        item_name VARCHAR(100), 
        qty INT
    );
    
    CREATE TABLE IF NOT EXISTS app.sales_log (
        id SERIAL PRIMARY KEY, 
        item VARCHAR(100), 
        qty_sold INT, 
        customer VARCHAR(100), 
        created_at TIMESTAMP DEFAULT NOW()
    );
    
    -- Seed data
    INSERT INTO app.inventory (item_name, qty) 
    VALUES ('Fuji Apples', 100), ('Honeycrisp Apples', 50)
    ON CONFLICT DO NOTHING;
    """
    
    res = requests.post(
        f"{BASE_URL}/execute",
        headers=HEADERS,
        json={"connection_id": CONN_ID, "sql": sql, "caller": "human"}
    )
    print("Table Provisioning Result:", res.json())
    
    print("\n🔍 Forcing introspection of 'app' schema...")
    res_index = requests.post(
        f"{BASE_URL}/connections/{CONN_ID}/introspect?schemas=app",
        headers=HEADERS
    )
    print("Introspection Result:", res_index.json())
    print("\n✅ App database schema initialized in schema 'app'.")

if __name__ == "__main__":
    initialize_app_schema()

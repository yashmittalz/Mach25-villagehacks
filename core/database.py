import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AUTODB_API_KEY")
CONN_ID = os.getenv("AUTODB_CONNECTION_ID")
BASE_URL = "http://api.autodb.app/api/v1" # Using HTTP to avoid ASU Wifi timeouts

def execute_vibe_query(intent_prompt: str) -> str:
    """Takes plain English and mutates the database via AutoDB."""
    # Since we split prompts in brain.py, we only need simple singular statements now.
    # Tell the Vibe Query LLM exactly which schema to use for inventory/sales
    schema_hint = "IMPORTANT: Use schema 'tenant_b0fbbfb01cc86d41' for all queries involving 'inventory' or 'sales_log' tables."
    safe_prompt = f"{intent_prompt} RULES: {schema_hint} Use a SINGLE SQL statement only. Use ILIKE for string matches. If it's an INSERT, UPDATE, or DELETE, ALWAYS end with RETURNING *."
    
    payload = {
        "connection_id": CONN_ID,
        "prompt": safe_prompt,
        "execute": True,
        "caller": "agent",
        "guardrail": "permissive"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate", headers={"X-API-Key": API_KEY}, json=payload, timeout=15)
        data = response.json()
        
        if data.get("success"):
            print("[AutoDB DEBUG]:", data)
            payload_data = data.get("data", {})
            markdown = payload_data.get("markdown_output")
            
            if payload_data.get("execution_error"):
                err_msg = payload_data['execution_error']
                # SQLAlchemy throws this when an UPDATE succeeds but returns no rows
                if "does not return rows" not in err_msg:
                    return f"Execution Error: {err_msg}"
            
            # Fallback if markdown_output is missing but we have execution_result rows
            if not markdown and payload_data.get("execution_result"):
                rows = payload_data["execution_result"].get("rows", [])
                cols = payload_data["execution_result"].get("columns", [])
                
                if rows:
                    if len(rows) == 1 and len(rows[0]) == 1:
                        markdown = str(rows[0][0])
                    else:
                        markdown = " | ".join(cols) + "\n"
                        for row in rows:
                            markdown += " | ".join([str(val) for val in row]) + "\n"
                else:
                    markdown = "Success, but no records returned."
            
            return markdown or "Success."
        else:
            print("[AutoDB Error]:", data)
            return "Database Error: " + str(data.get("error", "Unknown error"))
    except Exception as e:
        print("[AutoDB Exception]:", str(e))
        return "Database timeout or unreachable."

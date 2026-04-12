# 🍎 Vibecheck Inventory

A premium, AI-powered inventory management system built for **VillageHacks '26**. This system leverages **AutoDB** to allow users to manage stock and log sales using plain English natural language commands.

---

## 🏗️ Project Architecture

Designed by **The Architect**, this project uses a modular structure to support rapid development:

-   **`main.py`**: The "Plumbing" layer. Handles FastAPI endpoints, ngrok integration, and the web server lifecycle.
-   **`core/`**:
    -   `database.py`: The data-access layer. Interfaces directly with the AutoDB API.
    -   `ai_logic.py`: The "Brain". Home for custom Gemini-based intent parsing and decision-making logic.
-   **`scripts/`**:
    -   `init_db.py`: One-time setup script to provision the schema and seed initial inventory data.
-   **`Archive/`**: Preservation of legacy setup and debugging scripts.

---

## 🚀 Quick Start

### 1. Environment Setup
Create a virtual environment and install the required stack:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration
Copy the template and fill in your API keys:
```bash
cp .env.example .env
```
*Required: `AUTODB_API_KEY`, `AUTODB_CONNECTION_ID`, and `GEMINI_API_KEY`.*

### 3. Database Provisioning
Run the initialization script to create the `inventory` and `sales_log` tables in AutoDB:
```bash
python3 scripts/init_db.py
```

---

## 🛠️ Team
- **Yash Mittal**: The Architect
- **Reya**: The Plumber
- **Harshith**: The Brain

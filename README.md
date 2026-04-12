# VibeCheck Inventory
**Headless inventory management via text. If your software requires a tutorial, your software is broken.**

![Built at VillageHacks '26](https://img.shields.io/badge/VillageHacks-'26-orange)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green)
![AutoDB](https://img.shields.io/badge/Database-AutoDB-black)

Small business owners—like farmers, bakers, and local mechanics—spend up to 50% of their time on data entry. They are forced to use clunky, "vibe-coded" dashboards that only they understand. 

**VibeCheck kills the dashboard.** We built a headless ERP that lives entirely inside Telegram. You don't navigate menus; you just text your database. 

*“Sold 5 apples to John.”* -> **Database updated. Done.**

---

## Features

- **Natural Language to SQL:** Powered by Google Gemini (`gemma-3-27b-it`) and AutoDB's Text-to-SQL engine. Messy texts are instantly translated into precise database mutations.
- **Permissive Agent Execution:** We utilize AutoDB's `permissive` guardrails to allow our AI agent to autonomously execute `INSERT`, `UPDATE`, and `DELETE` commands without human intervention.
- **The Pinocchio Protocol (Proactive Alerts):** The system automatically queries the database state after every write action. If inventory drops below 20, the bot proactively texts the owner a low-stock warning.
- **Context-Aware Chat:** Maintains short-term memory of the last 3 conversation turns so users can ask follow-up questions seamlessly.

---

## Architecture & Tech Stack

We rebuilt our MVP mid-hackathon to separate concerns into a highly modular, production-ready FastAPI architecture.

* **Frontend:** Telegram Bot API (Interactive Keyboards & Webhooks)
* **Backend:** FastAPI (Python)
* **Database:** AutoDB (PostgreSQL)
* **AI/LLM:** Google Gemini API 
* **Marketing/Traction:** Tamagrow (Syncing GitHub commits to LinkedIn for "Build in Public" virality).

```text
/vibecheck-inventory
  ├── core/
  │   ├── brain.py         # LLM Intent extraction & JSON formatting
  │   ├── database.py      # AutoDB /generate client with permissive guardrails
  │   └── telegram.py      # Outbound Telegram API requests
  ├── scripts/
  │   ├── init_db.py       # AutoDB table creation & forced introspection
  │   ├── query_db.py      # CLI debugging tool
  │   └── set_webhook.py   # Binds the ngrok tunnel to Telegram
  └── main.py              # The Ultimate Orchestrator (FastAPI Webhook)

```

## Team
- **Yash Mittal**: The Forger
- **Reya**: The Conduit
- **Harshith**: The Alchemist
- **Souradeep**: The Herald

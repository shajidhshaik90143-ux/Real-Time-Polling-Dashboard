
# Real-Time Polling Dashboard

A strong Streamlit + SQLite polling application for creating live polls, recording votes, viewing real-time analytics, and exporting results.

## Features
- Create unlimited polls with 2–10 options
- SQLite persistence
- Live vote result charts
- Vote-count and percentage analytics
- CSV and JSON exports
- Admin panel with recent vote activity
- Duplicate-vote protection using voter tokens
- Responsive Streamlit UI
- No external database required
- English-only interface
- Clean modular source structure

## Requirements
- Python 3.10–3.13 recommended
- Windows / macOS / Linux

## Run on Windows PowerShell

```powershell
cd "Real-Time Polling Dashboard"
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

Alternative:

```powershell
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

## Database
The database is automatically created at:
`data/polls.db`

Do not commit `data/polls.db` to a public repository if it contains real voting data.

## Important production note
The demo uses a generated local voter token. For a real public election/polling system, implement authenticated users, rate limiting, audit logs, HTTPS, server-side authorization, and a production database.

## Project structure

Real-Time Polling Dashboard/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── .gitkeep
├── assets/
│   └── .gitkeep
└── src/
    ├── __init__.py
    ├── database.py
    └── utils.py

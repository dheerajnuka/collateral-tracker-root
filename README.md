# Collateral Tracker (Local)

A Streamlit app to track collateral entries with interest, receipts, and statuses.

## Features
- Columns: **Item Status, Date, Name, Item Name, Weight, Amount, Phone Number, Date Of Item Received, Amount Received, Interest Rate (% p.a.)**
- Status options: `""`, `Taken`, `ReWrite`, `Sold`
- Search & export, inline quick edit in the Records tab
- Full edit tab with search by name/phone and status
- Reports tab with quick metrics
- SQLite by default; lightweight migrations add new columns if missing

## Run locally
```bash
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py --server.address localhost --server.port 8501
```

## Use Postgres/MySQL (optional)
Create `.streamlit/secrets.toml`:
```toml
[general]
DATABASE_URL = "postgresql+psycopg://user:pass@host:5432/db"
```
Install the DB driver if needed (e.g., `pip install psycopg[binary]`).


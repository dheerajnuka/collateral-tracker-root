# Collateral Tracker — Streamlit + PostgreSQL

## Local DB URL (with URL-encoded password)
postgresql+psycopg://appuser:dheeraj%401@localhost:5432/collateral

### Locally
Create `.streamlit/secrets.toml`:
```
DATABASE_URL = "postgresql+psycopg://appuser:dheeraj%401@localhost:5432/collateral"
```
Then:
```
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### Streamlit Cloud
Use a hosted Postgres URL and put it in **Settings → Secrets** as `DATABASE_URL`. Add `?sslmode=require` if needed.

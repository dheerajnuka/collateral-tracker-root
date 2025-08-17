import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

# Prefer Streamlit secrets if available
try:
    import streamlit as st
    _secret_url = st.secrets.get("DATABASE_URL", None)
except Exception:
    _secret_url = None

DB_URL = _secret_url or os.getenv("DATABASE_URL", "sqlite:///collateral.db")

connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}
engine = create_engine(DB_URL, echo=False, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def init_db():
    from .models import Collateral  # noqa
    Base.metadata.create_all(engine)
    # Lightweight migrations for SQLite
    if DB_URL.startswith("sqlite"):
        with engine.begin() as conn:
            res = conn.execute(text("PRAGMA table_info(collateral)")).all()
            existing = {r[1] for r in res}
            needed = {
                "phone_number": "TEXT",
                "received_date": "DATE",
                "amount_received": "REAL"
            }
            for col, typ in needed.items():
                if col not in existing:
                    conn.execute(text(f"ALTER TABLE collateral ADD COLUMN {col} {typ}"))

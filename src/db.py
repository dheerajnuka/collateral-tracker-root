import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

def _get_db_url() -> str:
    """Prefer Streamlit secrets (Cloud), then env var; fall back to SQLite for dev."""
    try:
        import streamlit as st
        url = st.secrets.get("DATABASE_URL")
        if url:
            return url
    except Exception:
        pass
    return os.getenv("DATABASE_URL", "sqlite:///collateral.db")

DB_URL = _get_db_url()

connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}
engine = create_engine(DB_URL, echo=False, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def init_db():
    from .models import Collateral  # noqa
    Base.metadata.create_all(engine)
    # Lightweight migration only for SQLite (no-op on Postgres)
    if DB_URL.startswith("sqlite"):
        with engine.begin() as conn:
            cols = {r[1] for r in conn.execute(text("PRAGMA table_info(collateral)")).all()}
            for col, typ in {"phone_number":"TEXT","received_date":"DATE","amount_received":"REAL"}.items():
                if col not in cols:
                    conn.execute(text(f"ALTER TABLE collateral ADD COLUMN {col} {typ}"))

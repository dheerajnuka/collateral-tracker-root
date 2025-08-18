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

def _mask_url(url: str) -> str:
    try:
        from sqlalchemy.engine.url import make_url
        u = make_url(url)
        password = u.password or ""
        if password:
            # mask all but first and last char (if length > 2)
            if len(password) <= 2:
                masked = "*" * len(password)
            else:
                masked = password[0] + "*" * (len(password) - 2) + password[-1]
            u = u.set(password=masked)
        return str(u)
    except Exception:
        return "(hidden)"

def _diagnose_error(e: Exception):
    import streamlit as st
    masked = _mask_url(DB_URL)
    st.error(
        "Cannot connect to the database.\n\n"
        f"**DATABASE_URL (masked):** `{masked}`\n\n"
        "Common fixes:\n"
        "• On Streamlit Cloud, use a **hosted** Postgres URL (not `localhost`)\n"
        "• URL-encode special characters in the password (e.g. `@` → `%40`)\n"
        "• Add `?sslmode=require` if your provider requires SSL\n"
        "• Ensure the DB, user and privileges exist"
    )
    with st.expander("Show technical details"):
        st.exception(e)
    st.stop()

def init_db():
    # Try a lightweight connection test so we can show helpful errors
    try:
        with engine.connect() as conn:
            conn.execute(text("select 1"))
    except Exception as e:
        _diagnose_error(e)

    from .models import Collateral  # noqa
    Base.metadata.create_all(engine)

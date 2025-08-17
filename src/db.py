import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

DB_URL = os.getenv("DATABASE_URL", "sqlite:///collateral.db")

connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}
engine = create_engine(DB_URL, echo=False, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def init_db():
    from .models import Collateral  # noqa
    Base.metadata.create_all(engine)
    if DB_URL.startswith("sqlite"):
        with engine.begin() as conn:
            cols = {r[1] for r in conn.execute(text("PRAGMA table_info(collateral)")).all()}
            for col, typ in {"phone_number":"TEXT","received_date":"DATE","amount_received":"REAL"}.items():
                if col not in cols:
                    conn.execute(text(f"ALTER TABLE collateral ADD COLUMN {col} {typ}"))

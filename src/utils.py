from datetime import date
import pandas as pd
import streamlit as st
from sqlalchemy.orm import Session
from .models import Collateral

@st.cache_data(show_spinner=False)
def _df_style(df: pd.DataFrame) -> pd.DataFrame:
    return df

def compute_interest(principal: float, rate_percent_pa: float, start: date, end: date | None = None) -> float:
    if end is None:
        end = date.today()
    days = (end - start).days
    if days <= 0:
        return 0.0
    interest = principal * (rate_percent_pa / 100.0) * (days / 365.0)
    return round(interest, 2)

def amount_due(principal: float, accrued_interest: float) -> float:
    return round(principal + accrued_interest, 2)

def get_df(session: Session, filters: dict | None = None) -> pd.DataFrame:
    q = session.query(Collateral)
    if filters:
        if (name := filters.get("name")):
            q = q.filter(Collateral.customer_name.ilike(f"%{name}%"))
        if (status := filters.get("status")) and status != "All":
            q = q.filter(Collateral.status == status)
        if (from_dt := filters.get("from")):
            q = q.filter(Collateral.start_date >= from_dt)
        if (to_dt := filters.get("to")):
            q = q.filter(Collateral.start_date <= to_dt)
    rows = q.order_by(Collateral.id.desc()).all()
    data = []
    for r in rows:
        intr = compute_interest(r.principal, r.interest_rate_pa, r.start_date, r.end_date if r.status == "Closed" else None)
        data.append({
            "ID": r.id,
            "Created On": r.created_on,
            "Customer": r.customer_name,
            "Item": r.item,
            "Weight (g)": r.weight_grams,
            "Principal": r.principal,
            "Interest % p.a.": r.interest_rate_pa,
            "Start": r.start_date,
            "End": r.end_date,
            "Status": r.status,
            "Accrued Interest": intr,
            "Amount Due": amount_due(r.principal, intr),
            "Comments": r.comments,
        })
    return pd.DataFrame(data)

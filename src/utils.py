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
        name_q = (filters or {}).get("name") or ""
        status_q = (filters or {}).get("status") or "All"
        if name_q:
            q = q.filter(Collateral.customer_name.ilike(f"%{name_q}%"))
        if status_q and status_q != "All":
            q = q.filter(Collateral.status == status_q)
    rows = q.order_by(Collateral.id.desc()).all()
    data = []
    for r in rows:
        intr = compute_interest(r.principal, r.interest_rate_pa, r.start_date, r.end_date)
        data.append({
            "ID": r.id,
            "Item Status": r.status,
            "Date": r.created_on,
            "Name": r.customer_name,
            "Item Name": r.item,
            "Weight": r.weight_grams,
            "Amount": r.principal,
            "Phone Number": r.phone_number,
            "Date Of Item Received": r.received_date,
            "Amount Received": r.amount_received,
            "Interest Rate (% p.a.)": r.interest_rate_pa,
            "Start Date": r.start_date,
            "End Date": r.end_date,
            "Accrued Interest": intr,
            "Amount Due": amount_due(r.principal, intr),
            "Comments": r.comments,
        })
    return pd.DataFrame(data)

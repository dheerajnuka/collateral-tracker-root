from datetime import date
import pandas as pd
import streamlit as st
from sqlalchemy.orm import Session
from .models import Collateral

STATUS_OPTIONS = ["", "Taken", "ReWrite", "Sold"]

@st.cache_data(show_spinner=False)
def _df_style(df: pd.DataFrame) -> pd.DataFrame:
    return df

def duration_ymd(start: date, end: date) -> tuple[int, int, int]:
    y = end.year - start.year
    m = end.month - start.month
    d = end.day - start.day
    if d < 0:
        from datetime import timedelta
        prev_month_last_day = (end.replace(day=1) - timedelta(days=1)).day
        d += prev_month_last_day
        m -= 1
    if m < 0:
        m += 12
        y -= 1
    return y, m, d

def human_duration(start: date, end: date) -> str:
    y, m, d = duration_ymd(start, end)
    parts = []
    if y:
        parts.append(f"{y} year{'s' if y != 1 else ''}")
    if m:
        parts.append(f"{m} month{'s' if m != 1 else ''}")
    if d or not parts:
        parts.append(f"{d} day{'s' if d != 1 else ''}")
    return " ".join(parts)

def compute_interest(principal: float, rate_percent_pa: float, start: date, end: date | None = None) -> float:
    """Interest: 2% per month on principal, prorated by days/30. If end is None, use today."""
    if end is None:
        end = date.today()
    if end < start:
        return 0.0
    y, m, d = duration_ymd(start, end)
    months_total = y * 12 + m + (d / 30.0)
    interest = float(principal) * 0.02 * months_total
    return round(interest, 2)

def amount_due(principal: float, accrued_interest: float) -> float:
    return round(principal + accrued_interest, 2)

def get_df(session: Session, filters: dict | None = None) -> pd.DataFrame:
    q = session.query(Collateral)
    if filters:
        name_q = (filters or {}).get("name") or ""
        status_q = (filters or {}).get("status") or "All"
        # if name_q:
            # q = q.filter(Collateral.customer_name.ilike(f"%{name_q}%"))
            
        if name_q:
            q = q.filter(or_(
                Collateral.customer_name.ilike(f"%{name_q}%"),
                Collateral.phone_number.ilike(f"%{name_q}%")
            ))

        if status_q and status_q != "All":
            q = q.filter(Collateral.status == status_q)
    rows = q.order_by(Collateral.id.desc()).all()
    data = []
    for r in rows:
        intr = compute_interest(r.principal, r.interest_rate_pa, r.start_date, r.received_date)
        data.append({
            "ID": r.id,
            "Item Status": r.status,
            "Date": r.created_on,
            "Name": r.customer_name,
            "Item Name": r.item,
            "Weight": r.weight_grams,
            "Amount": r.principal,
            "Amount Received": r.amount_received,
            "Phone Number": r.phone_number,
            "Date Of Item Received": r.received_date,
            "Interest Rate (% p.a.)": r.interest_rate_pa,
            "Start Date": r.start_date,
            # no End Date column shown
            "Accrued Interest": intr,
            "Duration": human_duration(r.start_date, r.received_date or date.today()),
            "Amount Due": amount_due(r.principal, intr),
            "Comments": r.comments,
        })
    return pd.DataFrame(data)

def safe_rerun():
    """Call st.rerun() if available; otherwise fall back to st.experimental_rerun()."""
    try:
        if hasattr(st, "rerun"):
            st.rerun()
        else:
            st.experimental_rerun()
    except Exception:
        try:
            st.experimental_rerun()
        except Exception:
            pass

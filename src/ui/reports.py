import streamlit as st
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Collateral
from ..utils import get_df

def reports_view(session: Session):
    st.subheader("📈 Quick Stats")
    s = session
    total = s.query(func.count(Collateral.id)).scalar() or 0
    active = s.query(func.count(Collateral.id)).filter(Collateral.status == "Active").scalar() or 0
    closed = s.query(func.count(Collateral.id)).filter(Collateral.status == "Closed").scalar() or 0
    overdue = s.query(func.count(Collateral.id)).filter(Collateral.status == "Overdue").scalar() or 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", f"{total}")
    c2.metric("Active", f"{active}")
    c3.metric("Closed", f"{closed}")
    c4.metric("Overdue", f"{overdue}")

    df = get_df(session, {})
    if not df.empty:
        # align with the new column names; fall back if running older dataframes
        cols = []
        cols.append("Item Status" if "Item Status" in df.columns else ("Status" if "Status" in df.columns else None))
        cols.append("Amount" if "Amount" in df.columns else ("Principal" if "Principal" in df.columns else None))
        for k in ["Accrued Interest", "Amount Due"]:
            if k in df.columns:
                cols.append(k)
        cols = [c for c in cols if c]
        if cols:
            st.dataframe(df[cols], use_container_width=True, hide_index=True)
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No data yet.")

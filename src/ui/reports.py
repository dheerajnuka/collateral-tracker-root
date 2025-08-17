import streamlit as st
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Collateral
from ..utils import get_df

def reports_view(session: Session):
    st.subheader("📈 Quick Stats")
    s = session
    total = s.query(func.count(Collateral.id)).scalar() or 0
    blank = s.query(func.count(Collateral.id)).filter((Collateral.status == "") | (Collateral.status.is_(None))).scalar() or 0
    taken = s.query(func.count(Collateral.id)).filter(Collateral.status == "Taken").scalar() or 0
    rewrite = s.query(func.count(Collateral.id)).filter(Collateral.status == "ReWrite").scalar() or 0
    sold = s.query(func.count(Collateral.id)).filter(Collateral.status == "Sold").scalar() or 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total", f"{total}")
    c2.metric("Blank", f"{blank}")
    c3.metric("Taken", f"{taken}")
    c4.metric("ReWrite", f"{rewrite}")
    c5.metric("Sold", f"{sold}")

    df = get_df(session, {})
    if df is not None and not df.empty:
        cols = [c for c in ["Item Status", "Amount", "Accrued Interest", "Amount Due"] if c in df.columns]
        st.dataframe(df[cols] if cols else df, use_container_width=True, hide_index=True)
    else:
        st.info("No data yet.")

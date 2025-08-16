import streamlit as st
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Collateral
from ..utils import get_df

def reports_view(session: Session):
    st.subheader("📈 Quick Stats")
    s=session
    total=s.query(func.count(Collateral.id)).scalar() or 0
    active=s.query(func.count(Collateral.id)).filter(Collateral.status=="Active").scalar() or 0
    closed=s.query(func.count(Collateral.id)).filter(Collateral.status=="Closed").scalar() or 0
    overdue=s.query(func.count(Collateral.id)).filter(Collateral.status=="Overdue").scalar() or 0
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Total",f"{total}"); c2.metric("Active",f"{active}"); c3.metric("Closed",f"{closed}"); c4.metric("Overdue",f"{overdue}")
    df=get_df(session,{})
    if not df.empty:
        st.dataframe(df[["Status","Principal","Accrued Interest","Amount Due"]],use_container_width=True,hide_index=True)

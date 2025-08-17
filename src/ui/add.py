from datetime import date
import streamlit as st
from sqlalchemy.orm import Session
from ..models import Collateral

def add_form(session: Session):
    st.subheader("➕ Add New Entry")
    with st.form("add_entry"):
        c1, c2 = st.columns(2)
        with c1:
            customer_name = st.text_input("Name")
            phone_number = st.text_input("Phone Number")
            item = st.text_input("Item Name")
            weight = st.number_input("Weight (grams)", min_value=0.0, step=0.1, value=0.0)
            principal = st.number_input("Amount (Principal)", min_value=0.0, step=100.0)
        with c2:
            rate = st.number_input("Interest Rate (% p.a.)", min_value=0.0, step=0.1, value=2.0)
            start_dt = st.date_input("Start Date", value=date.today())
            received_date = st.date_input("Date Of Item Received", value=None)
            amount_received = st.number_input("Amount Received", min_value=0.0, step=100.0, value=0.0)
            status = st.selectbox("Item Status", ["Active", "Closed", "Overdue"], index=0)
        comments = st.text_area("Comments")
        end_dt = st.date_input("End Date (optional)", value=None)

        submitted = st.form_submit_button("💾 Save Entry", type="primary")
        if submitted:
            obj = Collateral(
                customer_name=customer_name.strip(),
                phone_number=phone_number.strip() or None,
                item=item.strip(),
                weight_grams=float(weight),
                principal=float(principal),
                interest_rate_pa=float(rate),
                start_date=start_dt,
                end_date=end_dt,
                status=status,
                comments=comments.strip() if comments else None,
                received_date=received_date,
                amount_received=float(amount_received) if amount_received else None,
            )
            session.add(obj)
            session.commit()
            st.success(f"Entry saved (ID #{obj.id}).")
            st.rerun()

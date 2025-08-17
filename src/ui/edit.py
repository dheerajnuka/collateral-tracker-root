from datetime import date
import streamlit as st
from sqlalchemy.orm import Session
from ..models import Collateral
from ..utils import compute_interest, amount_due, get_df

def edit_view(session: Session):
    st.subheader("✏️ Edit / Close / Delete")
    df_all = get_df(session)
    if df_all.empty:
        st.info("No records to edit.")
        return
    choices = df_all[["ID", "Name", "Item Name", "Item Status", "Amount Due"]].copy()
    choices["Label"] = choices.apply(lambda r: f"#{int(r['ID'])} • {r['Name']} • {r['Item Name']} • {r['Item Status']}", axis=1)
    selected_label = st.selectbox("Pick a record", choices["Label"].tolist())
    sel_id = int(selected_label.split("•")[0].strip().lstrip("#"))

    rec: Collateral | None = session.get(Collateral, sel_id)
    if not rec:
        st.error("Record not found.")
        return
    with st.form("edit_form"):
        c1, c2 = st.columns(2)
        with c1:
            customer_name = st.text_input("Name", value=rec.customer_name)
            phone_number = st.text_input("Phone Number", value=rec.phone_number or "")
            item = st.text_input("Item Name", value=rec.item)
            weight = st.number_input("Weight (grams)", min_value=0.0, step=0.1, value=float(rec.weight_grams or 0.0))
            principal = st.number_input("Amount (Principal)", min_value=0.0, step=100.0, value=float(rec.principal))
        with c2:
            rate = st.number_input("Interest Rate (% p.a.)", min_value=0.0, step=0.1, value=float(rec.interest_rate_pa))
            start_dt = st.date_input("Start Date", value=rec.start_date)
            end_dt = st.date_input("End Date (optional)", value=rec.end_date)
            status = st.selectbox("Item Status", ["", "Rewrite", "Sold", "Taken"], index=["", "Rewrite", "Sold", "Taken"].index(rec.status) if rec.status in ["", "Rewrite", "Sold", "Taken"] else 0)
            received_date = st.date_input("Date Of Item Received", value=rec.received_date)
            amount_received = st.number_input("Amount Received", min_value=0.0, step=100.0, value=float(rec.amount_received or 0.0))
        comments = st.text_area("Comments", value=rec.comments or "")

        intr = compute_interest(principal, rate, start_dt, end_dt if status=="Closed" else None)
        st.info(f"Accrued Interest: ₹{intr:,.2f} | Amount Due: ₹{amount_due(principal, intr):,.2f}")
        save_btn = st.form_submit_button("💾 Save Changes", type="primary")
        close_btn = st.form_submit_button("✅ Mark Closed")
        delete_btn = st.form_submit_button("🗑️ Delete")
    if save_btn:
        rec.customer_name = customer_name.strip()
        rec.phone_number = phone_number.strip() or None
        rec.item = item.strip()
        rec.weight_grams = float(weight)
        rec.principal = float(principal)
        rec.interest_rate_pa = float(rate)
        rec.start_date = start_dt
        rec.end_date = end_dt if status != "Active" else None
        rec.status = status
        rec.received_date = received_date
        rec.amount_received = float(amount_received) if amount_received else None
        rec.comments = comments.strip() if comments else None
        session.commit()
        st.success("Saved.")
        st.rerun()
    if close_btn:
        rec.status = "Closed"
        rec.end_date = rec.end_date or date.today()
        session.commit()
        st.success("Closed.")
        st.rerun()
    if delete_btn:
        session.delete(rec)
        session.commit()
        st.warning("Deleted.")
        st.rerun()

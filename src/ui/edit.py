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
    choices = df_all[["ID", "Customer", "Item", "Status", "Amount Due"]].copy()
    choices["Label"] = choices.apply(lambda r: f"#{int(r['ID'])} • {r['Customer']} • {r['Item']} • {r['Status']}", axis=1)
    selected_label = st.selectbox("Pick a record", choices["Label"].tolist())
    sel_id = int(selected_label.split("•")[0].strip().lstrip("#"))
    rec = session.get(Collateral, sel_id)
    if not rec:
        st.error("Record not found.")
        return
    with st.form("edit_form"):
        customer_name = st.text_input("Customer Name", value=rec.customer_name)
        item = st.text_input("Item", value=rec.item)
        principal = st.number_input("Principal Amount", min_value=0.0, step=100.0, value=float(rec.principal))
        rate = st.number_input("Interest Rate (% p.a.)", min_value=0.0, step=0.1, value=float(rec.interest_rate_pa))
        start_dt = st.date_input("Start Date", value=rec.start_date)
        end_dt = st.date_input("End Date (optional)", value=rec.end_date)
        status = st.selectbox("Status", ["Active", "Closed", "Overdue"], index=["Active", "Closed", "Overdue"].index(rec.status if rec.status in ["Active","Closed","Overdue"] else "Active"))
        comments = st.text_area("Comments", value=rec.comments or "")
        intr = compute_interest(principal, rate, start_dt, end_dt if status=="Closed" else None)
        st.info(f"Accrued Interest: ₹{intr:,.2f} | Amount Due: ₹{amount_due(principal, intr):,.2f}")
        save_btn = st.form_submit_button("💾 Save Changes", type="primary")
        close_btn = st.form_submit_button("✅ Mark Closed")
        delete_btn = st.form_submit_button("🗑️ Delete")
    if save_btn:
        rec.customer_name=customer_name.strip(); rec.item=item.strip(); rec.principal=float(principal); rec.interest_rate_pa=float(rate); rec.start_date=start_dt; rec.end_date=end_dt; rec.status=status; rec.comments=comments.strip() if comments else None; session.commit(); st.success("Saved."); st.rerun()
    if close_btn:
        rec.status="Closed"; rec.end_date=rec.end_date or date.today(); session.commit(); st.success("Closed."); st.rerun()
    if delete_btn:
        session.delete(rec); session.commit(); st.warning("Deleted."); st.rerun()

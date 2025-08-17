from datetime import date
import streamlit as st
from sqlalchemy.orm import Session
from ..models import Collateral
from ..utils import compute_interest, amount_due, get_df

STATUS_OPTIONS = ["", "Taken", "ReWrite", "Sold"]

def edit_view(session: Session):
    st.subheader("✏️ Edit / Delete (with Search)")

    with st.expander("🔎 Search Filters", expanded=True):
        q = st.text_input("Search by Name or Phone", key="edit_search_q")
        status_filter = st.selectbox("Status", ["All"] + STATUS_OPTIONS, index=0, key="edit_status_filter")

    # Server-side filter by name + status; phone filtered locally below
    df_all = get_df(session, {"name": q if q else "", "status": status_filter if status_filter != "All" else "All"})

    # Additional client-side phone filter
    if q:
        try:
            df_all = df_all[
                df_all.apply(
                    lambda r: (q.lower() in str(r.get("Name", "")).lower())
                              or (q.lower() in str(r.get("Phone Number", "")).lower()),
                    axis=1
                )
            ]
        except Exception:
            pass

    if df_all.empty:
        st.info("No matching records.")
        return

    needed_cols = ["ID", "Name", "Item Name", "Item Status", "Amount Due"]
    for c in needed_cols:
        if c not in df_all.columns:
            st.error(f"Missing column: {c}. Please refresh the app.")
            return

    choices = df_all[needed_cols].copy()
    choices["Label"] = choices.apply(lambda r: f"#{int(r['ID'])} • {r['Name']} • {r['Item Name']} • {r['Item Status']}", axis=1)
    selected_label = st.selectbox("Pick a record", choices["Label"].tolist(), key="edit_pick_record")
    sel_id = int(selected_label.split("•")[0].strip().lstrip("#"))

    rec: Collateral | None = session.get(Collateral, sel_id)
    if not rec:
        st.error("Record not found.")
        return

    # Unique keys per record to avoid duplicate element IDs
    k = lambda suffix: f"edit_{sel_id}_{suffix}"

    with st.form(k("form")):
        c1, c2 = st.columns(2)
        with c1:
            customer_name = st.text_input("Name", value=rec.customer_name, key=k("name"))
            phone_number = st.text_input("Phone Number", value=rec.phone_number or "", key=k("phone"))
            item = st.text_input("Item Name", value=rec.item, key=k("item"))
            weight = st.number_input("Weight (grams)", min_value=0.0, step=0.1, value=float(rec.weight_grams or 0.0), key=k("weight"))
            principal = st.number_input("Amount (Principal)", min_value=0.0, step=100.0, value=float(rec.principal), key=k("principal"))
        with c2:
            rate = st.number_input("Interest Rate (% p.a.)", min_value=0.0, step=0.1, value=float(rec.interest_rate_pa), key=k("rate"))
            start_dt = st.date_input("Start Date", value=rec.start_date, key=k("start"))
            end_dt = st.date_input("End Date (optional)", value=rec.end_date, key=k("end"))
            status = st.selectbox("Item Status", STATUS_OPTIONS, index=(STATUS_OPTIONS.index(rec.status) if rec.status in STATUS_OPTIONS else 0), key=k("status"))
            received_date = st.date_input("Date Of Item Received", value=rec.received_date, key=k("received"))
            amount_received = st.number_input("Amount Received", min_value=0.0, step=100.0, value=float(rec.amount_received or 0.0), key=k("amt_received"))
        comments = st.text_area("Comments", value=rec.comments or "", key=k("comments"))

        intr = compute_interest(principal, rate, start_dt, end_dt if status=="Sold" else None)
        st.info(f"Accrued Interest: ₹{intr:,.2f} | Amount Due: ₹{amount_due(principal, intr):,.2f}")
        save_btn = st.form_submit_button("💾 Save Changes", type="primary")
        sold_btn = st.form_submit_button("✅ Mark Sold")
        delete_btn = st.form_submit_button("🗑️ Delete")

    if save_btn:
        rec.customer_name = customer_name.strip()
        rec.phone_number = phone_number.strip() or None
        rec.item = item.strip()
        rec.weight_grams = float(weight)
        rec.principal = float(principal)
        rec.interest_rate_pa = float(rate)
        rec.start_date = start_dt
        rec.end_date = end_dt if status != "" else None
        rec.status = status
        rec.received_date = received_date
        rec.amount_received = float(amount_received) if amount_received else None
        rec.comments = comments.strip() if comments else None
        session.commit()
        st.success("Saved.")
        st.rerun()

    if sold_btn:
        rec.status = "Sold"
        rec.end_date = rec.end_date or date.today()
        session.commit()
        st.success("Marked as Sold.")
        st.rerun()

    if delete_btn:
        session.delete(rec)
        session.commit()
        st.warning("Deleted.")
        st.rerun()

import streamlit as st
from sqlalchemy.orm import Session
from ..utils import get_df, _df_style, safe_rerun
from ..models import Collateral

STATUS_OPTIONS = ["", "Taken", "ReWrite", "Sold"]

def list_view(session: Session):
    st.subheader("📋 Records — Search, Edit & Export")
    with st.expander("🔎 Search Filters", expanded=True):
        name_q = st.text_input("Search by Name", key="list_search_name")
        status_q = st.selectbox("Status", ["All"] + STATUS_OPTIONS, index=0, key="list_status_filter")

    df = get_df(session, filters={"name": name_q, "status": status_q})
    if df.empty:
        st.info("No records found.")
        return

    drop_cols = [c for c in ["Comments", "Amount Due"] if c in df.columns]
    show_df = df.drop(columns=drop_cols) if drop_cols else df

    show_cols = [c for c in [
        "ID","Item Status","Date","Name","Item Name","Weight","Amount","Amount Received",
        "Phone Number","Date Of Item Received","Interest Rate (% p.a.)","Start Date",
        "Accrued Interest","Duration"
    ] if c in show_df.columns]
    st.dataframe(_df_style(show_df[show_cols] if show_cols else show_df), use_container_width=True, hide_index=True)

    st.download_button("⬇️ Export CSV", data=df.to_csv(index=False).encode("utf-8"),
                       file_name="collateral_export.csv", mime="text/csv")

    st.markdown("---")
    st.subheader("✏️ Quick Edit Results")
    for _, row in df.iterrows():
        rec_id = int(row["ID"])
        with st.expander(f"#{rec_id} • {row['Name']} • {row['Item Name']} • {row['Item Status']}"):
            rec = session.get(Collateral, rec_id)
            if not rec:
                st.error("Record not found.")
                continue
            form_key = f"quick_edit_{rec_id}"
            with st.form(form_key):
                c1, c2 = st.columns(2)
                with c1:
                    name = st.text_input("Name", value=rec.customer_name, key=f"{form_key}_name")
                    phone = st.text_input("Phone Number", value=rec.phone_number or "", key=f"{form_key}_phone")
                    item = st.text_input("Item Name", value=rec.item, key=f"{form_key}_item")
                    weight = st.number_input("Weight (grams)", min_value=0.0, step=0.1, value=float(rec.weight_grams or 0.0), key=f"{form_key}_weight")
                    principal = st.number_input("Amount (Principal)", min_value=0.0, step=100.0, value=float(rec.principal), key=f"{form_key}_principal")
                with c2:
                    rate = st.number_input("Interest Rate (% p.a.)", min_value=0.0, step=0.1, value=float(rec.interest_rate_pa), key=f"{form_key}_rate")
                    start_dt = st.date_input("Start Date", value=rec.start_date, key=f"{form_key}_start")
                    received_date = st.date_input("Date Of Item Received", value=rec.received_date, key=f"{form_key}_received")
                    status = st.selectbox("Item Status", STATUS_OPTIONS, index=(STATUS_OPTIONS.index(rec.status) if rec.status in STATUS_OPTIONS else 0), key=f"{form_key}_status")
                    amount_received = st.number_input("Amount Received", min_value=0.0, step=100.0, value=float(rec.amount_received or 0.0), key=f"{form_key}_amt_received")
                save = st.form_submit_button("💾 Save", type="primary")
            if save:
                rec.customer_name = name.strip()
                rec.phone_number = phone.strip() or None
                rec.item = item.strip()
                rec.weight_grams = float(weight)
                rec.principal = float(principal)
                rec.interest_rate_pa = float(rate)
                rec.start_date = start_dt
                rec.received_date = received_date
                rec.end_date = received_date  # mirror
                rec.status = status
                rec.amount_received = float(amount_received)
                session.commit()
                st.success("Saved.")
                safe_rerun()

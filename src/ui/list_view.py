import streamlit as st
from sqlalchemy.orm import Session
from ..utils import get_df, _df_style
from ..models import Collateral

def list_view(session: Session):
    st.subheader("📋 Records — Search, Edit & Export")
    with st.expander("🔎 Search Filters", expanded=True):
        name_q = st.text_input("Search by Name")
        status_q = st.selectbox("Status", ["All", "Active", "Closed", "Overdue"], index=0)
    df = get_df(session, filters={"name": name_q, "status": status_q})
    if df.empty:
        st.info("No records found.")
        return
    st.dataframe(_df_style(df.drop(columns=["Comments"]) if "Comments" in df.columns else df), use_container_width=True, hide_index=True)
    st.download_button("⬇️ Export CSV", data=df.to_csv(index=False).encode("utf-8"), file_name="collateral_export.csv", mime="text/csv")

    st.markdown("---")
    st.subheader("✏️ Quick Edit Results")
    for _, row in df.iterrows():
        with st.expander(f"#{int(row['ID'])} • {row['Name']} • {row['Item Name']} • {row['Item Status']}"):
            rec = session.get(Collateral, int(row["ID"]))
            if not rec:
                st.error("Record not found.")
                continue
            with st.form(f"quick_edit_{int(row['ID'])}"):
                c1, c2 = st.columns(2)
                with c1:
                    name = st.text_input("Name", value=rec.customer_name)
                    phone = st.text_input("Phone Number", value=rec.phone_number or "")
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
                save = st.form_submit_button("💾 Save", type="primary")
            if save:
                rec.customer_name = name.strip()
                rec.phone_number = phone.strip() or None
                rec.item = item.strip()
                rec.weight_grams = float(weight)
                rec.principal = float(principal)
                rec.interest_rate_pa = float(rate)
                rec.start_date = start_dt
                rec.end_date = end_dt if status != "Active" else None
                rec.status = status
                rec.received_date = received_date
                rec.amount_received = float(amount_received) if amount_received else None
                session.commit()
                st.success("Saved.")
                st.rerun()

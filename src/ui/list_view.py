import streamlit as st
from sqlalchemy.orm import Session
from ..utils import get_df, _df_style, safe_rerun
from ..models import Collateral

STATUS_OPTIONS = ["", "Taken", "ReWrite", "Sold"]

def list_view(session: Session):
    st.subheader("📋 Records — Search, Edit & Export")

    # Search Filters
    with st.expander("🔎 Search Filters", expanded=True):
        name_q = st.text_input("Search by Name", key="list_search_name")
        status_q = st.selectbox("Status", ["All"] + STATUS_OPTIONS, index=0, key="list_status_filter")

    # Fetch filtered data
    df = get_df(session, filters={"name": name_q, "status": status_q})
    if df.empty:
        st.info("No records found.")
        return

    # Display filtered table
    drop_cols = [c for c in ["Comments", "Amount Due"] if c in df.columns]
    show_df = df.drop(columns=drop_cols) if drop_cols else df

    show_cols = [c for c in [
        "ID", "Item Status", "Date", "Name", "Item Name", "Weight", "Amount", "Amount Received",
        "Phone Number", "Date Of Item Received", "Interest Rate (% p.a.)", "Start Date",
        "Accrued Interest", "Duration"
    ] if c in show_df.columns]

    st.dataframe(_df_style(show_df[show_cols] if show_cols else show_df),
                 use_container_width=True, hide_index=True)

    st.download_button("⬇️ Export CSV", data=df.to_csv(index=False).encode("utf-8"),
                       file_name="collateral_export.csv", mime="text/csv")

    # Only show Quick Edit if filters are applied
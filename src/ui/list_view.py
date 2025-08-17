import streamlit as st
from sqlalchemy.orm import Session
from ..utils import get_df, _df_style

def list_view(session: Session):
    st.subheader("📋 Records — Search & Export")
    name_q = st.text_input("Search by Customer")
    status_q = st.selectbox("Status", ["All", "", "Taken", "ReWrite", "Sold"], index=0)
    df = get_df(session, filters={"name": name_q, "status": status_q})
    if df.empty:
        st.info("No records found.")
    else:
        st.dataframe(_df_style(df), use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Export CSV", data=csv, file_name="collateral_export.csv", mime="text/csv")

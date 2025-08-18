import streamlit as st
st.set_page_config(page_title="Collateral Tracker", page_icon="💼", layout="wide")

from src.db import SessionLocal, init_db
from src.ui.add import add_form
from src.ui.list_view import list_view
from src.ui.edit import edit_view
from src.ui.reports import reports_view

def header():
    st.title("💼 Collateral Tracker")
    st.caption("Track collateral, interest, receipts, and status — with inline and full edit.")

def main():
    header()
    init_db()
    session = SessionLocal()

    tab_add, tab_list, tab_edit, tab_reports = st.tabs(["Add Entry", "Records", "Edit", "Reports"])
    with tab_add:
        add_form(session)
    with tab_list:
        list_view(session)
    with tab_edit:
        edit_view(session)
    with tab_reports:
        reports_view(session)

if __name__ == "__main__":
    main()

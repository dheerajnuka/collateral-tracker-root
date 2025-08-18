import streamlit as st
from sqlalchemy import text
from ..db import engine, DB_URL

def diagnostics_view():
    st.subheader("🧪 Diagnostics")
    st.write("Check database connection and parsed URL info.")

    from sqlalchemy.engine.url import make_url
    try:
        url = make_url(DB_URL)
        safe = url.set(password="***" if url.password else None)
        st.code(str(safe))
        st.json({
            "drivername": url.drivername,
            "host": url.host,
            "port": url.port,
            "database": url.database,
            "username": url.username,
            "has_password": bool(url.password)
        })
    except Exception as e:
        st.warning("Could not parse DATABASE_URL")
        st.exception(e)

    if st.button("Test connection"):
        try:
            with engine.connect() as conn:
                one = conn.execute(text("select 1")).scalar()
            st.success(f"Connected OK (select 1 -> {one})")
        except Exception as e:
            st.error("Connection failed")
            st.exception(e)

# app.py
import streamlit as st

from app.db import get_connection
from app.schema import create_tables
from app.users import migrate_users
from app.datasets import load_datasets
from app.incidents import load_cyber_incidents
from app.tickets import load_tickets_csv


def init_database():
    """Create tables and load Week 8 CSV data once."""
    conn = get_connection()
    create_tables(conn)
    migrate_users(conn)
    load_datasets(conn)
    load_cyber_incidents(conn)
    load_tickets_csv(conn)
    conn.close()


# ---------- APP ENTRY ----------

st.set_page_config(
    page_title="Intelligence Platform",
    page_icon="📊",
    layout="wide",
)

# Initialise DB only once per session (simple guard)
if "db_initialised" not in st.session_state:
    init_database()
    st.session_state["db_initialised"] = True

# ---------- HOME PAGE UI ----------

st.title("📊 Intelligence Platform – Welcome")

# Professional banner image (royalty-free Unsplash URL)
st.image(
    "https://images.unsplash.com/photo-1531297484001-80022131f5a1",
    use_container_width=True,
    caption="Unified view across Cyber Incidents, Datasets, and IT Tickets.",
)

st.markdown(
    """
This is the **home page** of the Multi-Domain Intelligence Platform built with Streamlit.

The platform brings together three domains:

- 🛡️ **Cyber Incidents** – track and analyse security events  
- 📂 **Datasets** – manage metadata for analytical datasets  
- 🎫 **IT Tickets** – monitor IT support workload and status  

Use the navigation menu on the **left sidebar** to move around the app.
"""
)

st.divider()
st.subheader("Quick links")

#  NOTE: icons use real emojis
st.page_link("pages/Login.py", label="🔑 Login / Register")
st.page_link("pages/Dashboard_Cyber.py", label="🛡️ Cyber Incidents Dashboard")
st.page_link("pages/Dashboard_Datasets.py", label="📂 Datasets Dashboard")
st.page_link("pages/Dashboard_Tickets.py", label="🎫 IT Tickets Dashboard")
st.page_link("pages/AI_Assistant.py", label="🤖 AI Assistant (Gemini API)")

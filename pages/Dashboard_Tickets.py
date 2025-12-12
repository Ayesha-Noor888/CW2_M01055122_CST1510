# pages/Dashboard_Tickets.py
import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3  # <-- needed for catching UNIQUE constraint errors

from app.db import get_connection
from app.tickets import (
    get_tickets,
    create_ticket,
    update_ticket_status,
    delete_ticket,
)


def require_login(target_login_page: str = "pages/Login.py"):
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if not st.session_state.logged_in:
        st.error("You must be logged in to view this page.")
        if st.button("Go to Login"):
            st.switch_page(target_login_page)
        st.stop()


st.set_page_config(page_title="IT Tickets", page_icon="🎫", layout="wide")
require_login()

st.title("🎫 IT Tickets Dashboard")
st.caption(f"Logged in as **{st.session_state.username}**")

st.caption(
    """
This dashboard tracks IT support tickets raised by users.
It helps monitor ticket status, priority, and workload to ensure
issues are resolved efficiently and on time.
"""
)

st.info("Use the controls below to create, update, and monitor IT support tickets.")


conn = get_connection()
tickets_df = get_tickets(conn)
if tickets_df is None or tickets_df.empty:
    tickets_df = pd.DataFrame(
        columns=[
            "id",
            "ticket_id",
            "priority",
            "status",
            "category",
            "subject",
            "assigned_to",
        ]
    )

# ---- KPIs ----
st.subheader("Key Metrics")
c1, c2, c3 = st.columns(3)
total_tickets = len(tickets_df)
open_tickets = (tickets_df["status"] == "Open").sum() if "status" in tickets_df.columns else 0
high_priority = (tickets_df["priority"] == "High").sum() if "priority" in tickets_df.columns else 0

c1.metric("Total Tickets", total_tickets)
c2.metric("Open Tickets", open_tickets)
c3.metric("High Priority Tickets", high_priority)

st.divider()

left, right = st.columns([1, 2])

# ===== LEFT: CRUD =====
with left:
    st.subheader("Create New Ticket")

    ticket_id = st.text_input("Ticket ID", value="INC-001")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    status = st.selectbox("Status", ["Open", "In Progress", "Closed"])
    category = st.text_input("Category", value="Software")
    subject = st.text_input("Subject")
    description = st.text_area("Description")
    created_date = st.text_input("Created date (YYYY-MM-DD)", value="2024-11-25")
    resolved_date = st.text_input("Resolved date (optional)", value="")
    assigned_to = st.text_input("Assigned to", value=st.session_state.username or "")

    if st.button("Create Ticket"):
        if not ticket_id or not subject:
            st.warning("Ticket ID and Subject are required.")
        else:
            try:
                new_id = create_ticket(
                    conn,
                    ticket_id,
                    priority,
                    status,
                    category,
                    subject,
                    description,
                    created_date,
                    resolved_date or None,
                    assigned_to,
                )
            except sqlite3.IntegrityError:
                st.error(
                    "❌ This Ticket ID already exists in the system.\n\n"
                    "Please use a different, unique Ticket ID."
                )
            else:
                st.success(f"✅ Ticket created with internal ID {new_id}")
                tickets_df = get_tickets(conn)

    st.divider()
    st.subheader("Update / Delete Ticket")

    if not tickets_df.empty:
        selected_id = st.selectbox("Select Ticket (row ID)", tickets_df["id"].tolist())
        new_status = st.selectbox(
            "New status",
            ["Open", "In Progress", "Closed"],
            key="ticket_new_status",
        )

        u, d = st.columns(2)
        with u:
            if st.button("Update Ticket Status"):
                rows = update_ticket_status(conn, selected_id, new_status)
                if rows:
                    st.success("✅ Ticket status updated.")
                    tickets_df = get_tickets(conn)
                else:
                    st.error("Update failed.")
        with d:
            if st.button("Delete Ticket"):
                rows = delete_ticket(conn, selected_id)
                if rows:
                    st.success("🗑️ Ticket deleted.")
                    tickets_df = get_tickets(conn)
                else:
                    st.error("Delete failed.")
    else:
        st.info("No tickets available yet.")

# ===== RIGHT: TABLE + VISUALS =====
with right:
    st.subheader("Tickets Table")
    st.dataframe(tickets_df, use_container_width=True)

    st.divider()
    st.subheader("Visualisations")

    if not tickets_df.empty:
        if "priority" in tickets_df.columns:
            by_priority = tickets_df.groupby("priority")["id"].count().reset_index(name="count")
            fig1 = px.bar(by_priority, x="priority", y="count", title="Tickets by Priority")
            st.plotly_chart(fig1, use_container_width=True)

        if "status" in tickets_df.columns:
            by_status = tickets_df.groupby("status")["id"].count().reset_index(name="count")
            fig2 = px.bar(by_status, x="status", y="count", title="Tickets by Status")
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No data available for charts yet.")

st.divider()
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = "user"
    st.info("You have been logged out.")
    st.switch_page("pages/Login.py")

conn.close()

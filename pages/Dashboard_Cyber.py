# pages/Dashboard_Cyber.py
import streamlit as st
import pandas as pd
import plotly.express as px

from app.db import get_connection
from app.incidents import (
    create_incident,
    get_incidents,
    update_incident_status,
    delete_incident,
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


st.set_page_config(page_title="Cyber Incidents", page_icon="🛡", layout="wide")
require_login()

st.title("🛡 Cyber Incidents Dashboard")
st.caption(f"Logged in as **{st.session_state.username}**")

st.caption(
    """
This dashboard provides an overview of cybersecurity incidents recorded in the system.
It helps identify incident severity, trends, and potential threats so that security teams
can respond quickly and effectively.
"""
)

st.info("Use the controls below to explore incident severity, status, and trends.")


conn = get_connection()
incidents_df = get_incidents(conn)
if incidents_df is None or incidents_df.empty:
    incidents_df = pd.DataFrame(columns=["id", "timestamp", "incident_type", "severity", "status"])

# ---- KPIs ----
st.subheader("Key Metrics")
k1, k2, k3 = st.columns(3)

total_incidents = len(incidents_df)
open_incidents = (incidents_df["status"] == "Open").sum() if "status" in incidents_df.columns else 0
high_severity = (incidents_df["severity"] == "High").sum() if "severity" in incidents_df.columns else 0

k1.metric("Total Incidents", total_incidents)
k2.metric("Open Incidents", open_incidents)
k3.metric("High Severity Incidents", high_severity)

st.divider()

left, right = st.columns([1, 2])

# ===== LEFT: CRUD FORMS =====
with left:
    st.subheader("Create New Incident")

    ts = st.text_input("Timestamp", value="2024-11-25 10:00")
    inc_type = st.text_input("Incident type", value="Phishing")
    severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
    status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
    desc = st.text_area("Description")
    reported_by = st.text_input("Reported by", value=st.session_state.username or "")

    if st.button("Create Incident"):
        if not inc_type or not desc:
            st.warning("Incident type and description are required.")
        else:
            new_id = create_incident(conn, ts, inc_type, severity, status, desc, reported_by)
            st.success(f"Incident created with ID {new_id}")
            incidents_df = get_incidents(conn)

    st.divider()
    st.subheader("Update / Delete Incident")

    if not incidents_df.empty:
        selected_id = st.selectbox("Select Incident ID", incidents_df["id"].tolist())
        new_status = st.selectbox("New status", ["Open", "In Progress", "Resolved"], key="inc_new_status")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Update Status"):
                rows = update_incident_status(conn, selected_id, new_status)
                if rows:
                    st.success("Status updated.")
                    incidents_df = get_incidents(conn)
                else:
                    st.error("Update failed.")
        with c2:
            if st.button("Delete Incident"):
                rows = delete_incident(conn, selected_id)
                if rows:
                    st.success("Incident deleted.")
                    incidents_df = get_incidents(conn)
                else:
                    st.error("Delete failed.")
    else:
        st.info("No incidents to update yet.")

# ===== RIGHT: TABLE + VISUALS =====
with right:
    st.subheader("Incidents Table")
    st.dataframe(incidents_df, use_container_width=True)

    st.divider()
    st.subheader("Visualisations")

    if not incidents_df.empty:
        # Bar: by severity
        if "severity" in incidents_df.columns:
            by_severity = incidents_df.groupby("severity")["id"].count().reset_index(name="count")
            fig1 = px.bar(by_severity, x="severity", y="count", title="Incidents by Severity")
            st.plotly_chart(fig1, use_container_width=True)

        # Time series
        if "timestamp" in incidents_df.columns:
            tmp = incidents_df.copy()
            tmp["timestamp"] = pd.to_datetime(tmp["timestamp"], errors="coerce")
            tmp = tmp.dropna(subset=["timestamp"])
            if not tmp.empty:
                by_date = tmp.groupby(tmp["timestamp"].dt.date)["id"].count().reset_index(name="count")
                by_date.rename(columns={"timestamp": "date"}, inplace=True)
                fig2 = px.line(by_date, x="date", y="count", title="Incidents Over Time")
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

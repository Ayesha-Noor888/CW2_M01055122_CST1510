# pages/Dashboard_Datasets.py

import os

import streamlit as st
import pandas as pd
import plotly.express as px

from services.database_manager import DatabaseManager
from services.dataset_service import DatasetService
from models.dataset import Dataset


# ---------- LOGIN GUARD ----------

def require_login(target_login_page: str = "pages/Login.py"):
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "role" not in st.session_state:
        st.session_state.role = "user"

    if not st.session_state.logged_in:
        st.error("You must be logged in to view this page.")
        if st.button("Go to Login"):
            st.switch_page(target_login_page)
        st.stop()


# ---------- PAGE CONFIG ----------

st.set_page_config(page_title="Datasets", page_icon="📂", layout="wide")
require_login()

st.title("📂 Datasets Metadata Dashboard")
st.caption(f"Logged in as **{st.session_state.username}**")

st.caption(
    """
This dashboard manages and analyses datasets used across the platform.
It allows users to view dataset metadata, update record counts, and explore
data distribution using interactive visualisations.
"""
)

st.info("Use the controls below to manage datasets and analyse their statistics.")


# ---------- INITIALISE SERVICES (OOP) ----------

DB_PATH = "DATA/intelligence_platform.db"
db = DatabaseManager(DB_PATH)
dataset_service = DatasetService(db)

# Load all datasets via the service (returns List[Dataset])
datasets: list[Dataset] = dataset_service.get_all_datasets()

# Convert to DataFrame for visualisation
if datasets:
    datasets_df = pd.DataFrame([d.to_dict() for d in datasets])
else:
    datasets_df = pd.DataFrame(
        columns=[
            "id",
            "dataset_name",
            "category",
            "source",
            "last_updated",
            "record_count",
            "file_size_mb",
        ]
    )

# ---------- KPIs ----------

st.subheader("Key Metrics")
c1, c2, c3 = st.columns(3)

total_datasets = len(datasets_df)
total_records = int(datasets_df["record_count"].sum()) if "record_count" in datasets_df.columns else 0
avg_records = int(datasets_df["record_count"].mean()) if total_datasets > 0 else 0

c1.metric("Total Datasets", total_datasets)
c2.metric("Total Records", total_records)
c3.metric("Average Records per Dataset", avg_records)

st.divider()

left, right = st.columns([1, 2])

# ================= LEFT: CRUD (CREATE / UPDATE / DELETE) =================

with left:
    st.subheader("Add New Dataset")

    name = st.text_input("Dataset name")
    category = st.text_input("Category", value="General")
    source = st.text_input("Source", value="Unknown")
    last_updated = st.text_input("Last updated (YYYY-MM-DD)", value="2024-11-25")
    record_count = st.number_input("Record count", min_value=0, value=0, step=100)
    file_size_mb = st.number_input("File size (MB)", min_value=0.0, value=0.0, step=0.1)

    if st.button("Create Dataset"):
        if not name:
            st.warning("Dataset name is required.")
        else:
            new_id = dataset_service.create_dataset(
                name=name,
                category=category,
                source=source,
                last_updated=last_updated,
                record_count=record_count,
                file_size_mb=file_size_mb,
            )
            st.success(f"Dataset created with ID {new_id}")
            datasets = dataset_service.get_all_datasets()
            datasets_df = pd.DataFrame([d.to_dict() for d in datasets]) if datasets else datasets_df

    st.divider()
    st.subheader("Update / Delete Dataset")

    if not datasets_df.empty:
        selected_id = st.selectbox("Select Dataset ID", datasets_df["id"].tolist())
        new_count = st.number_input(
            "New record count",
            min_value=0,
            step=100,
            key="ds_new_count",
        )

        u, d = st.columns(2)

        with u:
            if st.button("Update Count"):
                rows = dataset_service.update_record_count(selected_id, new_count)
                if rows:
                    st.success("Record count updated.")
                    datasets = dataset_service.get_all_datasets()
                    datasets_df = pd.DataFrame([ds.to_dict() for ds in datasets])
                else:
                    st.error("Update failed.")

        with d:
            if st.button("Delete Dataset"):
                rows = dataset_service.delete_dataset(selected_id)
                if rows:
                    st.success("Dataset deleted.")
                    datasets = dataset_service.get_all_datasets()
                    datasets_df = pd.DataFrame([ds.to_dict() for ds in datasets]) if datasets else datasets_df.iloc[0:0]
                else:
                    st.error("Delete failed.")
    else:
        st.info("No datasets available yet.")

# ================= RIGHT: TABLE + VISUALS =================

with right:
    st.subheader("Datasets Table")
    st.dataframe(datasets_df, use_container_width=True)

    st.divider()
    st.subheader("Visualisations")

    if not datasets_df.empty:
        if "category" in datasets_df.columns:
            by_category = (
                datasets_df.groupby("category")["record_count"].sum().reset_index()
            )
            fig1 = px.bar(
                by_category,
                x="category",
                y="record_count",
                title="Records by Category",
            )
            st.plotly_chart(fig1, use_container_width=True)

        if "file_size_mb" in datasets_df.columns:
            fig2 = px.scatter(
                datasets_df,
                x="record_count",
                y="file_size_mb",
                hover_name="dataset_name",
                title="Record Count vs File Size",
            )
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

# Close DB connection nicely
db.close()

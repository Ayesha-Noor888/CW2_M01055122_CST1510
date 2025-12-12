# pages/Login.py

import streamlit as st

from services.database_manager import DatabaseManager
from services.auth_manager import AuthManager

# -------------------------------------------------------------------
# Page config
# -------------------------------------------------------------------
st.set_page_config(page_title="Login / Register", page_icon="🔑", layout="centered")

# -------------------------------------------------------------------
# Create shared DB + Auth objects for this page (OOP style)
# DatabaseManager() will default to DATA/intelligence_platform.db
# as defined in services/database_manager.py
# -------------------------------------------------------------------
db_manager = DatabaseManager()
auth_manager = AuthManager(db_manager)


# -------------------------------------------------------------------
# SMALL HELPER: LOGIN GUARD (USED BY DASHBOARDS TOO)
# -------------------------------------------------------------------
def require_login(target_login_page: str = "pages/Login.py"):
    """
    Redirect user to login page if not authenticated.
    You can import or copy this function into each dashboard file.
    """
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


# -------------------------------------------------------------------
# INITIALISE SESSION STATE
# -------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = "user"

st.title("🔐 Intelligence Platform – Login / Register")

# If already logged in, show quick links
if st.session_state.logged_in:
    st.success(
        f"Already logged in as **{st.session_state.username}** "
        f"(role: {st.session_state.role})."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.page_link("pages/Dashboard_Cyber.py", label="🛡 Cyber Incidents", icon="🛡️")
    with col2:
        st.page_link("pages/Dashboard_Datasets.py", label="📂 Datasets", icon="📂")
    with col3:
        st.page_link("pages/Dashboard_Tickets.py", label="🎫 Tickets", icon="🎫")

    st.divider()

# -------------------------------------------------------------------
# TABS: LOGIN / REGISTER
# -------------------------------------------------------------------
tab_login, tab_register = st.tabs(["Login", "Register"])

# ----- LOGIN TAB ----------------------------------------------------
with tab_login:
    st.subheader("Login")

    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log in", type="primary"):
        # Use AuthManager.check_credentials (OOP)
        ok, role = auth_manager.check_credentials(login_username, login_password)

        if ok:
            st.session_state.logged_in = True
            st.session_state.username = login_username
            st.session_state.role = role or "user"

            st.success(f"Welcome back, {login_username}! 🎉")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.page_link("pages/Dashboard_Cyber.py", label="🛡 Cyber Incidents", icon="🛡️")
            with col2:
                st.page_link("pages/Dashboard_Datasets.py", label="📂 Datasets", icon="📂")
            with col3:
                st.page_link("pages/Dashboard_Tickets.py", label="🎫 Tickets", icon="🎫")
        else:
            st.error("Invalid username or password.")

# ----- REGISTER TAB -------------------------------------------------
with tab_register:
    st.subheader("Register")

    new_username = st.text_input("Choose a username", key="register_username")
    new_password = st.text_input("Choose a password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm password", type="password", key="register_confirm")

    if st.button("Create account"):
        if not new_username or not new_password:
            st.warning("Please fill in all fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            # Use AuthManager.register_user instead of direct SQL
            created = auth_manager.register_user(new_username, new_password)
            if not created:
                st.error("Username already exists. Please choose another one.")
            else:
                st.success("Account created successfully! You can now log in from the Login tab.")
                st.info("Tip: go to the Login tab and sign in with your new account.")

# -------------------------------------------------------------------
# LOG OUT
# -------------------------------------------------------------------
st.divider()
if st.session_state.logged_in and st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = "user"
    st.info("You have been logged out.")

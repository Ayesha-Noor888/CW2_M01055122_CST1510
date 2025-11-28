# pages/Login.py
import streamlit as st
import bcrypt

from app.db import get_connection

st.set_page_config(page_title="Login / Register", page_icon="🔑", layout="centered")


# ---------- SMALL HELPER: LOGIN GUARD (USED BY DASHBOARDS TOO) ----------
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


# ---------- DB HELPERS FOR USERS ----------

def get_user_by_username(username: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, username, password_hash, role FROM users WHERE username = ?",
        (username,),
    )
    row = cur.fetchone()
    conn.close()
    return row  # None or (id, username, password_hash, role)


def register_user(username: str, password: str, role: str = "user") -> bool:
    # Check if user exists
    existing = get_user_by_username(username)
    if existing is not None:
        return False

    # Hash password
    pw_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(pw_bytes, bcrypt.gensalt())

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, hashed.decode("utf-8"), role),
    )
    conn.commit()
    conn.close()
    return True


def check_credentials(username: str, password: str):
    row = get_user_by_username(username)
    if row is None:
        return False, None

    _, db_username, db_hash, role = row
    pw_bytes = password.encode("utf-8")
    hash_bytes = db_hash.encode("utf-8")

    if bcrypt.checkpw(pw_bytes, hash_bytes):
        return True, role
    return False, None


# ---------- INITIALISE SESSION STATE ----------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = "user"

st.title("🔐 Intelligence Platform – Login / Register")

# If already logged in, show quick links
if st.session_state.logged_in:
    st.success(f"Already logged in as **{st.session_state.username}** (role: {st.session_state.role}).")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.page_link("pages/Dashboard_Cyber.py", label="🛡 Cyber Incidents", icon="🛡️")
    with col2:
        st.page_link("pages/Dashboard_Datasets.py", label="📂 Datasets", icon="📂")
    with col3:
        st.page_link("pages/Dashboard_Tickets.py", label="🎫 Tickets", icon="🎫")

    st.divider()

# ---------- TABS: LOGIN / REGISTER ----------
tab_login, tab_register = st.tabs(["Login", "Register"])

# ----- LOGIN TAB -----
with tab_login:
    st.subheader("Login")

    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log in", type="primary"):
        ok, role = check_credentials(login_username, login_password)
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

# ----- REGISTER TAB -----
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
            created = register_user(new_username, new_password)
            if not created:
                st.error("Username already exists. Please choose another one.")
            else:
                st.success("Account created successfully! You can now log in from the Login tab.")
                st.info("Tip: go to the Login tab and sign in with your new account.")


st.divider()
if st.session_state.logged_in and st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = "user"
    st.info("You have been logged out.")

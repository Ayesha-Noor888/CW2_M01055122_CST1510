# main.py
from app.db import get_connection
from app.schema import create_tables
from app.users import migrate_users
from app.datasets import load_datasets
from app.incidents import load_cyber_incidents, create_incident, get_incidents
from app.tickets import load_tickets_csv


def setup_database():
    conn = get_connection()
    create_tables(conn)
    migrate_users(conn)
    load_datasets(conn)
    load_cyber_incidents(conn)   # <-- NEW: load incidents from CSV
    load_tickets_csv(conn)
    conn.close()


def demo():
    conn = get_connection()
    # optional extra test insert
    create_incident(conn, "2024-11-01", "Phishing", "High", "Open", "Test", "admin")
    print(get_incidents(conn))
    conn.close()


if __name__ == "__main__":
    # Step 1 – create tables + load all CSV data
    setup_database()

    # Step 2 – (optional) a quick demo insert + print
    demo()

    # Or, if you prefer a simple print instead of demo(), use this:
    # conn = get_connection()
    # incidents_df = get_incidents(conn)
    # print(incidents_df.head())
    # conn.close()


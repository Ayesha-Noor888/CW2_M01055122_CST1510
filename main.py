# main.py

from app.data.db import get_connection
from app.data.schema import create_tables
from app.data.users import migrate_users
from app.data.datasets import load_datasets
from app.data.incidents import load_cyber_incidents, create_incident, get_incidents
from app.data.tickets import load_tickets_csv


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
    setup_database()
    demo()

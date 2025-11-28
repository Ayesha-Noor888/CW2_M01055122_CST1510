# app/data/incidents.py

import pandas as pd
from app.db import DATA_DIR


def load_cyber_incidents(conn):
    """Load cyber_incidents.csv into cyber_incidents table."""
    path = DATA_DIR / "cyber_incidents.csv"
    if not path.exists():
        print("cyber_incidents.csv not found, skipping incidents load")
        return 0

    df = pd.read_csv(path)

    cur = conn.cursor()
    cur.execute("PRAGMA table_info(cyber_incidents)")
    cols = [row[1] for row in cur.fetchall()]

    common = [c for c in df.columns if c in cols]
    if not common:
        print("No matching columns for cyber_incidents.csv -> cyber_incidents, skipping")
        return 0

    df = df[common]
    df.to_sql("cyber_incidents", conn, if_exists="append", index=False)
    print(f"Loaded {len(df)} cyber incident rows")
    return len(df)


# --- existing CRUD functions below ---

def create_incident(conn, timestamp, incident_type, severity, status, description, reported_by=None):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO cyber_incidents
        (timestamp, incident_type, severity, status, description, reported_by)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (timestamp, incident_type, severity, status, description, reported_by))
    conn.commit()
    return cur.lastrowid


def get_incidents(conn):
    query = "SELECT id, incident_type, severity, status FROM cyber_incidents"
    return pd.read_sql_query(query, conn)


def update_incident_status(conn, incident_id, new_status):
    cur = conn.cursor()
    cur.execute(
        "UPDATE cyber_incidents SET status = ? WHERE id = ?",
        (new_status, incident_id)
    )
    conn.commit()
    return cur.rowcount


def delete_incident(conn, incident_id):
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM cyber_incidents WHERE id = ?",
        (incident_id,)
    )
    conn.commit()
    return cur.rowcount

import sqlite3
from pathlib import Path

import pandas as pd

# ---------- PATHS ----------

DATA_DIR = Path("DATA")
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "intelligence_platform.db"


# ---------- BASIC DB HELPER ----------

def get_connection():
    """Return a new SQLite connection to the Week 8 database."""
    return sqlite3.connect(str(DB_PATH))


# ---------- TABLE CREATION ----------

def create_tables(conn):
    cur = conn.cursor()

    # users table (for auth)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # cyber incidents (security domain)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cyber_incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            incident_type TEXT,
            severity TEXT,
            status TEXT,
            description TEXT,
            reported_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # datasets metadata (data science domain)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS datasets_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataset_name TEXT,
            category TEXT,
            source TEXT,
            last_updated TEXT,
            record_count INTEGER,
            file_size_mb REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # IT tickets (IT operations domain)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS it_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT UNIQUE NOT NULL,
            priority TEXT,
            status TEXT,
            category TEXT,
            subject TEXT,
            description TEXT,
            created_date TEXT,
            resolved_date TEXT,
            assigned_to TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    print("Tables created (users, cyber_incidents, datasets_metadata, it_tickets)")


# ---------- MIGRATE USERS FROM Week 7 FILE ----------

def migrate_users(conn):
    """
    Migrate users from DATA/users.txt into the users table.

    Expected format (with or without header):
        username,password_hash,role
    """
    path = DATA_DIR / "users.txt"
    if not path.exists():
        print("users.txt not found in DATA/, skipping user migration")
        return

    cur = conn.cursor()
    migrated = 0

    with open(path, "r", encoding="utf-8") as f:
        first = f.readline().strip()

        # skip header if present
        if first.lower().startswith("username"):
            line = f.readline().strip()
        else:
            line = first

        while line:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 2:
                username = parts[0]
                password_hash = parts[1]
                role = parts[2] if len(parts) >= 3 else "user"

                cur.execute(
                    "INSERT OR IGNORE INTO users (username, password_hash, role) "
                    "VALUES (?, ?, ?)",
                    (username, password_hash, role)
                )
                if cur.rowcount > 0:
                    migrated += 1

            line = f.readline().strip()

    conn.commit()
    print(f"Users migrated from file: {migrated}")


# ---------- CSV LOADING HELPERS ----------

def load_csv_to_table(conn, csv_path: Path, table_name: str):
    """
    Load a CSV into a table using pandas.
    For datasets_metadata, also supports the older header format
    (dataset_id,name,rows,columns,uploaded_by,upload_date) by mapping it.
    """
    if not csv_path.exists():
        print(f"{csv_path.name} not found, skipping")
        return 0

    df = pd.read_csv(csv_path)

    # Special handling for datasets_metadata so old CSV still works
    if table_name == "datasets_metadata":
        # if it already has correct headers, do nothing
        if "dataset_name" not in df.columns and "name" in df.columns:
            # Old structure: dataset_id,name,rows,columns,uploaded_by,upload_date
            mapped = pd.DataFrame()
            mapped["dataset_name"] = df["name"]
            mapped["category"] = "General"
            mapped["source"] = df.get("uploaded_by", "Unknown")
            mapped["last_updated"] = df.get("upload_date", "")
            mapped["record_count"] = df.get("rows", 0)

            # use 'columns' as a rough proxy for size
            if "columns" in df.columns:
                mapped["file_size_mb"] = df["columns"]
            else:
                mapped["file_size_mb"] = 0.0

            df = mapped

    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table_name})")
    cols = [row[1] for row in cur.fetchall()]
    common = [c for c in df.columns if c in cols]

    if not common:
        print(f"No matching columns for {csv_path.name} -> {table_name}, skipping")
        return 0

    df = df[common]
    df.to_sql(table_name, conn, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into {table_name} (cols: {common})")
    return len(df)


def load_all_domain_data(conn):
    total = 0
    total += load_csv_to_table(conn, DATA_DIR / "cyber_incidents.csv", "cyber_incidents")
    total += load_csv_to_table(conn, DATA_DIR / "datasets_metadata.csv", "datasets_metadata")
    total += load_csv_to_table(conn, DATA_DIR / "it_tickets.csv", "it_tickets")
    print(f"Total rows loaded from CSVs: {total}")


# ---------- CRUD: CYBER INCIDENTS ----------

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


# ---------- CRUD: DATASETS METADATA ----------

def create_dataset(conn, dataset_name, category, source,
                   last_updated, record_count, file_size_mb):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO datasets_metadata
        (dataset_name, category, source, last_updated, record_count, file_size_mb)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (dataset_name, category, source, last_updated, record_count, file_size_mb))
    conn.commit()
    return cur.lastrowid


def get_datasets(conn):
    query = "SELECT id, dataset_name, category, record_count FROM datasets_metadata"
    return pd.read_sql_query(query, conn)


def update_dataset_record_count(conn, dataset_id, new_count):
    cur = conn.cursor()
    cur.execute(
        "UPDATE datasets_metadata SET record_count = ? WHERE id = ?",
        (new_count, dataset_id)
    )
    conn.commit()
    return cur.rowcount


def delete_dataset(conn, dataset_id):
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM datasets_metadata WHERE id = ?",
        (dataset_id,)
    )
    conn.commit()
    return cur.rowcount


# ---------- CRUD: IT TICKETS ----------

def create_ticket(conn, ticket_id, priority, status,
                  category, subject, description,
                  created_date, resolved_date, assigned_to):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO it_tickets
        (ticket_id, priority, status, category, subject, description,
         created_date, resolved_date, assigned_to)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ticket_id, priority, status, category, subject, description,
          created_date, resolved_date, assigned_to))
    conn.commit()
    return cur.lastrowid


def get_tickets(conn):
    query = "SELECT id, ticket_id, priority, status, assigned_to FROM it_tickets"
    return pd.read_sql_query(query, conn)


def update_ticket_status(conn, row_id, new_status):
    cur = conn.cursor()
    cur.execute(
        "UPDATE it_tickets SET status = ? WHERE id = ?",
        (new_status, row_id)
    )
    conn.commit()
    return cur.rowcount


def delete_ticket(conn, row_id):
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM it_tickets WHERE id = ?",
        (row_id,)
    )
    conn.commit()
    return cur.rowcount


# ---------- SETUP + DEMO ----------

def setup_database():
    conn = get_connection()
    print("DB path:", DB_PATH.resolve())

    create_tables(conn)
    migrate_users(conn)
    load_all_domain_data(conn)

    # Simple row counts for report
    cur = conn.cursor()
    for table in ["users", "cyber_incidents", "datasets_metadata", "it_tickets"]:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"{table}: {count} rows")

    conn.close()


def demo_crud():
    conn = get_connection()

    print("\n--- CRUD DEMO: CYBER INCIDENTS ---")
    inc_id = create_incident(
        conn,
        "2024-11-21T10:00:00Z",
        "Phishing",
        "High",
        "Open",
        "Test incident from Week 8 script",
        "alice"
    )
    print("After create:")
    print(get_incidents(conn))

    update_incident_status(conn, inc_id, "Resolved")
    print("After update:")
    print(get_incidents(conn))

    delete_incident(conn, inc_id)
    print("After delete:")
    print(get_incidents(conn))

    print("\n--- CRUD DEMO: DATASETS ---")
    ds_id = create_dataset(
        conn,
        "Week8_Test_Dataset",
        "Logs",
        "System A",
        "2024-11-20",
        1000,
        10.5
    )
    print("After create:")
    print(get_datasets(conn))

    update_dataset_record_count(conn, ds_id, 2000)
    print("After update:")
    print(get_datasets(conn))

    delete_dataset(conn, ds_id)
    print("After delete:")
    print(get_datasets(conn))

    print("\n--- CRUD DEMO: IT TICKETS ---")
    t_id = create_ticket(
        conn,
        "INC-W8-001",
        "Medium",
        "Open",
        "Software",
        "Demo ticket",
        "Test description",
        "2024-11-21",
        None,
        "tech1"
    )
    print("After create:")
    print(get_tickets(conn))

    update_ticket_status(conn, t_id, "Closed")
    print("After update:")
    print(get_tickets(conn))

    delete_ticket(conn, t_id)
    print("After delete:")
    print(get_tickets(conn))

    conn.close()


if __name__ == "__main__":
    setup_database()
    demo_crud()

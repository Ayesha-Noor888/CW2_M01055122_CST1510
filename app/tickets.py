from pathlib import Path
import pandas as pd

DATA_DIR = Path("DATA")


# ---------- CSV LOAD FOR WEEK 8 SETUP ----------

def load_tickets_csv(conn):
    """
    Load IT tickets from DATA/it_tickets.csv into the it_tickets table.

    - Only loads if the table is currently empty.
    - Prevents UNIQUE constraint errors on ticket_id when main.py is run multiple times.
    """
    path = DATA_DIR / "it_tickets.csv"
    if not path.exists():
        print("it_tickets.csv not found in DATA/, skipping tickets load")
        return 0

    cur = conn.cursor()
    # Check if table already has data
    cur.execute("SELECT COUNT(*) FROM it_tickets")
    existing = cur.fetchone()[0]

    if existing > 0:
        print(f"it_tickets already has {existing} rows – skipping CSV load")
        return 0

    df = pd.read_csv(path)
    df.to_sql("it_tickets", conn, if_exists="append", index=False)
    print(f"Loaded {len(df)} ticket rows")
    return len(df)


# ---------- CRUD HELPERS USED BY STREAMLIT / WEEK 8 DEMO ----------

def create_ticket(conn, ticket_id, priority, status,
                  category, subject, description,
                  created_date, resolved_date, assigned_to):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO it_tickets
        (ticket_id, priority, status, category, subject, description,
         created_date, resolved_date, assigned_to)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (ticket_id, priority, status, category, subject,
         description, created_date, resolved_date, assigned_to),
    )
    conn.commit()
    return cur.lastrowid


def get_tickets(conn):
    query = "SELECT id, ticket_id, priority, status, assigned_to FROM it_tickets"
    return pd.read_sql_query(query, conn)


def update_ticket_status(conn, row_id, new_status):
    cur = conn.cursor()
    cur.execute(
        "UPDATE it_tickets SET status = ? WHERE id = ?",
        (new_status, row_id),
    )
    conn.commit()
    return cur.rowcount


def delete_ticket(conn, row_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM it_tickets WHERE id = ?", (row_id,))
    conn.commit()
    return cur.rowcount

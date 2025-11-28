from pathlib import Path
import pandas as pd

DATA_DIR = Path("DATA")

def load_datasets(conn):
    csv_path = DATA_DIR / "datasets_metadata.csv"
    if not csv_path.exists():
        print("datasets_metadata.csv not found")
        return

    df = pd.read_csv(csv_path)

    # detect OLD format and convert
    if "dataset_name" not in df.columns and "name" in df.columns:
        mapped = pd.DataFrame()
        mapped["dataset_name"] = df["name"]
        mapped["category"] = "General"
        mapped["source"] = df.get("uploaded_by", "Unknown")
        mapped["last_updated"] = df.get("upload_date", "")
        mapped["record_count"] = df.get("rows", 0)
        mapped["file_size_mb"] = df.get("columns", 0)
        df = mapped

    df.to_sql("datasets_metadata", conn, if_exists="append", index=False)
    print(f"Loaded {len(df)} dataset rows")

# ---------- WEEK 9 HELPER FUNCTIONS FOR STREAMLIT DASHBOARD ----------

def get_datasets(conn):
    """
    Return all dataset rows as a DataFrame for the Streamlit dashboard.
    """
    query = """
        SELECT
            id,
            dataset_name,
            category,
            source,
            last_updated,
            record_count,
            file_size_mb
        FROM datasets_metadata
        ORDER BY id;
    """
    return pd.read_sql_query(query, conn)


def create_dataset(conn, dataset_name, category, source, last_updated, record_count, file_size_mb):
    """
    Insert a new dataset into datasets_metadata.
    """
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO datasets_metadata (
            dataset_name,
            category,
            source,
            last_updated,
            record_count,
            file_size_mb
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (dataset_name, category, source, last_updated, record_count, file_size_mb),
    )
    conn.commit()


def update_dataset(conn, dataset_id, dataset_name, category, source, last_updated, record_count, file_size_mb):
    """
    Update an existing dataset row in datasets_metadata.
    """
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE datasets_metadata
        SET
            dataset_name = ?,
            category = ?,
            source = ?,
            last_updated = ?,
            record_count = ?,
            file_size_mb = ?
        WHERE id = ?
        """,
        (dataset_name, category, source, last_updated, record_count, file_size_mb, dataset_id),
    )
    conn.commit()


def delete_dataset(conn, dataset_id):
    """
    Delete a dataset from datasets_metadata by id.
    """
    cur = conn.cursor()
    cur.execute("DELETE FROM datasets_metadata WHERE id = ?", (dataset_id,))
    conn.commit()


def get_dataset_stats(conn):
    """
    Aggregate stats for the datasets dashboard.
    - number of datasets per category
    - total records per category
    - total size in MB per category
    """
    query = """
        SELECT
            category,
            COUNT(*) AS dataset_count,
            SUM(record_count) AS total_records,
            SUM(file_size_mb) AS total_size_mb
        FROM datasets_metadata
        GROUP BY category
        ORDER BY dataset_count DESC;
    """
    return pd.read_sql_query(query, conn)


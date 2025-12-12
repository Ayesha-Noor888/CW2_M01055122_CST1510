# services/dataset_service.py

from typing import List, Optional

from services.database_manager import DatabaseManager
from models.dataset import Dataset


class DatasetService:
    """
    Service class that hides all SQL for datasets_metadata.
    The Streamlit page only talks to this class, not directly to SQL.
    """

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    # --------- READ ---------

    def get_all_datasets(self) -> List[Dataset]:
        rows = self._db.fetch_all(
            """
            SELECT id, dataset_name, category, source,
                   last_updated, record_count, file_size_mb
            FROM datasets_metadata
            ORDER BY id
            """
        )
        datasets: List[Dataset] = []
        for row in rows:
            datasets.append(
                Dataset(
                    dataset_id=row[0],
                    name=row[1],
                    category=row[2],
                    source=row[3],
                    last_updated=row[4],
                    record_count=row[5],
                    file_size_mb=row[6],
                )
            )
        return datasets

    def get_dataset_by_id(self, dataset_id: int) -> Optional[Dataset]:
        row = self._db.fetch_one(
            """
            SELECT id, dataset_name, category, source,
                   last_updated, record_count, file_size_mb
            FROM datasets_metadata
            WHERE id = ?
            """,
            (dataset_id,),
        )
        if row is None:
            return None

        return Dataset(
            dataset_id=row[0],
            name=row[1],
            category=row[2],
            source=row[3],
            last_updated=row[4],
            record_count=row[5],
            file_size_mb=row[6],
        )

    # --------- CREATE ---------

    def create_dataset(
        self,
        name: str,
        category: str,
        source: str,
        last_updated: str,
        record_count: int,
        file_size_mb: float,
    ) -> int:
        cur = self._db.execute_query(
            """
            INSERT INTO datasets_metadata
                (dataset_name, category, source,
                 last_updated, record_count, file_size_mb)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, category, source, last_updated, record_count, file_size_mb),
        )
        return cur.lastrowid

    # --------- UPDATE ---------

    def update_record_count(self, dataset_id: int, new_count: int) -> int:
        cur = self._db.execute_query(
            """
            UPDATE datasets_metadata
            SET record_count = ?
            WHERE id = ?
            """,
            (new_count, dataset_id),
        )
        return cur.rowcount

    # --------- DELETE ---------

    def delete_dataset(self, dataset_id: int) -> int:
        cur = self._db.execute_query(
            "DELETE FROM datasets_metadata WHERE id = ?",
            (dataset_id,),
        )
        return cur.rowcount

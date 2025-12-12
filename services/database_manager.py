# services/database_manager.py

import os
import sqlite3
from typing import Any, Iterable, Optional


class DatabaseManager:
    """
    Simple SQLite database manager used by the OOP refactor.

    It wraps the connection logic and provides helper methods
    for SELECT / INSERT / UPDATE queries.
    """

    def __init__(self, db_path: Optional[str] = None):
        # If no path is given, default to your existing DB:
        # DATA/intelligence_platform.db
        if db_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, "..", "DATA", "intelligence_platform.db")
            db_path = os.path.abspath(db_path)

        self._db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        """Open a SQLite connection if not already open."""
        if self._connection is None:
            self._connection = sqlite3.connect(self._db_path)

    def close(self) -> None:
        """Close the connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def _get_cursor(self) -> sqlite3.Cursor:
        """Internal helper to get a cursor, auto-connecting if needed."""
        if self._connection is None:
            self.connect()
        assert self._connection is not None
        return self._connection.cursor()

    def execute_query(self, sql: str, params: Iterable[Any] = ()) -> sqlite3.Cursor:
        """
        Run an INSERT / UPDATE / DELETE query and commit.
        Returns the cursor so you can inspect lastrowid if needed.
        """
        cur = self._get_cursor()
        cur.execute(sql, tuple(params))
        self._connection.commit()
        return cur

    def fetch_one(self, sql: str, params: Iterable[Any] = ()) -> Optional[tuple]:
        """Run a SELECT that returns a single row (or None)."""
        cur = self._get_cursor()
        cur.execute(sql, tuple(params))
        return cur.fetchone()

    def fetch_all(self, sql: str, params: Iterable[Any] = ()) -> list[tuple]:
        """Run a SELECT that returns all rows."""
        cur = self._get_cursor()
        cur.execute(sql, tuple(params))
        return cur.fetchall()

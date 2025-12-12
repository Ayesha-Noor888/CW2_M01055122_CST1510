# services/auth_manager.py

import os
import sys
from typing import Optional

import bcrypt

# Make sure Python can see the project root so "models" import works
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from models.user import User
from services.database_manager import DatabaseManager


class AuthManager:
    """
    Handles user registration and login, using:
    - DatabaseManager for all SQL
    - User entity for password verification and role
    """

    def __init__(self, db: DatabaseManager):
        self._db = db

    # ---------- INTERNAL HELPER ----------

    def _get_user_row(self, username: str) -> Optional[tuple]:
        """
        Return (id, username, password_hash, role) from DB or None.
        """
        return self._db.fetch_one(
            "SELECT id, username, password_hash, role FROM users WHERE username = ?",
            (username,),
        )

    def get_user(self, username: str) -> Optional[User]:
        """
        Return a User object from the database for this username,
        or None if it doesn't exist.
        """
        row = self._get_user_row(username)
        if row is None:
            return None

        _, uname, pw_hash, role = row
        return User(username=uname, password_hash=pw_hash, role=role)

    # ---------- PUBLIC METHODS ----------

    def register_user(self, username: str, password: str, role: str = "user") -> bool:
        """
        Create a new user if the username is free.
        Returns True on success, False if username already exists.
        """
        # Check if user exists
        if self._get_user_row(username) is not None:
            return False

        # Hash password
        pw_bytes = password.encode("utf-8")
        hashed = bcrypt.hashpw(pw_bytes, bcrypt.gensalt()).decode("utf-8")

        # Insert into DB
        self._db.execute_query(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hashed, role),
        )
        return True

    def check_credentials(self, username: str, password: str) -> tuple[bool, Optional[str]]:
        """
        Check username + password.
        Returns (True, role) if valid, otherwise (False, None).
        """
        user = self.get_user(username)
        if user is None:
            return False, None

        if user.verify_password(password):
            return True, user.get_role()

        return False, None

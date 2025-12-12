# models/user.py

import bcrypt


class User:
    """
    Represents a user in the Multi-Domain Intelligence Platform.
    Only stores username, password hash and role.
    """

    def __init__(self, username: str, password_hash: str, role: str):
        self.__username = username
        self.__password_hash = password_hash
        self.__role = role

    def get_username(self) -> str:
        return self.__username

    def get_role(self) -> str:
        return self.__role

    def verify_password(self, plain_password: str) -> bool:
        """
        Compare a plain-text password with this user's stored hash.
        """
        pw_bytes = plain_password.encode("utf-8")
        hash_bytes = self.__password_hash.encode("utf-8")
        return bcrypt.checkpw(pw_bytes, hash_bytes)

    def __str__(self) -> str:
        return f"User({self.__username}, role={self.__role})"

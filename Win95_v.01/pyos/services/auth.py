"""
Simple local authentication service for the pyOS window.

User accounts are stored in JSON inside the project's data folder. Passwords
are hashed with PBKDF2 so the file does not keep raw passwords.

Example usage:
    from pyos.services.auth import AuthService

    auth = AuthService()
    auth.sign_up("alice", "secret123")
    user = auth.sign_in("alice", "secret123")
    print(user["username"])
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Dict


class AuthError(ValueError):
    """Raised when sign-up or sign-in fails."""


@dataclass
class UserRecord:
    """Stored user information."""

    username: str
    salt: str
    password_hash: str

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "salt": self.salt,
            "password_hash": self.password_hash,
        }


class AuthService:
    """Tiny JSON-backed authentication service."""

    def __init__(self, storage_path: Path | None = None) -> None:
        project_root = Path(__file__).resolve().parents[2]
        self.storage_path = storage_path or project_root / "data" / "users.json"
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._save({"users": {}})

    def _load(self) -> dict:
        with self.storage_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _save(self, payload: dict) -> None:
        with self.storage_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)

    def _hash_password(self, password: str, salt: bytes) -> str:
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            120_000,
        )
        return base64.b64encode(digest).decode("ascii")

    def _validate_username(self, username: str) -> str:
        normalized = username.strip()
        if len(normalized) < 3:
            raise AuthError("Username must be at least 3 characters long.")
        if not normalized.replace("_", "").replace("-", "").isalnum():
            raise AuthError("Username can use letters, numbers, '_' and '-'.")
        return normalized

    def _validate_password(self, password: str) -> None:
        if len(password) < 6:
            raise AuthError("Password must be at least 6 characters long.")

    def list_users(self) -> Dict[str, dict]:
        """Return all stored users."""

        data = self._load()
        return data.get("users", {})

    def sign_up(self, username: str, password: str) -> dict:
        """Create a new local account."""

        username = self._validate_username(username)
        self._validate_password(password)

        data = self._load()
        users = data.setdefault("users", {})
        key = username.lower()
        if key in users:
            raise AuthError("That username already exists.")

        salt = secrets.token_bytes(16)
        record = UserRecord(
            username=username,
            salt=base64.b64encode(salt).decode("ascii"),
            password_hash=self._hash_password(password, salt),
        )
        users[key] = record.to_dict()
        self._save(data)
        return {"username": username}

    def sign_in(self, username: str, password: str) -> dict:
        """Authenticate an existing account."""

        key = username.strip().lower()
        data = self._load()
        users = data.get("users", {})
        if key not in users:
            raise AuthError("No account found for that username.")

        record = users[key]
        salt = base64.b64decode(record["salt"].encode("ascii"))
        candidate = self._hash_password(password, salt)
        if not hmac.compare_digest(candidate, record["password_hash"]):
            raise AuthError("Incorrect password.")
        return {"username": record["username"]}

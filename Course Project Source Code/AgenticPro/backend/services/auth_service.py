import hashlib
import os
import uuid
from backend.database.connection import get_connection
from backend.models.user import User


def hash_password(password: str, salt: str | None = None) -> str:
    """Hash password using SHA256 with salt."""
    if not salt:
        salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    return f"{salt}${hashed}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify plain password against stored salt$hash string."""
    try:
        salt, hash_val = stored_hash.split('$', 1)
        return hashlib.sha256((salt + password).encode('utf-8')).hexdigest() == hash_val
    except Exception:
        return False


def seed_default_users() -> None:
    """Ensure default student and faculty users exist in the database."""
    default_users = [
        # Student accounts
        {
            "id": "student-test-001",
            "username": "student1",
            "password": "student123",
            "role": "student",
            "full_name": "student1",
            "email": "student1@university.edu",
        },
        {
            "id": "student-test-002",
            "username": "student2",
            "password": "student123",
            "role": "student",
            "full_name": "student2",
            "email": "student2@university.edu",
        },
        # Faculty accounts
        {
            "id": "faculty-001",
            "username": "faculty1",
            "password": "faculty123",
            "role": "faculty",
            "full_name": "faculty1",
            "email": "faculty1@university.edu",
        },
        {
            "id": "faculty-admin",
            "username": "admin",
            "password": "admin123",
            "role": "faculty",
            "full_name": "admin",
            "email": "admin@university.edu",
        },
    ]

    with get_connection() as connection:
        for u in default_users:
            existing = connection.execute(
                "SELECT id FROM users WHERE username = ?",
                (u["username"],),
            ).fetchone()
            if not existing:
                p_hash = hash_password(u["password"])
                connection.execute(
                    """
                    INSERT INTO users (id, username, password_hash, role, full_name, email)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (u["id"], u["username"], p_hash, u["role"], u["full_name"], u["email"]),
                )

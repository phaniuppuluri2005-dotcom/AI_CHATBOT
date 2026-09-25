"""
Automated Test Suite for Phani AI Authentication, Hashing, and Role-Based Access Control.
"""

import time
from auth.authentication import hash_password, verify_password, register_user, authenticate_user
from auth.authorization import is_admin, verify_resource_ownership
from database.database import SessionLocal, init_db


def test_password_hashing():
    pwd = "secretpassword123"
    hashed = hash_password(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_user_authentication():
    init_db()
    db = SessionLocal()
    try:
        ts = int(time.time())
        unique_username = f"Test User {ts}"
        unique_email = f"testuser_{ts}@phani.ai"
        user = register_user(db, unique_username, unique_email, "password123", role="user")
        assert user is not None
        assert user.role == "user"

        auth_user = authenticate_user(db, unique_email, "password123")
        assert auth_user is not None
        assert auth_user.username == unique_username
    finally:
        db.close()


def test_rbac_authorization():
    user_dict = {"id": 1, "username": "User", "role": "user"}
    admin_dict = {"id": 2, "username": "Admin", "role": "admin"}

    assert is_admin(user_dict) is False
    assert is_admin(admin_dict) is True

    # Ownership checks
    assert verify_resource_ownership(resource_user_id=1, current_user_id=1) is True
    assert verify_resource_ownership(resource_user_id=1, current_user_id=2) is False

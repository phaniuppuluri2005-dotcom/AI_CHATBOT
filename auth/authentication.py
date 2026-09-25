"""
Authentication & Password Hashing Module for Phani AI Platform.
Handles secure user registration, password verification, session state, and default account initialization.
"""

import hashlib
import os
import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from database.models import User
from database.database import SessionLocal, init_db

logger = logging.getLogger("PhaniAI.Auth")


def hash_password(password: str, salt: Optional[bytes] = None) -> str:
    """Hash password securely using PBKDF2-HMAC-SHA256."""
    if not salt:
        salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"{salt.hex()}:{key.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against stored salt and PBKDF2 hash."""
    try:
        salt_hex, key_hex = hashed.split(":")
        salt = bytes.fromhex(salt_hex)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return key.hex() == key_hex
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def register_user(db: Session, username: str, email: str, password: str, role: str = "user") -> Optional[User]:
    """Register a new user account."""
    existing_email = db.query(User).filter(User.email == email.lower().strip()).first()
    if existing_email:
        return None

    pwd_hash = hash_password(password)
    user = User(
        username=username.strip(),
        email=email.lower().strip(),
        password_hash=pwd_hash,
        role=role.lower()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"User '{username}' ({role}) registered successfully.")
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password."""
    user = db.query(User).filter(User.email == email.lower().strip()).first()
    if user and verify_password(password, user.password_hash):
        return user
    return None


def init_default_accounts():
    """Ensure default demo user and admin accounts exist in the database."""
    init_db()
    db = SessionLocal()
    try:
        # Default standard user
        if not db.query(User).filter(User.email == "user@phani.ai").first():
            register_user(db, username="Phani User", email="user@phani.ai", password="password123", role="user")

        # Default admin user
        if not db.query(User).filter(User.email == "admin@phani.ai").first():
            register_user(db, username="System Admin", email="admin@phani.ai", password="adminpassword123", role="admin")

    finally:
        db.close()


def get_current_user_dict() -> Dict[str, Any]:
    """Retrieve current logged in user details from session state."""
    import streamlit as st
    user = st.session_state.get("current_user")
    if user:
        return user
    # Fallback to default demo user if session not explicitly initialized
    return {
        "id": 1,
        "username": "Phani User",
        "email": "user@phani.ai",
        "role": "user"
    }


# Auto-initialize default accounts on import
init_default_accounts()

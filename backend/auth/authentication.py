"""User authentication, registration, and credential validation."""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from backend.auth.password import hash_password, verify_password
from backend.database.connection import DEFAULT_DB_PATH
from backend.database.repository import (
    create_user,
    get_user_by_id,
    get_user_by_username,
)


def register_user(
    username: str,
    password: str,
    email: Optional[str] = None,
    db_path: Union[str, Path] = DEFAULT_DB_PATH,
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Registers a new user with securely hashed password.

    Args:
        username: Desired username.
        password: Plaintext password (must be >= 4 chars).
        email: Optional email address.
        db_path: Path to database.

    Returns:
        Tuple of (success_bool, message_str, user_dict_or_None).
    """
    cleaned_username = username.strip()
    if not cleaned_username:
        return False, "Username cannot be empty.", None

    if len(cleaned_username) < 3:
        return False, "Username must be at least 3 characters long.", None

    if not password or len(password) < 4:
        return False, "Password must be at least 4 characters long.", None

    # Check for existing user
    existing = get_user_by_username(cleaned_username, db_path=db_path)
    if existing:
        return False, f"Username '{cleaned_username}' is already taken.", None

    pw_hash = hash_password(password)
    user_id = create_user(
        username=cleaned_username,
        email=email.strip() if email else None,
        password_hash=pw_hash,
        db_path=db_path,
    )

    if not user_id:
        return False, "Failed to create user account.", None

    user = get_user_by_id(user_id, db_path=db_path)
    return True, "User registered successfully.", user


def authenticate_user(
    username: str,
    password: str,
    db_path: Union[str, Path] = DEFAULT_DB_PATH,
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Authenticates a user against stored password hash.

    Args:
        username: Provided username.
        password: Provided plaintext password.
        db_path: Path to database.

    Returns:
        Tuple of (authenticated_bool, message_str, user_dict_or_None).
    """
    cleaned_username = username.strip()
    if not cleaned_username or not password:
        return False, "Please enter both username and password.", None

    user = get_user_by_username(cleaned_username, db_path=db_path)
    if not user:
        return False, "Invalid username or password.", None

    stored_hash = user.get("password_hash")
    if not stored_hash:
        # Legacy user without password - allow or reject based on design
        return True, "Logged in as legacy user.", user

    if verify_password(password, stored_hash):
        # Exclude password_hash from session user object
        user_safe = {k: v for k, v in user.items() if k != "password_hash"}
        return True, "Login successful.", user_safe

    return False, "Invalid username or password.", None

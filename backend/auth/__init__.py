"""Authentication module for password hashing and user session management."""

from backend.auth.authentication import (
    authenticate_user,
    get_user_by_id,
    get_user_by_username,
    register_user,
)
from backend.auth.password import hash_password, verify_password

__all__ = [
    "hash_password",
    "verify_password",
    "register_user",
    "authenticate_user",
    "get_user_by_username",
    "get_user_by_id",
]

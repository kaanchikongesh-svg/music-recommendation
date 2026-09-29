"""Secure password hashing and verification using PBKDF2-HMAC-SHA256."""

import hashlib
import hmac
import secrets
from typing import Tuple


def hash_password(password: str, iterations: int = 100_000) -> str:
    """Hashes a password using PBKDF2-HMAC-SHA256 with a random cryptographic salt.

    Args:
        password: Plain text password string.
        iterations: Number of PBKDF2 hash iterations.

    Returns:
        Salted hash string in the format 'iterations$salt$hash'.
    """
    if not password:
        raise ValueError("Password cannot be empty.")

    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    return f"{iterations}${salt}${key.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verifies a plain text password against a stored salted hash.

    Args:
        password: Plain text password string.
        stored_hash: Stored hash in 'iterations$salt$hash' format.

    Returns:
        True if password matches, False otherwise.
    """
    if not password or not stored_hash:
        return False

    try:
        parts = stored_hash.split("$")
        if len(parts) != 3:
            return False

        iterations_str, salt, expected_hex = parts
        iterations = int(iterations_str)

        computed_key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        )
        return hmac.compare_digest(computed_key.hex(), expected_hex)
    except Exception:
        return False

"""JWT generation, decoding, and FastAPI authentication dependencies."""

from datetime import datetime, timedelta, timezone
import os
from typing import Any, Dict, Optional
from fastapi import Cookie, Depends, Header, HTTPException, status
import jwt

from backend.database.repository import get_user_by_id, get_user_by_username

SECRET_KEY = os.getenv("JWT_SECRET", "tunesphere-cinematic-super-secret-jwt-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Encodes a JWT payload with an expiration timestamp."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": now})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


def get_token_from_header_or_cookie(
    authorization: Optional[str] = Header(None),
    access_token: Optional[str] = Cookie(None),
) -> Optional[str]:
    """Extracts raw JWT string from either the Authorization header or HTTP-only cookie."""
    if authorization and authorization.startswith("Bearer "):
        return authorization[len("Bearer ") :].strip()
    if access_token:
        return access_token.strip()
    return None


def get_current_user(
    token: Optional[str] = Depends(get_token_from_header_or_cookie),
) -> Dict[str, Any]:
    """Dependency that requires an authenticated user; raises 401 if missing or invalid."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    user = get_user_by_id(int(user_id)) if user_id else None
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token not found.",
        )

    # Return safe user dictionary without password_hash
    return {k: v for k, v in user.items() if k != "password_hash"}


def get_optional_user(
    token: Optional[str] = Depends(get_token_from_header_or_cookie),
) -> Optional[Dict[str, Any]]:
    """Dependency that optionally extracts the authenticated user without rejecting guest requests."""
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    user_id = payload.get("sub")
    user = get_user_by_id(int(user_id)) if user_id else None
    if not user:
        return None
    return {k: v for k, v in user.items() if k != "password_hash"}

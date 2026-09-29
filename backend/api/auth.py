"""Authentication API router for registration, login, logout, and session check."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field

from backend.auth.authentication import authenticate_user, register_user
from backend.auth.jwt_utils import create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4, max_length=128)
    email: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user: dict
    message: str


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, response: Response):
    """Registers a new user account, creates JWT, and sets auth cookie."""
    success, msg, user = register_user(
        username=req.username,
        password=req.password,
        email=req.email,
    )
    if not success or not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    safe_user = {k: v for k, v in user.items() if k != "password_hash"}
    token = create_access_token({"sub": str(safe_user["id"]), "username": safe_user["username"]})

    # Set secure cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=60 * 60 * 24 * 7,
        samesite="lax",
    )

    return AuthResponse(token=token, user=safe_user, message="Registration successful.")


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, response: Response):
    """Authenticates user credentials, generates JWT token, and sets auth cookie."""
    success, msg, user = authenticate_user(
        username=req.username,
        password=req.password,
    )
    if not success or not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

    safe_user = {k: v for k, v in user.items() if k != "password_hash"}
    token = create_access_token({"sub": str(safe_user["id"]), "username": safe_user["username"]})

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=60 * 60 * 24 * 7,
        samesite="lax",
    )

    return AuthResponse(token=token, user=safe_user, message="Login successful.")


@router.post("/logout")
def logout(response: Response):
    """Logs out the user by clearing the access token cookie."""
    response.delete_cookie(key="access_token")
    return {"status": "ok", "message": "Successfully logged out."}


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """Returns the currently authenticated user profile."""
    return current_user

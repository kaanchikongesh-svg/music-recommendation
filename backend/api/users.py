"""Users API router providing activity metrics and personalized listening profile insights."""

from typing import Optional
from fastapi import APIRouter, Depends

from backend.api.songs import get_cached_df
from backend.auth.jwt_utils import get_optional_user
from backend.services.user_service import get_user_profile_analytics

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/profile")
def get_profile_analytics(current_user: Optional[dict] = Depends(get_optional_user)):
    """Computes listening metrics and musical taste insights for the current user."""
    df = get_cached_df()
    user_id = current_user["id"] if current_user else 1
    analytics = get_user_profile_analytics(user_id=user_id, df=df)
    return {
        "user": current_user or {"id": 1, "username": "Guest", "email": "guest@tunesphere.local"},
        "analytics": analytics,
    }

"""Favorites API router for managing user liked tracks in SQLite / PostgreSQL."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.api.songs import get_cached_df
from backend.auth.jwt_utils import get_current_user
from backend.services.history_service import (
    get_user_favorite_tracks,
    toggle_song_favorite,
)
from backend.database.repository import is_liked

router = APIRouter(prefix="/favorites", tags=["Favorites"])


class FavoriteRequest(BaseModel):
    song_id: str


@router.get("")
def list_favorites(current_user: dict = Depends(get_current_user)):
    """Retrieves all songs favorited by the logged-in user."""
    df = get_cached_df()
    user_id = current_user["id"]
    favs = get_user_favorite_tracks(user_id=user_id, df=df)
    return {"favorites": favs, "total": len(favs)}


@router.get("/check/{song_id}")
def check_is_favorite(song_id: str, current_user: dict = Depends(get_current_user)):
    """Checks whether a specific song is favorited by the current user."""
    user_id = current_user["id"]
    liked = is_liked(user_id, str(song_id))
    return {"song_id": song_id, "is_favorite": liked}


@router.post("", status_code=status.HTTP_201_CREATED)
def add_favorite(req: FavoriteRequest, current_user: dict = Depends(get_current_user)):
    """Adds or toggles a song to the user's favorites collection."""
    user_id = current_user["id"]
    is_now_liked = toggle_song_favorite(user_id, str(req.song_id))
    return {
        "status": "ok",
        "song_id": req.song_id,
        "is_favorite": is_now_liked,
        "message": "Added to favorites" if is_now_liked else "Removed from favorites",
    }


@router.delete("/{song_id}")
def remove_favorite(song_id: str, current_user: dict = Depends(get_current_user)):
    """Explicitly removes a song from the user's favorites collection."""
    user_id = current_user["id"]
    if is_liked(user_id, str(song_id)):
        toggle_song_favorite(user_id, str(song_id))
    return {"status": "ok", "song_id": song_id, "message": "Song removed from favorites."}

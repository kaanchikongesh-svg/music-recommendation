"""Playlists API router for playlist creation, track management, and curation."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.api.songs import get_cached_df
from backend.auth.jwt_utils import get_current_user
from backend.services.playlist_service import (
    add_track_to_playlist,
    create_user_playlist,
    delete_user_playlist,
    get_playlist_track_details,
    list_user_playlists,
    remove_track_from_playlist,
    rename_user_playlist,
)

router = APIRouter(prefix="/playlists", tags=["Playlists"])


class CreatePlaylistRequest(BaseModel):
    playlist_name: str = Field(..., min_length=1, max_length=100)


class RenamePlaylistRequest(BaseModel):
    playlist_name: str = Field(..., min_length=1, max_length=100)


class AddSongRequest(BaseModel):
    song_id: str


@router.get("")
def list_playlists(current_user: dict = Depends(get_current_user)):
    """Retrieves all playlists owned by the authenticated user."""
    user_id = current_user["id"]
    pls = list_user_playlists(user_id=user_id)
    return {"playlists": pls, "total": len(pls)}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_playlist(req: CreatePlaylistRequest, current_user: dict = Depends(get_current_user)):
    """Creates a new playlist for the authenticated user."""
    user_id = current_user["id"]
    pl_id = create_user_playlist(user_id=user_id, playlist_name=req.playlist_name.strip())
    if not pl_id:
        raise HTTPException(status_code=400, detail="Failed to create playlist.")
    return {"id": pl_id, "playlist_name": req.playlist_name.strip(), "message": "Playlist created successfully."}


@router.get("/{playlist_id}")
def get_playlist(playlist_id: int, current_user: dict = Depends(get_current_user)):
    """Retrieves playlist metadata along with its complete song tracklist."""
    df = get_cached_df()
    user_id = current_user["id"]
    all_pls = list_user_playlists(user_id=user_id)
    matched = [p for p in all_pls if p["id"] == playlist_id]
    if not matched:
        raise HTTPException(status_code=404, detail="Playlist not found or access denied.")

    tracks = get_playlist_track_details(playlist_id=playlist_id, df=df)
    return {
        "playlist": matched[0],
        "tracks": tracks,
        "total_tracks": len(tracks),
    }


@router.patch("/{playlist_id}")
def update_playlist_name(
    playlist_id: int,
    req: RenamePlaylistRequest,
    current_user: dict = Depends(get_current_user),
):
    """Renames an existing user playlist."""
    user_id = current_user["id"]
    rename_user_playlist(playlist_id=playlist_id, user_id=user_id, new_name=req.playlist_name.strip())
    return {"status": "ok", "playlist_id": playlist_id, "new_name": req.playlist_name.strip()}


@router.delete("/{playlist_id}")
def delete_playlist(playlist_id: int, current_user: dict = Depends(get_current_user)):
    """Deletes a playlist and all associated track associations."""
    user_id = current_user["id"]
    delete_user_playlist(playlist_id=playlist_id, user_id=user_id)
    return {"status": "ok", "message": "Playlist deleted successfully."}


@router.post("/{playlist_id}/songs", status_code=status.HTTP_201_CREATED)
def add_song(playlist_id: int, req: AddSongRequest, current_user: dict = Depends(get_current_user)):
    """Adds a track to the specified playlist."""
    added = add_track_to_playlist(playlist_id=playlist_id, song_id=str(req.song_id))
    if not added:
        return {"status": "duplicate", "message": "Track is already in this playlist."}
    return {"status": "ok", "playlist_id": playlist_id, "song_id": req.song_id, "message": "Track added to playlist."}


@router.delete("/{playlist_id}/songs/{song_id}")
def remove_song(playlist_id: int, song_id: str, current_user: dict = Depends(get_current_user)):
    """Removes a track from the specified playlist."""
    remove_track_from_playlist(playlist_id=playlist_id, song_id=str(song_id))
    return {"status": "ok", "playlist_id": playlist_id, "song_id": song_id, "message": "Track removed from playlist."}

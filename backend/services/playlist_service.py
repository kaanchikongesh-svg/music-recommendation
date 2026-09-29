"""Playlist service handling playlist CRUD operations and track associations."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd

from backend.data.loader import load_dataset
from backend.database.connection import DEFAULT_DB_PATH
from backend.database.repository import (
    add_song_to_playlist,
    create_playlist,
    delete_playlist,
    get_playlist_songs,
    get_user_playlists,
    remove_song_from_playlist,
    rename_playlist as repo_rename_playlist,
)


def create_user_playlist(
    user_id: int, playlist_name: str, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> Optional[int]:
    """Creates a new playlist for the user."""
    name = playlist_name.strip()
    if not name:
        return None
    return create_playlist(user_id=user_id, playlist_name=name, db_path=db_path)


def rename_user_playlist(
    playlist_id: int, user_id: int, new_name: str, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> bool:
    """Renames an existing user playlist."""
    return repo_rename_playlist(playlist_id=playlist_id, user_id=user_id, new_name=new_name, db_path=db_path)


def delete_user_playlist(
    playlist_id: int, user_id: int, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> bool:
    """Deletes a playlist belonging to the user."""
    return delete_playlist(playlist_id=playlist_id, user_id=user_id, db_path=db_path)


def list_user_playlists(
    user_id: int, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> List[Dict[str, Any]]:
    """Retrieves all playlists for a user with song counts."""
    return get_user_playlists(user_id=user_id, db_path=db_path)


def add_track_to_playlist(
    playlist_id: int, song_id: str, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> bool:
    """Adds a track to a playlist."""
    return add_song_to_playlist(playlist_id=playlist_id, song_id=str(song_id), db_path=db_path)


def remove_track_from_playlist(
    playlist_id: int, song_id: str, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> bool:
    """Removes a track from a playlist."""
    return remove_song_from_playlist(playlist_id=playlist_id, song_id=str(song_id), db_path=db_path)


def get_playlist_track_details(
    playlist_id: int,
    df: Optional[pd.DataFrame] = None,
    db_path: Union[str, Path] = DEFAULT_DB_PATH,
) -> List[Dict[str, Any]]:
    """Retrieves track metadata for all songs contained within a playlist."""
    raw_tracks = get_playlist_songs(playlist_id, db_path=db_path)
    if not raw_tracks:
        return []

    if df is None:
        res = load_dataset()
        df = res.df if res.is_valid else None

    df_lookup = {}
    if df is not None and not df.empty:
        df_lookup = df.set_index("song_id").to_dict(orient="index")

    tracks_with_meta = []
    for item in raw_tracks:
        sid = str(item["song_id"])
        meta = df_lookup.get(sid, {})
        tracks_with_meta.append(
            {
                "song_id": sid,
                "song_name": meta.get("song_name", f"Track {sid}"),
                "artist": meta.get("artist", "Unknown Artist"),
                "album": meta.get("album", "Unknown"),
                "genre": meta.get("genre", "Music"),
                "year": meta.get("year", None),
                "added_at": item["added_at"],
            }
        )

    return tracks_with_meta

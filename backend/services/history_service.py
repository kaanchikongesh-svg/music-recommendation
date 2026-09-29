"""History and favorites service handling interactions, plays, likes, and timeline logs."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd

from backend.data.loader import load_dataset
from backend.database.connection import DEFAULT_DB_PATH
from backend.database.repository import (
    add_favorite,
    clear_user_history as repo_clear_user_history,
    get_user_history,
    get_user_likes,
    is_liked,
    record_history,
    remove_favorite,
    toggle_dislike,
    toggle_like,
)


def log_play_action(
    user_id: int, song_id: str, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> None:
    """Records a PLAY action event into user listening history."""
    record_history(user_id=user_id, song_id=str(song_id), action="PLAY", db_path=db_path)


def clear_listening_history(
    user_id: int, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> bool:
    """Clears all listening history entries for the specified user."""
    return repo_clear_user_history(user_id=user_id, db_path=db_path)


def toggle_song_favorite(
    user_id: int, song_id: str, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> bool:
    """Toggles favorite status for a song."""
    return toggle_like(user_id=user_id, song_id=str(song_id), db_path=db_path)


def toggle_song_dislike(
    user_id: int, song_id: str, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> bool:
    """Toggles dislike status for a song."""
    return toggle_dislike(user_id=user_id, song_id=str(song_id), db_path=db_path)


def check_is_favorite(
    user_id: int, song_id: str, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> bool:
    """Checks whether a track is currently favorited by the user."""
    return is_liked(user_id=user_id, song_id=str(song_id), db_path=db_path)


def get_user_favorite_tracks(
    user_id: int,
    df: Optional[pd.DataFrame] = None,
    db_path: Union[str, Path] = DEFAULT_DB_PATH,
) -> List[Dict[str, Any]]:
    """Retrieves full track details for all songs liked by the user."""
    liked_ids = get_user_likes(user_id, db_path=db_path)
    if not liked_ids:
        return []

    if df is None:
        res = load_dataset()
        df = res.df if res.is_valid else None

    if df is None or df.empty:
        return [{"song_id": sid, "song_name": f"Track {sid}", "artist": "Unknown"} for sid in liked_ids]

    fav_df = df[df["song_id"].astype(str).isin([str(x) for x in liked_ids])]
    return fav_df.to_dict(orient="records")


def get_user_timeline_history(
    user_id: int,
    limit: int = 40,
    df: Optional[pd.DataFrame] = None,
    db_path: Union[str, Path] = DEFAULT_DB_PATH,
) -> List[Dict[str, Any]]:
    """Retrieves enriched chronological listening and interaction history."""
    raw_history = get_user_history(user_id=user_id, limit=limit, db_path=db_path)
    if not raw_history:
        return []

    if df is None:
        res = load_dataset()
        df = res.df if res.is_valid else None

    df_lookup = {}
    if df is not None and not df.empty:
        df_lookup = df.set_index("song_id").to_dict(orient="index")

    enriched = []
    for item in raw_history:
        sid = str(item["song_id"])
        meta = df_lookup.get(sid, {})
        enriched.append(
            {
                "song_id": sid,
                "action": item["action"],
                "played_at": item["played_at"],
                "song_name": meta.get("song_name", f"Track {sid}"),
                "artist": meta.get("artist", "Unknown Artist"),
                "genre": meta.get("genre", "Music"),
                "year": meta.get("year", None),
            }
        )

    return enriched

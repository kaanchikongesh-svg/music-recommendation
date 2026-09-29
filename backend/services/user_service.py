"""User service managing accounts, authentication flows, and dynamic profile analytics."""

from collections import Counter
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
import pandas as pd

from backend.auth.authentication import authenticate_user, register_user
from backend.data.loader import load_dataset
from backend.database.connection import DEFAULT_DB_PATH
from backend.database.repository import (
    get_or_create_default_user as repo_get_or_create_default_user,
    get_user_by_id,
    get_user_history,
    get_user_likes,
    get_user_stats,
)


def register_account(
    username: str,
    password: str,
    email: Optional[str] = None,
    db_path: Union[str, Path] = DEFAULT_DB_PATH,
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Registers a new user account with hashed credentials."""
    return register_user(username=username, password=password, email=email, db_path=db_path)


def login_account(
    username: str,
    password: str,
    db_path: Union[str, Path] = DEFAULT_DB_PATH,
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Authenticates a user account against stored credentials."""
    return authenticate_user(username=username, password=password, db_path=db_path)


def get_default_user(db_path: Union[str, Path] = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Retrieves or provisions the default active session user."""
    return repo_get_or_create_default_user(db_path=db_path)


def get_user_profile_analytics(
    user_id: int,
    df: Optional[pd.DataFrame] = None,
    db_path: Union[str, Path] = DEFAULT_DB_PATH,
) -> Dict[str, Any]:
    """Computes comprehensive user activity statistics including favorite genre and artist.

    Args:
        user_id: User identifier.
        df: Optional dataframe for metadata lookup.
        db_path: Path to SQLite database.

    Returns:
        Dict containing total_plays, total_likes, total_playlists, favorite_genre, favorite_artist.
    """
    stats = get_user_stats(user_id, db_path=db_path)

    # Calculate favorite genre & artist from user history and likes
    liked_ids = get_user_likes(user_id, db_path=db_path)
    history_entries = get_user_history(user_id, limit=100, db_path=db_path)
    played_ids = [entry["song_id"] for entry in history_entries]

    all_interacted_ids = liked_ids + played_ids

    favorite_genre = "None yet"
    favorite_artist = "None yet"

    if all_interacted_ids:
        if df is None:
            res = load_dataset()
            df = res.df if res.is_valid else None

        if df is not None and not df.empty:
            interacted_df = df[df["song_id"].astype(str).isin([str(x) for x in all_interacted_ids])]
            if not interacted_df.empty:
                genres = [
                    g
                    for g in interacted_df["genre"].dropna().tolist()
                    if g and str(g).lower() != "unknown"
                ]
                artists = [
                    a
                    for a in interacted_df["artist"].dropna().tolist()
                    if a and str(a).lower() != "unknown"
                ]

                if genres:
                    favorite_genre = Counter(genres).most_common(1)[0][0]
                if artists:
                    favorite_artist = Counter(artists).most_common(1)[0][0]

    return {
        "total_plays": stats["total_plays"],
        "total_likes": stats["total_likes"],
        "total_playlists": stats["total_playlists"],
        "favorite_genre": favorite_genre,
        "favorite_artist": favorite_artist,
    }

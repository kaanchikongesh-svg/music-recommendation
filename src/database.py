"""Database access and operations module for SQLite backend.

Preserved for backwards-compatibility; delegates to backend.database.
"""

from backend.database.connection import (
    DEFAULT_DB_PATH,
    get_db_connection,
    init_db,
)
from backend.database.models import ListeningHistory, Playlist, Song, User
from backend.database.repository import (
    add_favorite,
    add_song_to_playlist,
    create_playlist,
    create_user,
    delete_playlist,
    get_or_create_default_user,
    get_playlist_songs,
    get_user_by_id,
    get_user_by_username,
    get_user_history,
    get_user_likes,
    get_user_playlists,
    get_user_stats,
    is_liked,
    record_history,
    remove_favorite,
    remove_song_from_playlist,
    toggle_dislike,
    toggle_like,
)

DB_PATH = str(DEFAULT_DB_PATH)

__all__ = [
    "DEFAULT_DB_PATH",
    "DB_PATH",
    "get_db_connection",
    "init_db",
    "User",
    "Song",
    "ListeningHistory",
    "Playlist",
    "create_user",
    "get_user_by_username",
    "get_user_by_id",
    "get_or_create_default_user",
    "record_history",
    "toggle_like",
    "toggle_dislike",
    "add_favorite",
    "remove_favorite",
    "is_liked",
    "get_user_likes",
    "get_user_history",
    "create_playlist",
    "delete_playlist",
    "get_user_playlists",
    "add_song_to_playlist",
    "remove_song_from_playlist",
    "get_playlist_songs",
    "get_user_stats",
]

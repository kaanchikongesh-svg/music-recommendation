"""Services package aggregating business logic for music, users, playlists, and interactions."""

from backend.services.history_service import (
    check_is_favorite,
    get_user_favorite_tracks,
    get_user_timeline_history,
    log_play_action,
    toggle_song_dislike,
    toggle_song_favorite,
)
from backend.services.music_service import (
    get_catalog_statistics,
    get_featured_tracks,
    get_music_catalog,
    get_song_details,
    get_top_genres,
    search_and_filter_tracks,
)
from backend.services.playlist_service import (
    add_track_to_playlist,
    create_user_playlist,
    delete_user_playlist,
    get_playlist_track_details,
    list_user_playlists,
    remove_track_from_playlist,
)
from backend.services.user_service import (
    get_default_user,
    get_user_profile_analytics,
    login_account,
    register_account,
)

__all__ = [
    "get_music_catalog",
    "get_catalog_statistics",
    "search_and_filter_tracks",
    "get_song_details",
    "get_featured_tracks",
    "get_top_genres",
    "register_account",
    "login_account",
    "get_default_user",
    "get_user_profile_analytics",
    "create_user_playlist",
    "delete_user_playlist",
    "list_user_playlists",
    "add_track_to_playlist",
    "remove_track_from_playlist",
    "get_playlist_track_details",
    "log_play_action",
    "toggle_song_favorite",
    "toggle_song_dislike",
    "check_is_favorite",
    "get_user_favorite_tracks",
    "get_user_timeline_history",
]

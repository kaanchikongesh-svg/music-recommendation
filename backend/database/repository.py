"""Data repository for SQLite database queries and transactions."""

from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional, Union

from backend.database.connection import DEFAULT_DB_PATH, get_db_connection, init_db


def create_user(
    username: str,
    email: Optional[str] = None,
    password_hash: Optional[str] = None,
    db_path: Union[str, Path] = DEFAULT_DB_PATH,
) -> Optional[int]:
    """Creates a new user record.

    Returns:
        User ID if successful, None if username or email already exists.
    """
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username.strip(), email.strip() if email else None, password_hash),
        )
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        user_id = None
    finally:
        conn.close()
    return user_id


def get_user_by_username(
    username: str, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> Optional[Dict[str, Any]]:
    """Retrieves a user by username."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, email, password_hash, created_at FROM users WHERE username = ?",
        (username.strip(),),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(
    user_id: int, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> Optional[Dict[str, Any]]:
    """Retrieves a user by user ID."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, email, password_hash, created_at FROM users WHERE id = ?",
        (user_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_or_create_default_user(
    username: str = "Music Lover",
    email: str = "user@musicrecommender.local",
    db_path: Union[str, Path] = DEFAULT_DB_PATH,
) -> Dict[str, Any]:
    """Retrieves or creates a default user for active session interactions."""
    user = get_user_by_username(username, db_path=db_path)
    if user:
        return user

    uid = create_user(username=username, email=email, db_path=db_path)
    return {"id": uid, "username": username, "email": email}


def record_history(
    user_id: int,
    song_id: str,
    action: str = "PLAY",
    db_path: Union[str, Path] = DEFAULT_DB_PATH,
) -> None:
    """Records a user listening interaction in listening_history."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO listening_history (user_id, song_id, action) VALUES (?, ?, ?)",
        (user_id, str(song_id), action),
    )
    conn.commit()
    conn.close()


def toggle_like(
    user_id: int, song_id: str, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> bool:
    """Toggles like status for a song.

    Returns:
        True if the song is now liked, False if unliked.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    song_str = str(song_id)

    cursor.execute(
        "SELECT id FROM likes WHERE user_id = ? AND song_id = ?",
        (user_id, song_str),
    )
    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            "DELETE FROM likes WHERE user_id = ? AND song_id = ?",
            (user_id, song_str),
        )
        conn.commit()
        conn.close()
        return False
    else:
        cursor.execute(
            "DELETE FROM dislikes WHERE user_id = ? AND song_id = ?",
            (user_id, song_str),
        )
        cursor.execute(
            "INSERT INTO likes (user_id, song_id) VALUES (?, ?)",
            (user_id, song_str),
        )
        cursor.execute(
            "INSERT INTO listening_history (user_id, song_id, action) VALUES (?, ?, 'LIKE')",
            (user_id, song_str),
        )
        conn.commit()
        conn.close()
        return True


def add_favorite(
    user_id: int, song_id: str, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> bool:
    """Adds a song to favorites."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    song_str = str(song_id)
    try:
        cursor.execute(
            "INSERT INTO likes (user_id, song_id) VALUES (?, ?)",
            (user_id, song_str),
        )
        cursor.execute(
            "INSERT INTO listening_history (user_id, song_id, action) VALUES (?, ?, 'LIKE')",
            (user_id, song_str),
        )
        conn.commit()
        added = True
    except sqlite3.IntegrityError:
        added = False
    finally:
        conn.close()
    return added


def remove_favorite(
    user_id: int, song_id: str, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> bool:
    """Removes a song from favorites."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM likes WHERE user_id = ? AND song_id = ?",
        (user_id, str(song_id)),
    )
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def is_liked(
    user_id: int, song_id: str, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> bool:
    """Checks if a song is liked by the specified user."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM likes WHERE user_id = ? AND song_id = ?",
        (user_id, str(song_id)),
    )
    row = cursor.fetchone()
    conn.close()
    return row is not None


def get_user_likes(
    user_id: int, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> List[str]:
    """Returns a list of song_ids liked by the user."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT song_id FROM likes WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [row["song_id"] for row in rows]


def toggle_dislike(
    user_id: int, song_id: str, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> bool:
    """Toggles dislike status for a song."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    song_str = str(song_id)

    cursor.execute(
        "SELECT id FROM dislikes WHERE user_id = ? AND song_id = ?",
        (user_id, song_str),
    )
    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            "DELETE FROM dislikes WHERE user_id = ? AND song_id = ?",
            (user_id, song_str),
        )
        conn.commit()
        conn.close()
        return False
    else:
        cursor.execute(
            "DELETE FROM likes WHERE user_id = ? AND song_id = ?",
            (user_id, song_str),
        )
        cursor.execute(
            "INSERT INTO dislikes (user_id, song_id) VALUES (?, ?)",
            (user_id, song_str),
        )
        cursor.execute(
            "INSERT INTO listening_history (user_id, song_id, action) VALUES (?, ?, 'DISLIKE')",
            (user_id, song_str),
        )
        conn.commit()
        conn.close()
        return True


def get_user_history(
    user_id: int, limit: int = 30, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> List[Dict[str, Any]]:
    """Returns recent listening history entries for the user."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT song_id, action, played_at
        FROM listening_history
        WHERE user_id = ?
        ORDER BY played_at DESC, id DESC
        LIMIT ?
        """,
        (user_id, limit),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def create_playlist(
    user_id: int, playlist_name: str, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> int:
    """Creates a new playlist for the user."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO playlists (user_id, playlist_name) VALUES (?, ?)",
        (user_id, playlist_name.strip()),
    )
    conn.commit()
    playlist_id = cursor.lastrowid
    conn.close()
    return playlist_id


def clear_user_history(
    user_id: int, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> bool:
    """Clears all listening history records for a specific user."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM listening_history WHERE user_id = ?",
        (user_id,),
    )
    cleared = cursor.rowcount >= 0
    conn.commit()
    conn.close()
    return cleared


def rename_playlist(
    playlist_id: int, user_id: int, new_name: str, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> bool:
    """Renames an existing playlist belonging to a user."""
    cleaned = new_name.strip()
    if not cleaned:
        return False
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE playlists SET playlist_name = ? WHERE id = ? AND user_id = ?",
        (cleaned, playlist_id, user_id),
    )
    renamed = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return renamed


def delete_playlist(
    playlist_id: int, user_id: int, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> bool:
    """Deletes a playlist belonging to a user."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM playlists WHERE id = ? AND user_id = ?",
        (playlist_id, user_id),
    )
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def get_user_playlists(
    user_id: int, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> List[Dict[str, Any]]:
    """Returns all playlists belonging to the user with song counts."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT p.id, p.playlist_name, p.created_at,
               COUNT(ps.id) AS song_count
        FROM playlists p
        LEFT JOIN playlist_songs ps ON p.id = ps.playlist_id
        WHERE p.user_id = ?
        GROUP BY p.id
        ORDER BY p.created_at DESC
        """,
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_song_to_playlist(
    playlist_id: int, song_id: str, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> bool:
    """Adds a song to a playlist. Returns True if added, False if already exists."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO playlist_songs (playlist_id, song_id) VALUES (?, ?)",
            (playlist_id, str(song_id)),
        )
        conn.commit()
        added = True
    except sqlite3.IntegrityError:
        added = False
    finally:
        conn.close()
    return added


def remove_song_from_playlist(
    playlist_id: int, song_id: str, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> bool:
    """Removes a song from a playlist."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM playlist_songs WHERE playlist_id = ? AND song_id = ?",
        (playlist_id, str(song_id)),
    )
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def get_playlist_songs(
    playlist_id: int, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> List[Dict[str, Any]]:
    """Returns all song_ids and added_at timestamps in a playlist."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT song_id, added_at
        FROM playlist_songs
        WHERE playlist_id = ?
        ORDER BY added_at DESC
        """,
        (playlist_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_user_stats(
    user_id: int, db_path: Union[str, Path] = DEFAULT_DB_PATH
) -> Dict[str, Any]:
    """Calculates user activity statistics from database records."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) AS total_plays FROM listening_history WHERE user_id = ? AND action = 'PLAY'",
        (user_id,),
    )
    total_plays = cursor.fetchone()["total_plays"]

    cursor.execute(
        "SELECT COUNT(*) AS total_likes FROM likes WHERE user_id = ?",
        (user_id,),
    )
    total_likes = cursor.fetchone()["total_likes"]

    cursor.execute(
        "SELECT COUNT(*) AS total_playlists FROM playlists WHERE user_id = ?",
        (user_id,),
    )
    total_playlists = cursor.fetchone()["total_playlists"]

    conn.close()

    return {
        "total_plays": total_plays,
        "total_likes": total_likes,
        "total_playlists": total_playlists,
    }

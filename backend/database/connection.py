"""Database connection management supporting PostgreSQL (via DATABASE_URL) and SQLite fallback."""

import os
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# In Vercel serverless functions, /tmp is the only writable directory if no DATABASE_URL is configured
if os.getenv("VERCEL"):
    DEFAULT_DB_PATH = Path("/tmp") / "music.db"
else:
    DEFAULT_DB_PATH = BASE_DIR / "database" / "music.db"


def get_database_url() -> Optional[str]:
    """Returns DATABASE_URL from environment if configured."""
    url = os.getenv("DATABASE_URL")
    if url and url.strip():
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        return url.strip()
    return None


def is_postgres() -> bool:
    """Checks if the configured database is PostgreSQL."""
    url = get_database_url()
    return bool(url and (url.startswith("postgresql://") or url.startswith("postgres://")))


def get_db_connection(db_path: Union[str, Path] = DEFAULT_DB_PATH):
    """Creates a database connection (PostgreSQL if DATABASE_URL is set, else SQLite)."""
    pg_url = get_database_url()
    if pg_url and is_postgres():
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            conn = psycopg2.connect(pg_url, cursor_factory=RealDictCursor)
            conn.autocommit = False
            return conn
        except Exception:
            try:
                import pg8000.dbapi
                u = urlparse(pg_url)
                conn = pg8000.dbapi.connect(
                    user=u.username or "postgres",
                    password=u.password or "",
                    host=u.hostname or "localhost",
                    port=u.port or 5432,
                    database=u.path.lstrip("/") or "postgres",
                )
                return conn
            except Exception as e:
                print(f"[Database Warning] PostgreSQL connection failed: {e}. Falling back to SQLite.")

    # SQLite fallback
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _format_sql_for_engine(sql: str, is_pg: bool) -> str:
    """Translates parameter placeholders between SQLite (?) and PostgreSQL (%s)."""
    if is_pg:
        return sql.replace("?", "%s")
    return sql


def execute_write(sql: str, params: tuple = (), db_path: Union[str, Path] = DEFAULT_DB_PATH) -> Optional[int]:
    """Executes an INSERT/UPDATE/DELETE statement and returns the inserted/updated ID if available."""
    conn = get_db_connection(db_path)
    is_pg = hasattr(conn, "autocommit") and not isinstance(conn, sqlite3.Connection)
    formatted_sql = _format_sql_for_engine(sql, is_pg)

    last_id = None
    try:
        cursor = conn.cursor()
        if is_pg and "INSERT INTO" in formatted_sql.upper() and "RETURNING" not in formatted_sql.upper():
            formatted_sql += " RETURNING id"
            cursor.execute(formatted_sql, params)
            row = cursor.fetchone()
            if row:
                last_id = row["id"] if isinstance(row, dict) else row[0]
        else:
            cursor.execute(formatted_sql, params)
            if hasattr(cursor, "lastrowid"):
                last_id = cursor.lastrowid
        conn.commit()
    finally:
        conn.close()
    return last_id


def query_all(sql: str, params: tuple = (), db_path: Union[str, Path] = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Executes a SELECT query and returns all records as a list of dictionaries."""
    conn = get_db_connection(db_path)
    is_pg = hasattr(conn, "autocommit") and not isinstance(conn, sqlite3.Connection)
    formatted_sql = _format_sql_for_engine(sql, is_pg)

    try:
        cursor = conn.cursor()
        cursor.execute(formatted_sql, params)
        rows = cursor.fetchall()
        results = []
        for r in rows:
            if isinstance(r, dict):
                results.append(dict(r))
            elif hasattr(r, "keys"):
                results.append({k: r[k] for k in r.keys()})
            else:
                col_names = [desc[0] for desc in cursor.description]
                results.append(dict(zip(col_names, r)))
        return results
    finally:
        conn.close()


def query_one(sql: str, params: tuple = (), db_path: Union[str, Path] = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """Executes a SELECT query and returns the first record as a dictionary or None."""
    results = query_all(sql, params, db_path)
    return results[0] if results else None


def init_db(db_path: Union[str, Path] = DEFAULT_DB_PATH) -> None:
    """Initializes database schema and tables if they do not exist."""
    conn = get_db_connection(db_path)
    is_pg = hasattr(conn, "autocommit") and not isinstance(conn, sqlite3.Connection)
    cursor = conn.cursor()

    try:
        if not is_pg:
            cursor.execute("PRAGMA foreign_keys = ON;")

        # Auto-increment type definition
        pk_type = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"

        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS users (
                id {pk_type},
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE,
                password_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS songs (
                id {pk_type},
                song_id VARCHAR(255) UNIQUE NOT NULL,
                song_name TEXT NOT NULL,
                artist TEXT NOT NULL,
                lyrics TEXT,
                source_link TEXT,
                source_dataset VARCHAR(100) DEFAULT 'spotify_millsongdata',
                album TEXT,
                genre TEXT,
                language TEXT,
                year INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Indexes for high performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_songs_song_id ON songs(song_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_songs_artist ON songs(artist);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_songs_song_name ON songs(song_name);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_songs_language ON songs(language);")

        # Auto-migrate SQLite columns if table was created in an earlier version
        if not is_pg:
            cursor.execute("PRAGMA table_info(songs);")
            existing_cols = {row["name"] for row in cursor.fetchall()}
            if "lyrics" not in existing_cols:
                cursor.execute("ALTER TABLE songs ADD COLUMN lyrics TEXT;")
            if "source_link" not in existing_cols:
                cursor.execute("ALTER TABLE songs ADD COLUMN source_link TEXT;")
            if "source_dataset" not in existing_cols:
                cursor.execute("ALTER TABLE songs ADD COLUMN source_dataset VARCHAR(100) DEFAULT 'spotify_millsongdata';")
            if "updated_at" not in existing_cols:
                cursor.execute("ALTER TABLE songs ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")

        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS listening_history (
                id {pk_type},
                user_id INTEGER NOT NULL,
                song_id VARCHAR(255) NOT NULL,
                action VARCHAR(50) DEFAULT 'PLAY',
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS likes (
                id {pk_type},
                user_id INTEGER NOT NULL,
                song_id VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, song_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS dislikes (
                id {pk_type},
                user_id INTEGER NOT NULL,
                song_id VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, song_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS playlists (
                id {pk_type},
                user_id INTEGER NOT NULL,
                playlist_name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS playlist_songs (
                id {pk_type},
                playlist_id INTEGER NOT NULL,
                song_id VARCHAR(255) NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(playlist_id, song_id),
                FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE
            )
            """
        )

        conn.commit()
    finally:
        conn.close()

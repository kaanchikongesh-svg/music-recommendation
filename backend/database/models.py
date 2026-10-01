"""Data models and type definitions for database entities."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """User entity."""

    id: int
    username: str
    email: Optional[str] = None
    password_hash: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class Song:
    """Song catalog entity."""

    id: Optional[int] = None
    song_id: str = ""
    song_name: str = ""
    artist: str = ""
    lyrics: Optional[str] = None
    source_link: Optional[str] = None
    source_dataset: Optional[str] = "spotify_millsongdata"
    album: Optional[str] = None
    genre: Optional[str] = None
    language: Optional[str] = None
    year: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class ListeningHistory:
    """User interaction record entity."""

    id: Optional[int] = None
    user_id: int = 0
    song_id: str = ""
    action: str = "PLAY"
    played_at: Optional[str] = None


@dataclass
class Playlist:
    """User playlist entity."""

    id: Optional[int] = None
    user_id: int = 0
    playlist_name: str = ""
    created_at: Optional[str] = None
    song_count: int = 0

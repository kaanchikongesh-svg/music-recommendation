"""Music catalog service for querying, searching, filtering, and retrieving track metadata."""

from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

from backend.data.loader import (
    filter_songs,
    get_dataset_statistics,
    load_dataset,
)
from backend.data.validator import ValidationResult


def get_music_catalog() -> ValidationResult:
    """Loads and validates the current music dataset catalog."""
    return load_dataset()


def get_catalog_statistics(df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """Retrieves high-level metadata statistics about the music library."""
    if df is None:
        res = load_dataset()
        df = res.df if res.is_valid else None
    return get_dataset_statistics(df)


def search_and_filter_tracks(
    search_query: str = "",
    artist: str = "All",
    genre: str = "All",
    language: str = "All",
    year_range: Optional[Tuple[int, int]] = None,
    df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Searches and filters tracks according to text criteria and facet filters."""
    if df is None:
        res = load_dataset()
        if not res.is_valid or res.df is None:
            return pd.DataFrame()
        df = res.df

    return filter_songs(
        df=df,
        search_query=search_query,
        artist=artist,
        genre=genre,
        language=language,
        year_range=year_range,
    )


def get_song_details(song_id: str, df: Optional[pd.DataFrame] = None) -> Optional[Dict[str, Any]]:
    """Retrieves full metadata details for a specific song ID."""
    if df is None:
        res = load_dataset()
        if not res.is_valid or res.df is None:
            return None
        df = res.df

    match = df[df["song_id"].astype(str) == str(song_id)]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def get_featured_tracks(limit: int = 6, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Returns top featured tracks from catalog (ordered by popularity if available)."""
    if df is None:
        res = load_dataset()
        if not res.is_valid or res.df is None:
            return pd.DataFrame()
        df = res.df

    if "popularity" in df.columns:
        return df.sort_values(by="popularity", ascending=False).head(limit)
    return df.head(limit)


def get_top_genres(limit: int = 8, df: Optional[pd.DataFrame] = None) -> List[str]:
    """Returns the top represented genres in the catalog."""
    if df is None:
        res = load_dataset()
        if not res.is_valid or res.df is None:
            return []
        df = res.df

    if "genre" not in df.columns:
        return []

    genres = (
        df["genre"]
        .dropna()
        .astype(str)
        .loc[lambda s: (s.str.strip() != "") & (s.str.lower() != "unknown")]
    )
    return genres.value_counts().head(limit).index.tolist()

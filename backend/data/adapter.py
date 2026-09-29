"""Dataset adapter mapping diverse Kaggle / external music schemas to canonical schema.

Canonical Schema:
- song_id (str, unique)
- song_name (str, required)
- artist (str, required)
- album (str, optional, default 'Unknown')
- genre (str, optional, default 'Unknown')
- language (str, optional, default 'Unknown')
- year (int, optional, nullable)

Optional Audio Features:
- danceability (float)
- energy (float)
- tempo (float)
- valence (float)
- acousticness (float)
- instrumentalness (float)
- speechiness (float)
- loudness (float)
- popularity (float/int)
"""

from dataclasses import dataclass, field
import re
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

# Mapping of canonical columns to common Kaggle/external column aliases
COLUMN_ALIASES: Dict[str, List[str]] = {
    "song_id": ["song_id", "track_id", "id", "spotify_id", "track_uri", "uri"],
    "song_name": ["song_name", "track_name", "title", "name", "song", "track"],
    "artist": ["artist", "artists", "artist_name", "artists_name", "performer", "singer"],
    "album": ["album", "album_name", "release", "collection_name", "album_title"],
    "genre": ["genre", "track_genre", "genres", "playlist_genre", "top_genre", "category"],
    "language": ["language", "lang", "track_language", "locale"],
    "year": ["year", "release_year", "release_date", "album_release_year", "date"],
    "danceability": ["danceability", "dance"],
    "energy": ["energy"],
    "tempo": ["tempo", "bpm"],
    "valence": ["valence", "positivity"],
    "acousticness": ["acousticness", "acoustic"],
    "instrumentalness": ["instrumentalness", "instrumental"],
    "speechiness": ["speechiness"],
    "loudness": ["loudness", "loudness_db"],
    "popularity": ["popularity", "track_popularity", "song_popularity", "pop"],
}


@dataclass
class AdaptationReport:
    """Report describing column mappings and transformations applied by the adapter."""

    is_adapted: bool = False
    source_columns: List[str] = field(default_factory=list)
    mapped_columns: Dict[str, str] = field(default_factory=dict)
    missing_required_columns: List[str] = field(default_factory=list)
    missing_optional_columns: List[str] = field(default_factory=list)
    total_records: int = 0
    warnings: List[str] = field(default_factory=list)


def extract_year_from_value(val: Any) -> Optional[int]:
    """Extracts a 4-digit year integer from dates or strings like '2021-05-12' or 2021."""
    if val is None or pd.isna(val):
        return None
    val_str = str(val).strip()
    match = re.search(r"\b(18\d{2}|19\d{2}|20\d{2})\b", val_str)
    if match:
        return int(match.group(1))
    return None


def clean_artist_list_string(val: Any) -> str:
    """Cleans artist strings that may be formatted as Python lists or semicolon-delimited."""
    if val is None or pd.isna(val):
        return ""
    val_str = str(val).strip()
    # If formatted as "['Artist 1', 'Artist 2']"
    if val_str.startswith("[") and val_str.endswith("]"):
        val_str = re.sub(r"[\[\]'\"\\]", "", val_str)
        items = [x.strip() for x in val_str.split(",") if x.strip()]
        return ", ".join(items) if items else ""
    return val_str


def adapt_kaggle_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, AdaptationReport]:
    """Adapts a raw Kaggle or external music DataFrame to the canonical schema.

    Args:
        df: Raw DataFrame from Kaggle or external source.

    Returns:
        Tuple of (adapted_df, adaptation_report).
    """
    if df is None or df.empty:
        return pd.DataFrame(), AdaptationReport(warnings=["Input DataFrame is empty or None."])

    report = AdaptationReport(
        source_columns=list(df.columns),
        total_records=len(df),
    )

    col_map: Dict[str, str] = {}
    normalized_cols = {c.strip().lower(): c for c in df.columns}

    # Match canonical columns with available aliases
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias.lower() in normalized_cols:
                actual_col = normalized_cols[alias.lower()]
                col_map[canonical] = actual_col
                report.mapped_columns[canonical] = actual_col
                break

    # Required canonical columns
    required_canonical = ["song_name", "artist"]
    missing_required = [c for c in required_canonical if c not in col_map]

    if missing_required:
        report.is_adapted = False
        report.missing_required_columns = missing_required
        report.warnings.append(
            f"Cannot adapt dataset: missing required field(s) {missing_required}. "
            f"Source columns available: {list(df.columns)}"
        )
        return pd.DataFrame(), report

    adapted = pd.DataFrame()

    # 1. song_id
    if "song_id" in col_map:
        adapted["song_id"] = df[col_map["song_id"]].astype(str).str.strip()
    else:
        # Fallback: create stable deterministic index-based song_id
        adapted["song_id"] = [f"song_{i+1}" for i in range(len(df))]
        report.warnings.append("No explicit song_id column found; generated sequential IDs.")

    # 2. song_name
    adapted["song_name"] = df[col_map["song_name"]].astype(str).str.strip()

    # 3. artist (clean lists if present)
    adapted["artist"] = df[col_map["artist"]].apply(clean_artist_list_string)

    # 4. album
    if "album" in col_map:
        adapted["album"] = df[col_map["album"]].fillna("Unknown").astype(str).str.strip()
    else:
        adapted["album"] = "Unknown"
        report.missing_optional_columns.append("album")

    # 5. genre
    if "genre" in col_map:
        adapted["genre"] = df[col_map["genre"]].fillna("Unknown").astype(str).str.strip()
    else:
        adapted["genre"] = "Unknown"
        report.missing_optional_columns.append("genre")

    # 6. language (documented fallback: 'Unknown' - never fabricate)
    if "language" in col_map:
        adapted["language"] = df[col_map["language"]].fillna("Unknown").astype(str).str.strip()
    else:
        adapted["language"] = "Unknown"
        report.missing_optional_columns.append("language")

    # 7. year
    if "year" in col_map:
        year_source = df[col_map["year"]]
        adapted["year"] = year_source.apply(extract_year_from_value)
    else:
        adapted["year"] = None
        report.missing_optional_columns.append("year")

    # 8. Optional audio & popularity features
    audio_features = [
        "danceability",
        "energy",
        "tempo",
        "valence",
        "acousticness",
        "instrumentalness",
        "speechiness",
        "loudness",
        "popularity",
    ]
    for feat in audio_features:
        if feat in col_map:
            adapted[feat] = pd.to_numeric(df[col_map[feat]], errors="coerce")
        else:
            report.missing_optional_columns.append(feat)

    report.is_adapted = True
    return adapted, report

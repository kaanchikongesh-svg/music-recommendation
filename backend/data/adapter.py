"""Dataset adapter mapping diverse Kaggle / external music schemas to canonical schema.

Canonical Schema:
- song_id (str, unique, deterministic SHA-256 hash or natural ID)
- song_name (str, required)
- artist (str, required)
- lyrics (str, optional)
- source_link (str, optional)
- source_dataset (str, optional, default 'spotify_millsongdata')
- album (str, optional)
- genre (str, optional)
- language (str, optional)
- year (int, optional, nullable)
"""

from dataclasses import dataclass, field
import hashlib
import re
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

# Mapping of canonical columns to common Kaggle/external column aliases
COLUMN_ALIASES: Dict[str, List[str]] = {
    "song_id": ["song_id", "track_id", "id", "spotify_id", "track_uri", "uri"],
    "song_name": ["song_name", "track_name", "title", "name", "song", "track"],
    "artist": ["artist", "artists", "artist_name", "artists_name", "performer", "singer"],
    "lyrics": ["lyrics", "text", "lyric", "song_lyrics", "words"],
    "source_link": ["source_link", "link", "url", "spotify_url"],
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
    invalid_years_handled: int = 0
    warnings: List[str] = field(default_factory=list)


def generate_deterministic_song_id(artist: str, song_name: str, source_link: Optional[str] = None) -> str:
    """Generates a stable deterministic 16-character hex hash from artist + song_name + link."""
    key = f"{str(artist).strip()}|{str(song_name).strip()}|{str(source_link or '').strip()}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


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
    if val_str.startswith("[") and val_str.endswith("]"):
        val_str = re.sub(r"[\[\]'\"\\]", "", val_str)
        items = [x.strip() for x in val_str.split(",") if x.strip()]
        return ", ".join(items) if items else ""
    return val_str


def detect_text_language(text: Any, fallback: str = "Unknown") -> str:
    """Reliably detects song language from lyrics and title text using Unicode script analysis."""
    if text is None or pd.isna(text):
        return fallback

    sample = str(text)[:1500]

    # Tamil Unicode block: U+0B80 to U+0BFF
    if re.search(r"[\u0B80-\u0BFF]", sample):
        return "Tamil"
    # Hindi / Devanagari Unicode block: U+0900 to U+097F
    if re.search(r"[\u0900-\u097F]", sample):
        return "Hindi"
    # Telugu Unicode block: U+0C00 to U+0C7F
    if re.search(r"[\u0C00-\u0C7F]", sample):
        return "Telugu"
    # Malayalam Unicode block: U+0D00 to U+0D7F
    if re.search(r"[\u0D00-\u0D7F]", sample):
        return "Malayalam"
    # Kannada Unicode block: U+0C80 to U+0CFF
    if re.search(r"[\u0C80-\u0CFF]", sample):
        return "Kannada"
    # Bengali Unicode block: U+0980 to U+09FF
    if re.search(r"[\u0980-\u09FF]", sample):
        return "Bengali"

    if fallback and fallback not in ("Unknown", "None", ""):
        return fallback

    # Check for Latin letters (English)
    latin_count = len(re.findall(r"[a-zA-Z]", sample))
    if latin_count > 15:
        return "English"

    return fallback


def clean_lyrics_text(val: Any) -> Optional[str]:
    """Cleans lyrics text by normalizing CRLF to LF and trimming excess whitespace."""
    if val is None or pd.isna(val):
        return None
    text = str(val).replace("\r\n", "\n").replace("\r", "\n").strip()
    return text if text else None


def adapt_kaggle_dataset(df: pd.DataFrame, dataset_name: str = "spotify_millsongdata") -> Tuple[pd.DataFrame, AdaptationReport]:
    """Adapts a raw DataFrame to the canonical schema.

    Args:
        df: Raw DataFrame from CSV.
        dataset_name: Identifier for the source dataset.

    Returns:
        Tuple of (adapted_df, adaptation_report).
    """
    if df is None or df.empty:
        return pd.DataFrame(), AdaptationReport(warnings=["Input DataFrame is empty or None."])

    # If this is the Tamil movies corpus
    if "movies" in df.columns:
        return adapt_tamil_corpus_dataset(df, dataset_name="tamil_songs_corpus")

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

    # 1. song_name & artist
    adapted["song_name"] = df[col_map["song_name"]].astype(str).str.strip()
    adapted["artist"] = df[col_map["artist"]].apply(clean_artist_list_string)

    # 2. source_link & lyrics
    if "source_link" in col_map:
        adapted["source_link"] = df[col_map["source_link"]].astype(str).str.strip()
    else:
        adapted["source_link"] = None

    if "lyrics" in col_map:
        adapted["lyrics"] = df[col_map["lyrics"]].apply(clean_lyrics_text)
    else:
        adapted["lyrics"] = None

    # 3. song_id (deterministic hash if no natural ID present)
    if "song_id" in col_map and col_map["song_id"] != col_map.get("song_name"):
        adapted["song_id"] = df[col_map["song_id"]].astype(str).str.strip()
    else:
        adapted["song_id"] = [
            generate_deterministic_song_id(a, s, l)
            for a, s, l in zip(adapted["artist"], adapted["song_name"], adapted["source_link"])
        ]

    adapted["source_dataset"] = dataset_name

    # 4. Optional metadata
    if "album" in col_map:
        adapted["album"] = df[col_map["album"]].fillna("Unknown").astype(str).str.strip()
    else:
        adapted["album"] = "Unknown"
        report.missing_optional_columns.append("album")

    if "genre" in col_map:
        adapted["genre"] = df[col_map["genre"]].fillna("Unknown").astype(str).str.strip()
    else:
        adapted["genre"] = "Unknown"
        report.missing_optional_columns.append("genre")

    if "language" in col_map:
        adapted["language"] = df[col_map["language"]].fillna("Unknown").astype(str).str.strip()
    else:
        # Detect language using real lyrics and title text
        adapted["language"] = [
            detect_text_language(f"{lyrics or ''} {song or ''}", fallback="Unknown")
            for lyrics, song in zip(adapted["lyrics"], adapted["song_name"])
        ]
        report.missing_optional_columns.append("language")

    if "year" in col_map:
        raw_year = df[col_map["year"]]
        cleaned_year = raw_year.apply(extract_year_from_value)
        report.invalid_years_handled = int((raw_year.notna() & cleaned_year.isna()).sum())
        adapted["year"] = cleaned_year
    else:
        adapted["year"] = None
        report.missing_optional_columns.append("year")

    # 5. Optional audio features
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


def adapt_tamil_corpus_dataset(df: pd.DataFrame, dataset_name: str = "tamil_songs_corpus") -> Tuple[pd.DataFrame, AdaptationReport]:
    """Adapts a raw Tamil songs corpus dataset (containing movies with movie_song lists) to canonical schema."""
    import ast

    if df is None or df.empty:
        return pd.DataFrame(), AdaptationReport(warnings=["Input DataFrame is empty or None."])

    report = AdaptationReport(
        source_columns=list(df.columns),
        total_records=len(df),
    )

    records: List[Dict[str, Any]] = []

    # If df has 'movies' column with nested movie_song structures
    if "movies" in df.columns:
        for _, row in df.iterrows():
            try:
                val = row["movies"]
                data = ast.literal_eval(val) if isinstance(val, str) else val
                if not isinstance(data, dict):
                    continue

                movie_eng = (data.get("movie_name_eng") or "").strip()
                movie_tam = (data.get("movie_name_tamil") or "").strip()
                year_val = data.get("year")
                year = extract_year_from_value(year_val)
                movie_music = (data.get("music") or "").strip()
                album = movie_eng or movie_tam or None
                movie_url = (data.get("movie_url") or "").strip()

                for s in data.get("movie_song") or []:
                    raw_title = s.get("song_title", "")
                    raw_title = re.sub(r"[\r\n\t]+", " ", str(raw_title)).strip()
                    if not raw_title:
                        continue
                    raw_title = re.sub(r"\s+", " ", raw_title).strip()

                    singers = (s.get("song_singers") or "").strip()
                    music = (s.get("song_music") or "").strip() or movie_music
                    lyricist = (s.get("song_lyrics") or "").strip()

                    # Artist determination: prioritize singers if available, else music composer
                    if singers and music:
                        artist = f"{music} ft. {singers}" if music not in singers else singers
                    elif music:
                        artist = music
                    elif singers:
                        artist = singers
                    elif lyricist:
                        artist = lyricist
                    else:
                        artist = movie_eng or "Tamil Artist"

                    lyrics = clean_lyrics_text(s.get("song_fulllyrics"))
                    source_link = (s.get("song_url") or movie_url or "").strip() or None
                    song_id = generate_deterministic_song_id(artist, raw_title, source_link)

                    records.append({
                        "song_id": song_id,
                        "song_name": raw_title,
                        "artist": artist,
                        "lyrics": lyrics,
                        "source_link": source_link,
                        "source_dataset": dataset_name,
                        "album": album or "Tamil Cinema",
                        "genre": "Tamil Film Music",
                        "language": "Tamil",
                        "year": year,
                    })
            except Exception as e:
                report.warnings.append(f"Skipping malformed row: {e}")
                continue
    else:
        # Standard tabular Tamil CSV
        return adapt_kaggle_dataset(df, dataset_name=dataset_name)

    adapted_df = pd.DataFrame(records)
    if not adapted_df.empty:
        adapted_df = adapted_df.drop_duplicates(subset=["song_id"]).reset_index(drop=True)
        report.is_adapted = True
        report.total_records = len(adapted_df)
    else:
        report.warnings.append("No valid Tamil song records could be extracted.")

    return adapted_df, report


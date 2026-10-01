"""Songs catalog API router providing catalog browsing, search, details, and statistics."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
import numpy as np
import pandas as pd

from backend.data.loader import get_dataset_statistics, load_dataset
from backend.services.music_service import (
    get_featured_tracks,
    get_top_genres,
    search_and_filter_tracks,
)

router = APIRouter(tags=["Songs"])

# Load dataset once into memory
_DATASET_CACHE = None


def get_cached_df() -> pd.DataFrame:
    """Retrieves or loads the cached music dataset DataFrame."""
    global _DATASET_CACHE
    if _DATASET_CACHE is None or _DATASET_CACHE.empty:
        from pathlib import Path
        base_dir = Path(__file__).resolve().parent.parent.parent
        processed_path = base_dir / "data" / "processed" / "songs_processed.csv"
        
        if processed_path.exists():
            try:
                _DATASET_CACHE = pd.read_csv(processed_path)
                return _DATASET_CACHE
            except Exception:
                pass

        val = load_dataset()
        if val.is_valid and val.df is not None and not val.df.empty:
            _DATASET_CACHE = val.df
        else:
            # Fallback to database
            try:
                from backend.database.connection import get_db_connection
                conn = get_db_connection()
                _DATASET_CACHE = pd.read_sql_query("SELECT * FROM songs", conn)
                conn.close()
            except Exception:
                _DATASET_CACHE = pd.DataFrame()
    return _DATASET_CACHE


def sanitize_records(df_subset: pd.DataFrame) -> List[dict]:
    """Converts a DataFrame subset into JSON-compliant dictionary records, replacing NaN/inf with None."""
    if df_subset is None or df_subset.empty:
        return []
    records = []
    for row in df_subset.to_dict(orient="records"):
        clean_row = {}
        for k, v in row.items():
            if pd.isna(v) or v is None:
                clean_row[k] = None
            elif isinstance(v, (float, np.floating)) and (np.isnan(v) or np.isinf(v)):
                clean_row[k] = None
            elif isinstance(v, (int, np.integer)):
                clean_row[k] = int(v)
            elif isinstance(v, (float, np.floating)):
                clean_row[k] = float(v)
            else:
                clean_row[k] = v
        records.append(clean_row)
    return records


def sanitize_song_dict(row_dict: dict) -> dict:
    """Converts a single song dictionary into JSON-compliant format."""
    clean_row = {}
    for k, v in row_dict.items():
        if pd.isna(v) or v is None:
            clean_row[k] = None
        elif isinstance(v, (float, np.floating)) and (np.isnan(v) or np.isinf(v)):
            clean_row[k] = None
        elif isinstance(v, (int, np.integer)):
            clean_row[k] = int(v)
        elif isinstance(v, (float, np.floating)):
            clean_row[k] = float(v)
        else:
            clean_row[k] = v
    return clean_row


@router.get("/songs")
def list_songs(
    query: Optional[str] = Query(default=None, description="Search keyword in title, artist, or album"),
    genre: Optional[str] = Query(default=None, description="Genre filter"),
    language: Optional[str] = Query(default=None, description="Language filter"),
    artist: Optional[str] = Query(default=None, description="Artist filter"),
    year_min: Optional[int] = Query(default=None, description="Minimum release year"),
    year_max: Optional[int] = Query(default=None, description="Maximum release year"),
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(default=24, ge=1, le=100, description="Items per page"),
):
    """Filters, searches, and paginates songs from the catalog."""
    df = get_cached_df()
    if df.empty:
        return {"songs": [], "total": 0, "page": 1, "limit": 24, "total_pages": 0}

    # Safe parameter extraction (guards against direct function calls with Query default objects)
    q_val = query if isinstance(query, str) else ""
    artist_val = artist if isinstance(artist, str) else "All"
    genre_val = genre if isinstance(genre, str) else "All"
    lang_val = language if isinstance(language, str) else "All"

    y_min = year_min if isinstance(year_min, int) else None
    y_max = year_max if isinstance(year_max, int) else None
    year_range = (y_min, y_max) if y_min is not None and y_max is not None else None

    p_num = page if isinstance(page, int) and page >= 1 else 1
    p_lim = limit if isinstance(limit, int) and limit >= 1 else 24

    filtered = search_and_filter_tracks(
        search_query=q_val,
        artist=artist_val,
        genre=genre_val,
        language=lang_val,
        year_range=year_range,
        df=df,
    )

    total = len(filtered)
    total_pages = max(1, (total + p_lim - 1) // p_lim)
    start_idx = (p_num - 1) * p_lim
    end_idx = start_idx + p_lim

    subset = filtered.iloc[start_idx:end_idx]
    records = sanitize_records(subset)

    return {
        "songs": records,
        "total": total,
        "page": p_num,
        "limit": p_lim,
        "total_pages": total_pages,
    }


@router.get("/search")
def search_songs(
    q: str = Query("", description="Query string"),
    limit: int = Query(20, ge=1, le=100),
):
    """Fast auto-complete / search endpoint across track name, artist, and album."""
    df = get_cached_df()
    if df.empty or not q.strip():
        return {"results": []}

    filtered = search_and_filter_tracks(search_query=q.strip(), df=df)
    subset = filtered.head(limit)
    records = sanitize_records(subset)
    return {"results": records, "total": len(filtered)}


@router.get("/songs/{song_id}")
def get_song_details(song_id: str):
    """Retrieves full details and acoustic audio profile for a specific track."""
    df = get_cached_df()
    if df.empty:
        raise HTTPException(status_code=404, detail="Catalog is currently empty.")

    matched = df[df["song_id"].astype(str) == str(song_id)]
    if matched.empty:
        raise HTTPException(status_code=404, detail=f"Song with ID '{song_id}' not found.")

    song_dict = sanitize_song_dict(matched.iloc[0].to_dict())

    # Extract detected audio features for radar visualization
    audio_feature_keys = [
        "danceability",
        "energy",
        "valence",
        "tempo",
        "acousticness",
        "instrumentalness",
        "speechiness",
        "loudness",
        "popularity",
    ]
    features = {k: song_dict.get(k) for k in audio_feature_keys if k in song_dict and song_dict.get(k) is not None}

    return {
        "song": song_dict,
        "audio_features": features,
    }


@router.get("/genres")
def list_genres(limit: int = Query(20, ge=1, le=50)):
    """Returns top genres/moods present in the actual music catalog."""
    df = get_cached_df()
    if df.empty:
        return {"genres": []}
    genres = get_top_genres(limit=limit, df=df)
    return {"genres": genres}


@router.get("/featured")
def list_featured(limit: int = Query(6, ge=1, le=50)):
    """Returns trending/featured tracks based on available popularity or catalog order."""
    df = get_cached_df()
    if df.empty:
        return {"featured": []}
    featured_df = get_featured_tracks(limit=limit, df=df)
    records = sanitize_records(featured_df)
    return {"featured": records}


@router.get("/languages")
def list_languages():
    """Returns the distinct list of real languages present in the music catalog."""
    df = get_cached_df()
    if df.empty or "language" not in df.columns:
        return {"languages": []}

    langs = df["language"].dropna().astype(str).str.strip()
    valid_langs = sorted([l for l in langs.unique() if l and l.lower() not in ("unknown", "none", "nan")])
    return {"languages": valid_langs}


@router.get("/tamil")
@router.get("/tamil-music")
def list_tamil_songs(
    query: Optional[str] = Query(default=None, description="Search keyword in Tamil or English"),
    artist: Optional[str] = Query(default=None, description="Filter by Tamil artist"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=24, ge=1, le=100),
):
    """Returns real Tamil songs from the catalog supporting Unicode and transliterated search."""
    import re
    df = get_cached_df()
    if df.empty:
        return {"songs": [], "total": 0, "page": page, "limit": limit, "total_pages": 0}

    # Extract Tamil songs based on language column or Tamil Unicode script
    if "language" in df.columns:
        mask = df["language"].astype(str).str.strip().str.lower() == "tamil"
    else:
        def has_tamil(val: Any) -> bool:
            return bool(re.search(r"[\u0B80-\u0BFF]", str(val))) if val is not None else False
        mask = df["song_name"].apply(has_tamil) | df["lyrics"].apply(has_tamil)

    tamil_df = df[mask]

    # Search filter if provided
    q_str = str(query or "").strip().lower()
    if query and not isinstance(query, str) and hasattr(query, "default"):
        q_str = ""

    if q_str and not tamil_df.empty:
        q_mask = pd.Series(False, index=tamil_df.index)
        for col in ["song_name", "artist", "album", "lyrics"]:
            if col in tamil_df.columns:
                q_mask = q_mask | tamil_df[col].astype(str).str.lower().str.contains(q_str, regex=False, na=False)
        tamil_df = tamil_df[q_mask]

    # Artist filter if provided
    art_str = str(artist or "").strip()
    if artist and not isinstance(artist, str) and hasattr(artist, "default"):
        art_str = ""
    if art_str and art_str.lower() != "all" and not tamil_df.empty:
        tamil_df = tamil_df[tamil_df["artist"].astype(str).str.lower().str.contains(art_str.lower(), regex=False, na=False)]

    total = len(tamil_df)
    total_pages = max(1, (total + limit - 1) // limit) if total > 0 else 0
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit

    subset = tamil_df.iloc[start_idx:end_idx]
    records = sanitize_records(subset)
    return {
        "songs": records,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
    }



@router.get("/stats")
def catalog_stats():
    """Returns summary metadata statistics for the entire music catalog."""
    df = get_cached_df()
    stats = get_dataset_statistics(df)
    return stats


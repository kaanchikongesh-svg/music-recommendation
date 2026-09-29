"""Songs catalog API router providing catalog browsing, search, details, and statistics."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
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
        val = load_dataset()
        if val.is_valid and val.df is not None:
            _DATASET_CACHE = val.df
        else:
            _DATASET_CACHE = pd.DataFrame()
    return _DATASET_CACHE


@router.get("/songs")
def list_songs(
    query: Optional[str] = Query(None, description="Search keyword in title, artist, or album"),
    genre: Optional[str] = Query(None, description="Genre filter"),
    language: Optional[str] = Query(None, description="Language filter"),
    artist: Optional[str] = Query(None, description="Artist filter"),
    year_min: Optional[int] = Query(None, description="Minimum release year"),
    year_max: Optional[int] = Query(None, description="Maximum release year"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(24, ge=1, le=100, description="Items per page"),
):
    """Filters, searches, and paginates songs from the catalog."""
    df = get_cached_df()
    if df.empty:
        return {"songs": [], "total": 0, "page": page, "limit": limit, "total_pages": 0}

    year_range = (year_min, year_max) if year_min is not None and year_max is not None else None

    filtered = search_and_filter_tracks(
        search_query=query or "",
        artist=artist or "All",
        genre=genre or "All",
        language=language or "All",
        year_range=year_range,
        df=df,
    )

    total = len(filtered)
    total_pages = max(1, (total + limit - 1) // limit)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit

    subset = filtered.iloc[start_idx:end_idx]
    # Replace NaN with None for clean JSON serialization
    records = subset.where(pd.notnull(subset), None).to_dict(orient="records")

    return {
        "songs": records,
        "total": total,
        "page": page,
        "limit": limit,
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
    records = subset.where(pd.notnull(subset), None).to_dict(orient="records")
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

    song_dict = matched.iloc[0].where(pd.notnull(matched.iloc[0]), None).to_dict()

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
    records = featured_df.where(pd.notnull(featured_df), None).to_dict(orient="records")
    return {"featured": records}


@router.get("/stats")
def catalog_stats():
    """Returns summary metadata statistics for the entire music catalog."""
    df = get_cached_df()
    stats = get_dataset_statistics(df)
    return stats

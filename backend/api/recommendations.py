"""Recommendations API router delivering content-based and personalized music discovery."""

from typing import Optional
from fastapi import APIRouter, Depends, Query

from backend.api.songs import get_cached_df
from backend.auth.jwt_utils import get_optional_user
from backend.recommendation.engine import (
    get_personalized_recommendations,
    recommend_songs,
)

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("")
def get_recommendations(
    song_id: Optional[str] = Query(None, description="Seed song ID for content-based matching"),
    limit: int = Query(6, ge=1, le=50, description="Number of recommendations"),
    language_mode: str = Query("same", description="'same' for same language, 'any' for cross-language"),
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Generates recommendations either for a seed track or tailored to the logged-in user."""
    df = get_cached_df()
    if df.empty:
        return {"recommendations": []}

    if song_id:
        recs = recommend_songs(song_id=str(song_id), df=df, n_recommendations=limit, language_mode=language_mode)
        return {
            "type": "content_based",
            "seed_song_id": song_id,
            "language_mode": language_mode,
            "recommendations": recs,
        }

    # Personalized recommendations for user or cold start
    user_id = current_user["id"] if current_user else 1
    recs = get_personalized_recommendations(user_id=user_id, df=df, n_recommendations=limit)
    return {
        "type": "personalized",
        "user_id": user_id,
        "recommendations": recs,
    }


@router.get("/seed/{song_id}")
def get_seed_recommendations(
    song_id: str,
    limit: int = Query(6, ge=1, le=50),
    language_mode: str = Query("same", description="'same' or 'any'"),
):
    """Generates acoustic and lexical similar tracks for a specific song ID."""
    df = get_cached_df()
    if df.empty:
        return {"recommendations": []}
    recs = recommend_songs(song_id=str(song_id), df=df, n_recommendations=limit, language_mode=language_mode)
    return {"seed_song_id": song_id, "language_mode": language_mode, "recommendations": recs}


@router.get("/personalized")
def get_user_personalized(
    limit: int = Query(6, ge=1, le=50),
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Generates taste-centroid vector recommendations for the active user session."""
    df = get_cached_df()
    if df.empty:
        return {"recommendations": []}
    user_id = current_user["id"] if current_user else 1
    recs = get_personalized_recommendations(user_id=user_id, df=df, n_recommendations=limit)
    return {"user_id": user_id, "recommendations": recs}

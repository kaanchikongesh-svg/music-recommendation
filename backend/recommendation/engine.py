"""Unified recommendation engine facade for content-based and personalized recommendations."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import pandas as pd

from backend.data.loader import load_dataset
from backend.data.preprocessing import preprocess_dataset
from backend.database.repository import get_user_history, get_user_likes
from backend.recommendation.content_based import ContentBasedRecommender
from backend.recommendation.ranking import rank_and_enrich_recommendations

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_MODEL_DIR = BASE_DIR / "models"
DEFAULT_MODEL_PATH = DEFAULT_MODEL_DIR / "content_recommender.pkl"

# In-memory singleton cache
_RECOMMENDER_INSTANCE: Optional[ContentBasedRecommender] = None
_CACHED_DATAFRAME: Optional[pd.DataFrame] = None


def is_model_trained(model_path: Union[str, Path] = DEFAULT_MODEL_PATH) -> bool:
    """Checks whether the serialized recommendation model exists on disk or in memory."""
    global _RECOMMENDER_INSTANCE
    if _RECOMMENDER_INSTANCE is not None:
        return True
    return Path(model_path).exists()


def get_or_train_recommender(
    df: Optional[pd.DataFrame] = None,
    model_path: Union[str, Path] = DEFAULT_MODEL_PATH,
    force_retrain: bool = False,
) -> Tuple[Optional[ContentBasedRecommender], Optional[pd.DataFrame]]:
    """Loads an existing model from disk or trains a new one from the provided or loaded dataset.

    Args:
        df: Optional processed or raw DataFrame.
        model_path: Path to serialized model file in models/ directory.
        force_retrain: If True, forces model retraining and serialization.

    Returns:
        Tuple of (ContentBasedRecommender_instance, active_dataframe).
    """
    global _RECOMMENDER_INSTANCE, _CACHED_DATAFRAME

    # If already cached in memory and not forcing retrain
    if not force_retrain and _RECOMMENDER_INSTANCE is not None and _CACHED_DATAFRAME is not None:
        return _RECOMMENDER_INSTANCE, _CACHED_DATAFRAME

    # Check if model exists on disk
    path = Path(model_path)
    if not force_retrain and path.exists():
        loaded_model = ContentBasedRecommender.load(path)
        if loaded_model is not None:
            _RECOMMENDER_INSTANCE = loaded_model
            # Prepare dataframe
            if df is not None and not df.empty:
                _CACHED_DATAFRAME = df
            else:
                raw_res = load_dataset()
                if raw_res.is_valid and raw_res.df is not None:
                    if "combined_features" in raw_res.df.columns:
                        _CACHED_DATAFRAME = raw_res.df
                    else:
                        prep_res = preprocess_dataset(raw_res.df, save_processed=True)
                        if prep_res.is_success and prep_res.df is not None:
                            _CACHED_DATAFRAME = prep_res.df
            return _RECOMMENDER_INSTANCE, _CACHED_DATAFRAME

    # Train from scratch
    active_df = df
    if active_df is None or active_df.empty:
        raw_res = load_dataset()
        if not raw_res.is_valid or raw_res.df is None:
            return None, None
        prep_res = preprocess_dataset(raw_res.df, save_processed=True)
        if not prep_res.is_success or prep_res.df is None:
            return None, None
        active_df = prep_res.df

    if "combined_features" not in active_df.columns:
        prep_res = preprocess_dataset(active_df, save_processed=True)
        if not prep_res.is_success or prep_res.df is None:
            return None, None
        active_df = prep_res.df

    recommender = ContentBasedRecommender()
    recommender.fit(active_df)
    recommender.save(path)

    _RECOMMENDER_INSTANCE = recommender
    _CACHED_DATAFRAME = active_df

    return _RECOMMENDER_INSTANCE, _CACHED_DATAFRAME


def recommend_songs(
    song_id: str,
    df: Optional[pd.DataFrame] = None,
    n_recommendations: int = 10,
    language_mode: str = "same",
    model_path: Union[str, Path] = DEFAULT_MODEL_PATH,
) -> List[Dict[str, Any]]:
    """Generates content-based song recommendations for a specific song ID."""
    recommender, active_df = get_or_train_recommender(df=df, model_path=model_path)
    if recommender is None or active_df is None or active_df.empty:
        return []

    candidates = recommender.get_similar_indices(
        query_song_id=str(song_id), top_k=n_recommendations * 6
    )

    # Detect seed song language
    seed_lang = None
    if "language" in active_df.columns:
        match = active_df[active_df["song_id"].astype(str) == str(song_id)]
        if not match.empty:
            seed_lang = match.iloc[0].get("language")

    return rank_and_enrich_recommendations(
        candidates=candidates,
        df=active_df,
        query_song_id=str(song_id),
        preferred_language=seed_lang,
        language_mode=language_mode,
        n_recommendations=n_recommendations,
    )


def get_personalized_recommendations(
    user_id: int,
    df: Optional[pd.DataFrame] = None,
    n_recommendations: int = 10,
    model_path: Union[str, Path] = DEFAULT_MODEL_PATH,
) -> List[Dict[str, Any]]:
    """Generates personalized recommendations based on a user's listening history and likes.

    Args:
        user_id: User identifier.
        df: Optional dataframe of the catalog.
        n_recommendations: Number of recommendations to return.
        model_path: Path to serialized model.

    Returns:
        List of personalized song recommendation dictionaries.
    """
    recommender, active_df = get_or_train_recommender(df=df, model_path=model_path)
    if recommender is None or active_df is None or active_df.empty:
        return []

    # Retrieve user liked and played songs
    liked_ids = get_user_likes(user_id)
    history_entries = get_user_history(user_id, limit=50)
    played_ids = [entry["song_id"] for entry in history_entries if entry.get("action") == "PLAY"]

    # Combine seeds with higher weight for liked songs
    seed_ids = list(dict.fromkeys(liked_ids + played_ids))
    valid_seeds = [sid for sid in seed_ids if str(sid) in recommender.song_id_to_idx]

    if not valid_seeds:
        # Cold start fallback: top popular songs or top catalog tracks
        if "popularity" in active_df.columns:
            top_df = active_df.sort_values(by="popularity", ascending=False).head(n_recommendations)
        else:
            top_df = active_df.head(n_recommendations)
        candidates = [(int(i), 0.95 - (idx * 0.02)) for idx, i in enumerate(top_df.index)]
        return rank_and_enrich_recommendations(
            candidates=candidates,
            df=active_df,
            n_recommendations=n_recommendations,
        )

    candidates = recommender.get_profile_recommendations(
        seed_song_ids=valid_seeds, top_k=n_recommendations * 5
    )

    # Exclude tracks already liked/played
    exclude_set = set(valid_seeds)

    return rank_and_enrich_recommendations(
        candidates=candidates,
        df=active_df,
        exclude_song_ids=exclude_set,
        n_recommendations=n_recommendations,
    )

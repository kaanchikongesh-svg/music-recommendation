"""Recommendation engine interface and core algorithms module.

Preserved for backwards-compatibility; delegates to backend.recommendation.
"""

from backend.recommendation.engine import (
    DEFAULT_MODEL_PATH,
    get_or_train_recommender,
    get_personalized_recommendations,
    is_model_trained,
    recommend_songs,
)

__all__ = [
    "DEFAULT_MODEL_PATH",
    "get_or_train_recommender",
    "is_model_trained",
    "recommend_songs",
    "get_personalized_recommendations",
]

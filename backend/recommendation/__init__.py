"""Recommendation package providing content-based and personalized recommendation algorithms."""

from backend.recommendation.content_based import ContentBasedRecommender
from backend.recommendation.engine import (
    DEFAULT_MODEL_PATH,
    get_or_train_recommender,
    get_personalized_recommendations,
    is_model_trained,
    recommend_songs,
)
from backend.recommendation.ranking import rank_and_enrich_recommendations

__all__ = [
    "DEFAULT_MODEL_PATH",
    "ContentBasedRecommender",
    "rank_and_enrich_recommendations",
    "get_or_train_recommender",
    "is_model_trained",
    "recommend_songs",
    "get_personalized_recommendations",
]

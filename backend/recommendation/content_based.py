"""Content-based filtering using TF-IDF text features and optional audio feature similarity."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

BOUNDED_AUDIO_FEATURES = [
    "danceability",
    "energy",
    "valence",
    "acousticness",
    "instrumentalness",
    "speechiness",
]


class ContentBasedRecommender:
    """Content-based recommendation model using TF-IDF vectorization and audio features."""

    def __init__(self):
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.audio_scaler: Optional[MinMaxScaler] = None
        self.audio_matrix: Optional[np.ndarray] = None
        self.song_ids: List[str] = []
        self.song_id_to_idx: Dict[str, int] = {}
        self.audio_features_used: List[str] = []

    def fit(self, df: pd.DataFrame) -> "ContentBasedRecommender":
        """Fits the TF-IDF vectorizer and audio feature matrix from a processed DataFrame."""
        if df is None or df.empty or "combined_features" not in df.columns:
            raise ValueError("Processed dataframe must contain 'combined_features' column.")

        self.song_ids = df["song_id"].astype(str).tolist()
        self.song_id_to_idx = {sid: idx for idx, sid in enumerate(self.song_ids)}

        # 1. Fit TF-IDF on combined_features
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=10_000,
            ngram_range=(1, 2),
            sublinear_tf=True,
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(df["combined_features"].fillna(""))

        # 2. Check and normalize optional audio features
        detected_audio = [
            col
            for col in [
                "danceability",
                "energy",
                "valence",
                "acousticness",
                "instrumentalness",
                "speechiness",
                "tempo",
                "loudness",
            ]
            if col in df.columns
        ]

        if detected_audio:
            self.audio_features_used = detected_audio
            audio_data = df[detected_audio].fillna(0).to_numpy()
            self.audio_scaler = MinMaxScaler()
            self.audio_matrix = self.audio_scaler.fit_transform(audio_data)
        else:
            self.audio_features_used = []
            self.audio_scaler = None
            self.audio_matrix = None

        return self

    def get_similar_indices(
        self, query_song_id: str, top_k: int = 50
    ) -> List[Tuple[int, float]]:
        """Computes similarity scores for a given query song ID.

        Args:
            query_song_id: Unique song ID in catalog.
            top_k: Number of raw candidate indices to retrieve.

        Returns:
            List of (song_index, similarity_score) tuples.
        """
        query_id_str = str(query_song_id)
        if query_id_str not in self.song_id_to_idx or self.tfidf_matrix is None:
            return []

        idx = self.song_id_to_idx[query_id_str]
        query_vec = self.tfidf_matrix[idx]

        # Cosine similarity over TF-IDF text features
        text_sim = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # Blend audio features similarity if available
        if self.audio_matrix is not None:
            query_audio = self.audio_matrix[idx : idx + 1]
            audio_sim = cosine_similarity(query_audio, self.audio_matrix).flatten()
            total_sim = 0.75 * text_sim + 0.25 * audio_sim
        else:
            total_sim = text_sim

        # Get sorted candidate indices (excluding self)
        ranked_indices = np.argsort(-total_sim)
        candidates = []
        for i in ranked_indices:
            if i == idx:
                continue
            candidates.append((int(i), float(total_sim[i])))
            if len(candidates) >= top_k:
                break

        return candidates

    def get_profile_recommendations(
        self,
        seed_song_ids: List[str],
        top_k: int = 50,
    ) -> List[Tuple[int, float]]:
        """Generates recommendations based on a user profile centroid of seed song IDs."""
        if not seed_song_ids or self.tfidf_matrix is None:
            return []

        valid_indices = [
            self.song_id_to_idx[str(sid)]
            for sid in seed_song_ids
            if str(sid) in self.song_id_to_idx
        ]

        if not valid_indices:
            return []

        # Centroid of TF-IDF vectors
        user_tfidf_profile = self.tfidf_matrix[valid_indices].mean(axis=0)
        # Convert matrix to array for cosine_similarity
        user_tfidf_profile = np.asarray(user_tfidf_profile)
        text_sim = cosine_similarity(user_tfidf_profile, self.tfidf_matrix).flatten()

        if self.audio_matrix is not None:
            user_audio_profile = self.audio_matrix[valid_indices].mean(axis=0, keepdims=True)
            audio_sim = cosine_similarity(user_audio_profile, self.audio_matrix).flatten()
            total_sim = 0.75 * text_sim + 0.25 * audio_sim
        else:
            total_sim = text_sim

        seed_set = set(valid_indices)
        ranked_indices = np.argsort(-total_sim)
        candidates = []
        for i in ranked_indices:
            if i in seed_set:
                continue
            candidates.append((int(i), float(total_sim[i])))
            if len(candidates) >= top_k:
                break

        return candidates

    def save(self, model_path: Union[str, Path]) -> None:
        """Serializes the fitted recommender instance to disk."""
        path = Path(model_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    @classmethod
    def load(cls, model_path: Union[str, Path]) -> Optional["ContentBasedRecommender"]:
        """Loads a serialized recommender model from disk."""
        path = Path(model_path)
        if not path.exists():
            return None
        try:
            return joblib.load(path)
        except Exception:
            return None

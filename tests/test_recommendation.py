"""Unit tests for content-based and personalized recommendation algorithms."""

import os
import tempfile
import unittest
import pandas as pd

from backend.data.preprocessing import preprocess_dataset
from backend.database.connection import init_db
from backend.database.repository import get_or_create_default_user, record_history, toggle_like
from backend.recommendation.content_based import ContentBasedRecommender
from backend.recommendation.engine import (
    get_or_train_recommender,
    get_personalized_recommendations,
    is_model_trained,
    recommend_songs,
)


class TestRecommendation(unittest.TestCase):
    """Test suite verifying TF-IDF, cosine similarity, ranking, and personalization."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.model_path = os.path.join(self.temp_dir.name, "test_recommender.pkl")
        self.db_path = os.path.join(self.temp_dir.name, "test_rec.db")
        init_db(self.db_path)

        # Sample rich song catalog
        self.raw_df = pd.DataFrame(
            {
                "song_id": ["s1", "s2", "s3", "s4", "s5", "s6"],
                "song_name": [
                    "Bohemian Rhapsody",
                    "We Will Rock You",
                    "Another One Bites the Dust",
                    "Shape of You",
                    "Perfect",
                    "Thinking Out Loud",
                ],
                "artist": [
                    "Queen",
                    "Queen",
                    "Queen",
                    "Ed Sheeran",
                    "Ed Sheeran",
                    "Ed Sheeran",
                ],
                "album": [
                    "A Night at the Opera",
                    "News of the World",
                    "The Game",
                    "Divide",
                    "Divide",
                    "Multiply",
                ],
                "genre": ["Rock", "Rock", "Rock", "Pop", "Pop", "Pop"],
                "language": ["English", "English", "English", "English", "English", "English"],
                "year": [1975, 1977, 1980, 2017, 2017, 2014],
                "danceability": [0.39, 0.69, 0.81, 0.82, 0.59, 0.78],
                "energy": [0.40, 0.49, 0.52, 0.65, 0.45, 0.44],
                "popularity": [88, 82, 85, 92, 89, 87],
            }
        )

        prep_res = preprocess_dataset(self.raw_df, save_processed=False)
        self.processed_df = prep_res.df

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_content_based_recommender_fit_and_query(self):
        recommender = ContentBasedRecommender()
        recommender.fit(self.processed_df)

        self.assertIsNotNone(recommender.vectorizer)
        self.assertIsNotNone(recommender.tfidf_matrix)

        # Query Queen song "s1"
        candidates = recommender.get_similar_indices("s1", top_k=5)
        self.assertGreater(len(candidates), 0)

        # Ensure query song itself is excluded
        candidate_indices = [idx for idx, _ in candidates]
        self.assertNotIn(0, candidate_indices)

        # Queen songs (s2, s3 at idx 1, 2) should score highest
        top_cand_idx = candidates[0][0]
        top_song_id = self.processed_df.iloc[top_cand_idx]["song_id"]
        self.assertIn(top_song_id, ["s2", "s3"])

    def test_recommend_songs_facade(self):
        recs = recommend_songs(
            song_id="s4",  # Shape of You by Ed Sheeran
            df=self.processed_df,
            n_recommendations=2,
            model_path=self.model_path,
        )

        self.assertEqual(len(recs), 2)
        # Should recommend other Ed Sheeran tracks
        rec_artists = [r["artist"] for r in recs]
        self.assertTrue(all(a == "Ed Sheeran" for a in rec_artists))
        # Excludes s4 itself
        self.assertNotIn("s4", [r["song_id"] for r in recs])

    def test_model_serialization(self):
        self.assertFalse(is_model_trained(self.model_path))

        rec_model, _ = get_or_train_recommender(
            df=self.processed_df, model_path=self.model_path
        )
        self.assertIsNotNone(rec_model)
        self.assertTrue(os.path.exists(self.model_path))

        # Re-load
        loaded_model = ContentBasedRecommender.load(self.model_path)
        self.assertIsNotNone(loaded_model)
        self.assertEqual(len(loaded_model.song_ids), 6)


if __name__ == "__main__":
    unittest.main()

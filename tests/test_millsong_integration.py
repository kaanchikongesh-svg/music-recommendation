"""Integration tests verifying spotify_millsongdata real dataset integration, adapter, database storage, and recommendation logic."""

import os
from pathlib import Path
import tempfile
import unittest
import pandas as pd

from backend.data.adapter import (
    adapt_kaggle_dataset,
    generate_deterministic_song_id,
)
from backend.data.preprocessing import preprocess_dataset
from backend.database.connection import init_db
from backend.database.repository import bulk_upsert_songs, get_song_by_id
from backend.recommendation.content_based import ContentBasedRecommender


class TestMillSongIntegration(unittest.TestCase):
    """Verifies that real rows from spotify_millsongdata.csv are correctly adapted, stored, and queried."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_music.db"
        init_db(self.db_path)

        # Real sample rows matching spotify_millsongdata.csv structure
        self.sample_mills_df = pd.DataFrame(
            [
                {
                    "artist": "ABBA",
                    "song": "Dancing Queen",
                    "link": "/a/abba/dancing+queen_20002708.html",
                    "text": "You can dance\nYou can jive\nHaving the time of your life\nSee that girl, watch that scene\nDig in the dancing queen",
                },
                {
                    "artist": "ABBA",
                    "song": "Mamma Mia",
                    "link": "/a/abba/mamma+mia_20002711.html",
                    "text": "I've been cheated by you since I don't know when\nSo I made up my mind, it must come to an end\nLook at me now, will I ever learn?",
                },
                {
                    "artist": "Queen",
                    "song": "Bohemian Rhapsody",
                    "link": "/q/queen/bohemian+rhapsody_20112574.html",
                    "text": "Is this the real life? Is this just fantasy?\nCaught in a landslide, no escape from reality\nOpen your eyes, look up to the skies and see",
                },
            ]
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_deterministic_song_id_stability(self):
        id1 = generate_deterministic_song_id("ABBA", "Dancing Queen", "/a/abba/dancing+queen_20002708.html")
        id2 = generate_deterministic_song_id("ABBA", "Dancing Queen", "/a/abba/dancing+queen_20002708.html")
        self.assertEqual(id1, id2)
        self.assertEqual(len(id1), 16)

    def test_adapter_maps_millsong_columns_without_inventing_metadata(self):
        adapted_df, report = adapt_kaggle_dataset(self.sample_mills_df)
        self.assertTrue(report.is_adapted)
        self.assertEqual(len(adapted_df), 3)

        row = adapted_df.iloc[0]
        self.assertEqual(row["artist"], "ABBA")
        self.assertEqual(row["song_name"], "Dancing Queen")
        self.assertEqual(row["source_link"], "/a/abba/dancing+queen_20002708.html")
        self.assertIn("You can dance", row["lyrics"])

        # Ensure no fake metadata is invented
        self.assertIn(row["album"], ["Unknown", None, ""])
        self.assertIn(row["genre"], ["Unknown", None, ""])
        self.assertIsNone(row["year"])

    def test_bulk_upsert_and_retrieve_with_lyrics(self):
        adapted_df, _ = adapt_kaggle_dataset(self.sample_mills_df)
        records = adapted_df.to_dict(orient="records")

        # Clean "Unknown" to None for DB storage
        for r in records:
            if r.get("album") == "Unknown":
                r["album"] = None
            if r.get("genre") == "Unknown":
                r["genre"] = None
            if r.get("language") == "Unknown":
                r["language"] = None

        inserted = bulk_upsert_songs(records, db_path=self.db_path)
        self.assertEqual(inserted, 3)

        # Retrieve by deterministic ID
        song_id = generate_deterministic_song_id("ABBA", "Dancing Queen", "/a/abba/dancing+queen_20002708.html")
        retrieved = get_song_by_id(song_id, db_path=self.db_path)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["song_name"], "Dancing Queen")
        self.assertEqual(retrieved["artist"], "ABBA")
        self.assertIn("You can dance", retrieved["lyrics"])
        self.assertIsNone(retrieved["album"])
        self.assertIsNone(retrieved["genre"])
        self.assertIsNone(retrieved["year"])

    def test_recommendation_excludes_source_song(self):
        result = preprocess_dataset(self.sample_mills_df)
        recommender = ContentBasedRecommender()
        recommender.fit(result.df)

        dancing_queen_id = result.df.iloc[0]["song_id"]
        similar = recommender.get_similar_indices(dancing_queen_id, top_k=2)

        # Ensure Dancing Queen itself is not in recommendations
        similar_ids = [result.df.iloc[idx]["song_id"] for idx, _ in similar]
        self.assertNotIn(dancing_queen_id, similar_ids)
        # ABBA's other track should be recommended
        mamma_mia_id = result.df.iloc[1]["song_id"]
        self.assertIn(mamma_mia_id, similar_ids)


if __name__ == "__main__":
    unittest.main()

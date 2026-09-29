"""Unit tests for Kaggle and external dataset adapter (backend/data/adapter.py)."""

import unittest
import pandas as pd

from backend.data.adapter import (
    adapt_kaggle_dataset,
    clean_artist_list_string,
    extract_year_from_value,
)


class TestDatasetAdapter(unittest.TestCase):
    """Test suite verifying Kaggle column mapping, normalization, and fallbacks."""

    def test_extract_year(self):
        self.assertEqual(extract_year_from_value("2021-05-12"), 2021)
        self.assertEqual(extract_year_from_value(1999), 1999)
        self.assertEqual(extract_year_from_value("Album Released in 2004"), 2004)
        self.assertIsNone(extract_year_from_value("No Year Available"))
        self.assertIsNone(extract_year_from_value(None))

    def test_clean_artist_list_string(self):
        self.assertEqual(
            clean_artist_list_string("['Daft Punk', 'Pharrell Williams']"),
            "Daft Punk, Pharrell Williams",
        )
        self.assertEqual(clean_artist_list_string("Adele"), "Adele")
        self.assertEqual(clean_artist_list_string(None), "")

    def test_adapt_spotify_kaggle_dataset(self):
        # Kaggle Spotify dataset schema sample
        kaggle_df = pd.DataFrame(
            {
                "track_id": ["track_101", "track_102"],
                "track_name": ["Get Lucky", "Rolling in the Deep"],
                "artists": ["['Daft Punk', 'Pharrell Williams']", "Adele"],
                "album_name": ["Random Access Memories", "21"],
                "track_genre": ["disco", "pop"],
                "danceability": [0.79, 0.73],
                "energy": [0.81, 0.86],
                "tempo": [116.0, 105.0],
                "valence": [0.86, 0.52],
                "popularity": [85, 90],
                "release_date": ["2013-04-19", "2011-01-24"],
            }
        )

        adapted_df, report = adapt_kaggle_dataset(kaggle_df)

        self.assertTrue(report.is_adapted)
        self.assertEqual(len(adapted_df), 2)
        self.assertIn("song_id", adapted_df.columns)
        self.assertIn("song_name", adapted_df.columns)
        self.assertIn("artist", adapted_df.columns)
        self.assertIn("album", adapted_df.columns)
        self.assertIn("genre", adapted_df.columns)
        self.assertIn("language", adapted_df.columns)
        self.assertIn("year", adapted_df.columns)
        self.assertIn("danceability", adapted_df.columns)

        # Check values
        self.assertEqual(adapted_df.iloc[0]["song_id"], "track_101")
        self.assertEqual(adapted_df.iloc[0]["song_name"], "Get Lucky")
        self.assertEqual(adapted_df.iloc[0]["artist"], "Daft Punk, Pharrell Williams")
        self.assertEqual(adapted_df.iloc[0]["album"], "Random Access Memories")
        self.assertEqual(adapted_df.iloc[0]["genre"], "disco")
        self.assertEqual(adapted_df.iloc[0]["language"], "Unknown")
        self.assertEqual(adapted_df.iloc[0]["year"], 2013)
        self.assertEqual(adapted_df.iloc[0]["danceability"], 0.79)

    def test_adapt_dataset_missing_critical_column(self):
        # Missing artist column
        invalid_df = pd.DataFrame(
            {
                "track_name": ["Song 1", "Song 2"],
                "genre": ["Rock", "Pop"],
            }
        )
        adapted_df, report = adapt_kaggle_dataset(invalid_df)
        self.assertFalse(report.is_adapted)
        self.assertIn("artist", report.missing_required_columns)
        self.assertTrue(adapted_df.empty)


if __name__ == "__main__":
    unittest.main()

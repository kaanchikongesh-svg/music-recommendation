"""Unit tests for src/preprocessing.py data preprocessing pipeline."""

import os
import tempfile
import unittest
import numpy as np
import pandas as pd

from src.preprocessing import (
    clean_text,
    normalize_text,
    clean_year_column,
    validate_and_clean_audio_features,
    create_combined_features,
    preprocess_dataset,
    PreprocessingResult,
    DEFAULT_PROCESSED_DATA_PATH,
)


class TestPreprocessing(unittest.TestCase):
    """Test suite verifying data cleaning, deduplication, imputation, and feature extraction."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.processed_path = os.path.join(self.temp_dir.name, "songs_processed.csv")

    def tearDown(self):
        self.temp_dir.cleanup()

    def _sample_valid_df(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "song_id": ["S01", "S02", "S03"],
                "song_name": ["  Believer  ", "Blinding Lights", "Shape of You"],
                "artist": ["Imagine Dragons", "The Weeknd", "Ed Sheeran"],
                "album": ["Evolve", "After Hours", "Divide"],
                "genre": ["Rock", "Synthwave", "Pop"],
                "language": ["English", "English", "English"],
                "year": [2017, 2020, 2017],
                "danceability": [0.77, 0.51, 0.82],
                "energy": [0.78, 0.73, 0.65],
                "tempo": [125.0, 171.0, 96.0],
            }
        )

    # TEST 1: Valid dataset preprocessing
    def test_valid_dataset_preprocessing(self):
        df = self._sample_valid_df()
        result = preprocess_dataset(
            df, save_processed=True, processed_path=self.processed_path
        )

        self.assertTrue(result.is_success)
        self.assertIsNotNone(result.df)
        self.assertEqual(result.report.original_rows, 3)
        self.assertEqual(result.report.final_rows, 3)
        self.assertEqual(result.report.duplicates_removed, 0)
        self.assertIn("combined_features", result.df.columns)
        self.assertTrue(os.path.exists(self.processed_path))

    # TEST 2: Missing optional audio features
    def test_missing_optional_audio_features(self):
        df = pd.DataFrame(
            {
                "song_id": ["S01", "S02"],
                "song_name": ["Song One", "Song Two"],
                "artist": ["Artist A", "Artist B"],
                "album": ["Album A", "Album B"],
                "genre": ["Pop", "Jazz"],
                "language": ["English", "English"],
                "year": [2021, 2019],
            }
        )
        result = preprocess_dataset(
            df, save_processed=False, processed_path=self.processed_path
        )

        self.assertTrue(result.is_success)
        self.assertEqual(result.report.available_audio_features, [])
        self.assertTrue(len(result.report.missing_audio_features) > 0)
        self.assertIn("combined_features", result.df.columns)

    # TEST 3: Missing song_name
    def test_missing_song_name(self):
        df = pd.DataFrame(
            {
                "song_id": ["S01", "S02", "S03"],
                "song_name": ["Valid Song", "", None],
                "artist": ["Artist A", "Artist B", "Artist C"],
                "album": ["Album A", "Album B", "Album C"],
                "genre": ["Pop", "Rock", "Pop"],
                "language": ["English", "English", "English"],
                "year": [2020, 2021, 2022],
            }
        )
        result = preprocess_dataset(df, save_processed=False)

        self.assertTrue(result.is_success)
        self.assertEqual(result.report.missing_song_names_removed, 2)
        self.assertEqual(result.report.final_rows, 1)
        self.assertEqual(result.df.iloc[0]["song_id"], "S01")

    # TEST 4: Missing artist
    def test_missing_artist(self):
        df = pd.DataFrame(
            {
                "song_id": ["S01", "S02"],
                "song_name": ["Song A", "Song B"],
                "artist": [None, "Valid Artist"],
                "album": ["Album A", "Album B"],
                "genre": ["Pop", "Rock"],
                "language": ["English", "English"],
                "year": [2020, 2021],
            }
        )
        result = preprocess_dataset(df, save_processed=False)

        self.assertTrue(result.is_success)
        self.assertEqual(result.report.missing_artists_removed, 1)
        self.assertEqual(result.report.final_rows, 1)
        self.assertEqual(result.df.iloc[0]["song_id"], "S02")

    # TEST 5: Invalid year
    def test_invalid_year(self):
        df = pd.DataFrame(
            {
                "song_id": ["S01", "S02", "S03"],
                "song_name": ["Song A", "Song B", "Song C"],
                "artist": ["Artist A", "Artist B", "Artist C"],
                "album": ["Album A", "Album B", "Album C"],
                "genre": ["Pop", "Rock", "Jazz"],
                "language": ["English", "English", "English"],
                "year": [2021, "invalid_year", 1500],
            }
        )
        result = preprocess_dataset(df, save_processed=False)

        self.assertTrue(result.is_success)
        # Song should not be removed just for bad year, but cleaned to NaN
        self.assertEqual(result.report.final_rows, 3)
        self.assertEqual(result.report.invalid_years_handled, 2)

    # TEST 6: Duplicate song_id
    def test_duplicate_song_id(self):
        df = pd.DataFrame(
            {
                "song_id": ["S01", "S01", "S02"],
                "song_name": ["Song A", "Song A Duplicate", "Song B"],
                "artist": ["Artist A", "Artist A", "Artist B"],
                "album": ["Album A", "Album A", "Album B"],
                "genre": ["Pop", "Pop", "Rock"],
                "language": ["English", "English", "English"],
                "year": [2020, 2020, 2021],
            }
        )
        result = preprocess_dataset(df, save_processed=False)

        self.assertTrue(result.is_success)
        self.assertEqual(result.report.original_rows, 3)
        self.assertEqual(result.report.duplicates_removed, 1)
        self.assertEqual(result.report.final_rows, 2)

    # TEST 7: Invalid audio feature values
    def test_invalid_audio_feature_values(self):
        df = pd.DataFrame(
            {
                "song_id": ["S01", "S02"],
                "song_name": ["Song A", "Song B"],
                "artist": ["Artist A", "Artist B"],
                "album": ["Album A", "Album B"],
                "genre": ["Pop", "Rock"],
                "language": ["English", "English"],
                "year": [2020, 2021],
                "danceability": [1.85, -0.2],  # Out of [0, 1] bounds
                "tempo": [-50.0, 120.0],       # Negative tempo
            }
        )
        result = preprocess_dataset(df, save_processed=False)

        self.assertTrue(result.is_success)
        self.assertIn("danceability", result.report.invalid_audio_values_fixed)
        self.assertIn("tempo", result.report.invalid_audio_values_fixed)
        # Verify clamped values
        self.assertLessEqual(result.df["danceability"].max(), 1.0)
        self.assertGreaterEqual(result.df["danceability"].min(), 0.0)
        self.assertGreater(result.df["tempo"].min(), 0.0)

    # TEST 8: Empty dataset
    def test_empty_dataset(self):
        empty_df = pd.DataFrame()
        result = preprocess_dataset(empty_df, save_processed=False)

        self.assertFalse(result.is_success)
        self.assertIsNone(result.df)
        self.assertTrue(len(result.errors) > 0)

    # TEST 9: Combined feature generation
    def test_combined_feature_generation(self):
        df = pd.DataFrame(
            {
                "song_id": ["S01"],
                "song_name": ["  Believer  "],
                "artist": ["Imagine Dragons"],
                "album": ["Evolve"],
                "genre": ["Rock"],
                "language": ["English"],
                "year": [2017],
            }
        )
        result = preprocess_dataset(df, save_processed=False)

        self.assertTrue(result.is_success)
        combined = result.df.iloc[0]["combined_features"]
        self.assertEqual(
            combined, "believer imagine dragons evolve rock english"
        )

    # TEST 10: Raw dataset remains unchanged
    def test_raw_dataset_remains_unchanged(self):
        raw_df = self._sample_valid_df()
        original_cols = list(raw_df.columns)
        original_values = raw_df["song_name"].tolist()

        result = preprocess_dataset(raw_df, save_processed=False)

        self.assertTrue(result.is_success)
        # Verify original raw_df was not mutated
        self.assertEqual(list(raw_df.columns), original_cols)
        self.assertEqual(raw_df["song_name"].tolist(), original_values)
        self.assertNotIn("combined_features", raw_df.columns)


if __name__ == "__main__":
    unittest.main()

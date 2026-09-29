"""Verification tests for UI state handling (State A, State B, State C)."""

import os
import tempfile
import unittest
import pandas as pd

from src.data_loader import (
    load_dataset,
    save_uploaded_dataset,
    filter_songs,
    get_dataset_statistics,
)
from src.database import init_db, get_or_create_default_user, get_user_stats


class TestUIStates(unittest.TestCase):
    """Verifies that the data layer and state engines handle all 3 dataset states properly."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "music_state_test.db")
        init_db(self.db_path)
        self.user = get_or_create_default_user(db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    # State B: Dataset missing
    def test_state_b_missing_dataset(self):
        missing_path = os.path.join(self.temp_dir.name, "no_songs.csv")
        result = load_dataset(missing_path)

        self.assertFalse(result.is_valid)
        self.assertIsNone(result.df)
        self.assertTrue(len(result.errors) > 0)
        # Stats handle None/empty safely without crashing
        stats = get_dataset_statistics(result.df)
        self.assertEqual(stats["total_songs"], 0)
        filtered = filter_songs(result.df, "rock")
        self.assertTrue(filtered.empty)

    # State A: Valid dataset
    def test_state_a_valid_dataset(self):
        csv_data = (
            "song_id,song_name,artist,album,genre,language,year,danceability,energy,valence\n"
            "S01,Believer,Imagine Dragons,Evolve,Rock,English,2017,0.77,0.78,0.66\n"
            "S02,Blinding Lights,The Weeknd,After Hours,Synthwave,English,2020,0.51,0.73,0.33\n"
            "S03,Shape of You,Ed Sheeran,Divide,Pop,English,2017,0.82,0.65,0.93\n"
        )
        path = os.path.join(self.temp_dir.name, "songs.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write(csv_data)

        result = load_dataset(path)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.total_songs, 3)

        # Statistics
        stats = get_dataset_statistics(result.df)
        self.assertEqual(stats["total_songs"], 3)
        self.assertEqual(stats["total_artists"], 3)
        self.assertIn("Rock", stats["genres_list"])

        # Search filtering
        rock_songs = filter_songs(result.df, genre="Rock")
        self.assertEqual(len(rock_songs), 1)
        self.assertEqual(rock_songs.iloc[0]["song_name"], "Believer")

    # State C: Invalid dataset
    def test_state_c_invalid_dataset(self):
        csv_data = "song_id,song_name\nS01,Incomplete Song\n"
        path = os.path.join(self.temp_dir.name, "invalid.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write(csv_data)

        result = load_dataset(path)
        self.assertFalse(result.is_valid)
        self.assertTrue(len(result.missing_required_columns) > 0)


if __name__ == "__main__":
    unittest.main()

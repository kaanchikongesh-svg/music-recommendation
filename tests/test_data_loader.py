"""Unit tests for src/data_loader.py."""

import os
import tempfile
import unittest
import pandas as pd

from src.data_loader import (
    load_dataset,
    validate_dataset,
    detect_audio_features,
    get_optional_features,
    save_uploaded_dataset,
    REQUIRED_COLUMNS,
    OPTIONAL_AUDIO_FEATURES,
    ValidationResult,
)


class TestDataLoader(unittest.TestCase):
    """Test suite verifying dataset loading, schema validation, and error handling."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_temp_csv(self, filename: str, content: str) -> str:
        filepath = os.path.join(self.temp_dir.name, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath

    # 1. Valid CSV dataset (with optional audio features)
    def test_valid_csv_dataset(self):
        csv_data = (
            "song_id,song_name,artist,album,genre,language,year,danceability,energy,valence\n"
            "S001,Song One,Artist A,Album A,Pop,English,2021,0.85,0.78,0.92\n"
            "S002,Song Two,Artist B,Album B,Rock,English,2019,0.55,0.89,0.45\n"
        )
        path = self._create_temp_csv("valid.csv", csv_data)
        result = load_dataset(path)

        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(result.total_songs, 2)
        self.assertEqual(result.unique_artists, 2)
        self.assertEqual(result.unique_genres, 2)
        self.assertIn("danceability", result.detected_audio_features)
        self.assertIn("energy", result.detected_audio_features)
        self.assertIn("valence", result.detected_audio_features)

    # 2. Missing CSV file
    def test_missing_csv_file(self):
        non_existent_path = os.path.join(self.temp_dir.name, "does_not_exist.csv")
        result = load_dataset(non_existent_path)

        self.assertFalse(result.is_valid)
        self.assertIsNone(result.df)
        self.assertTrue(any("not found" in err.lower() for err in result.errors))

    # 3. Empty CSV file (0 bytes and header-only empty)
    def test_empty_csv_file(self):
        path = self._create_temp_csv("empty.csv", "")
        result = load_dataset(path)

        self.assertFalse(result.is_valid)
        self.assertTrue(any("empty" in err.lower() for err in result.errors))

    # 4. Missing required columns
    def test_missing_required_columns(self):
        csv_data = (
            "song_id,song_name,artist\n"
            "S001,Song One,Artist A\n"
        )
        path = self._create_temp_csv("missing_cols.csv", csv_data)
        result = load_dataset(path)

        self.assertFalse(result.is_valid)
        self.assertIn("album", result.missing_required_columns)
        self.assertIn("genre", result.missing_required_columns)
        self.assertIn("language", result.missing_required_columns)
        self.assertIn("year", result.missing_required_columns)
        self.assertTrue(any("Missing required columns" in err for err in result.errors))

    # 5. Missing optional audio features (valid dataset without audio features)
    def test_missing_optional_audio_features(self):
        csv_data = (
            "song_id,song_name,artist,album,genre,language,year\n"
            "S001,Song One,Artist A,Album A,Pop,English,2021\n"
            "S002,Song Two,Artist B,Album B,Jazz,English,2020\n"
        )
        path = self._create_temp_csv("no_audio_features.csv", csv_data)
        result = load_dataset(path)

        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(result.detected_audio_features, [])
        self.assertEqual(result.total_songs, 2)

    # 6. Duplicate song IDs
    def test_duplicate_song_ids(self):
        csv_data = (
            "song_id,song_name,artist,album,genre,language,year\n"
            "S001,Song One,Artist A,Album A,Pop,English,2021\n"
            "S001,Song One Duplicate,Artist A,Album A,Pop,English,2021\n"
        )
        path = self._create_temp_csv("duplicates.csv", csv_data)
        result = load_dataset(path)

        self.assertTrue(result.is_valid)  # Valid but has warnings
        self.assertTrue(any("duplicate" in warn.lower() for warn in result.warnings))

    # 7. Invalid year values
    def test_invalid_year_values(self):
        csv_data = (
            "song_id,song_name,artist,album,genre,language,year\n"
            "S001,Song One,Artist A,Album A,Pop,English,abc_invalid_year\n"
            "S002,Song Two,Artist B,Album B,Pop,English,1500\n"
        )
        path = self._create_temp_csv("invalid_year.csv", csv_data)
        result = load_dataset(path)

        self.assertTrue(result.is_valid)
        self.assertTrue(any("year" in warn.lower() for warn in result.warnings))

    # 8. Malformed CSV input
    def test_malformed_csv_input(self):
        # CSV with unequal number of columns causing parser error
        csv_data = (
            "song_id,song_name,artist,album,genre,language,year\n"
            "S001,Song One,Artist A,Album A,Pop,English,2021\n"
            "S002,Song Two,Artist B,Album B,Pop,English,2021,ExtraField1,ExtraField2\n"
        )
        path = self._create_temp_csv("malformed.csv", csv_data)
        result = load_dataset(path)

        self.assertFalse(result.is_valid)
        self.assertTrue(any("parsing error" in err.lower() for err in result.errors))

    # 9. save_uploaded_dataset with valid in-memory file
    def test_save_uploaded_dataset_valid(self):
        import io
        csv_bytes = (
            "song_id,song_name,artist,album,genre,language,year\n"
            "U01,Upload Song,Upload Artist,Upload Album,Pop,English,2022\n"
        ).encode("utf-8")
        uploaded_file = io.BytesIO(csv_bytes)
        target_path = os.path.join(self.temp_dir.name, "saved_songs.csv")

        result = save_uploaded_dataset(uploaded_file, target_path=target_path)
        self.assertTrue(result.is_valid)
        self.assertTrue(os.path.exists(target_path))
        self.assertEqual(result.total_songs, 1)

    # 10. save_uploaded_dataset with invalid in-memory file
    def test_save_uploaded_dataset_invalid(self):
        import io
        csv_bytes = "invalid,header\n1,2\n".encode("utf-8")
        uploaded_file = io.BytesIO(csv_bytes)
        target_path = os.path.join(self.temp_dir.name, "should_not_save.csv")

        result = save_uploaded_dataset(uploaded_file, target_path=target_path)
        self.assertFalse(result.is_valid)
        self.assertFalse(os.path.exists(target_path))


if __name__ == "__main__":
    unittest.main()

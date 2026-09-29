"""Unit tests for high-level business services (backend/services)."""

import os
import tempfile
import unittest
import pandas as pd

from backend.database.connection import init_db
from backend.services.history_service import (
    check_is_favorite,
    get_user_favorite_tracks,
    get_user_timeline_history,
    log_play_action,
    toggle_song_favorite,
)
from backend.services.music_service import (
    get_featured_tracks,
    get_song_details,
    get_top_genres,
    search_and_filter_tracks,
)
from backend.services.playlist_service import (
    add_track_to_playlist,
    create_user_playlist,
    delete_user_playlist,
    get_playlist_track_details,
    list_user_playlists,
    remove_track_from_playlist,
)
from backend.services.user_service import (
    get_default_user,
    get_user_profile_analytics,
)


class TestServices(unittest.TestCase):
    """Test suite verifying business service abstractions."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_services.db")
        init_db(self.db_path)

        self.df = pd.DataFrame(
            {
                "song_id": ["song_1", "song_2", "song_3"],
                "song_name": ["Starlight", "Supermassive Black Hole", "Viva La Vida"],
                "artist": ["Muse", "Muse", "Coldplay"],
                "album": ["Black Holes and Revelations", "Black Holes and Revelations", "Viva La Vida"],
                "genre": ["Alternative Rock", "Alternative Rock", "Pop Rock"],
                "language": ["English", "English", "English"],
                "year": [2006, 2006, 2008],
                "popularity": [75, 80, 85],
            }
        )
        self.user = get_default_user(db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_music_service_queries(self):
        # Details
        details = get_song_details("song_1", df=self.df)
        self.assertIsNotNone(details)
        self.assertEqual(details["song_name"], "Starlight")

        # Top genres
        genres = get_top_genres(limit=2, df=self.df)
        self.assertIn("Alternative Rock", genres)

        # Search
        filtered = search_and_filter_tracks(search_query="Viva", df=self.df)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered.iloc[0]["artist"], "Coldplay")

    def test_playlist_service_lifecycle(self):
        uid = self.user["id"]
        pl_id = create_user_playlist(uid, "Space Rock Mix", db_path=self.db_path)
        self.assertIsNotNone(pl_id)

        playlists = list_user_playlists(uid, db_path=self.db_path)
        self.assertGreater(len(playlists), 0)

        # Add & retrieve track
        added = add_track_to_playlist(pl_id, "song_1", db_path=self.db_path)
        self.assertTrue(added)

        tracks = get_playlist_track_details(pl_id, df=self.df, db_path=self.db_path)
        self.assertEqual(len(tracks), 1)
        self.assertEqual(tracks[0]["song_name"], "Starlight")

        # Remove track
        removed = remove_track_from_playlist(pl_id, "song_1", db_path=self.db_path)
        self.assertTrue(removed)

        # Delete playlist
        deleted = delete_user_playlist(pl_id, user_id=uid, db_path=self.db_path)
        self.assertTrue(deleted)

    def test_user_analytics_calculation(self):
        uid = self.user["id"]
        # Log interactions
        log_play_action(uid, "song_1", db_path=self.db_path)
        log_play_action(uid, "song_2", db_path=self.db_path)
        toggle_song_favorite(uid, "song_1", db_path=self.db_path)

        analytics = get_user_profile_analytics(uid, df=self.df, db_path=self.db_path)
        self.assertGreaterEqual(analytics["total_plays"], 2)
        self.assertGreaterEqual(analytics["total_likes"], 1)
        self.assertEqual(analytics["favorite_genre"], "Alternative Rock")
        self.assertEqual(analytics["favorite_artist"], "Muse")


if __name__ == "__main__":
    unittest.main()

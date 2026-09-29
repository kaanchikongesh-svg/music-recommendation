"""Unit tests for src/database.py."""

import os
import tempfile
import unittest

from backend.database.repository import (
    init_db,
    get_or_create_default_user,
    record_history,
    clear_user_history,
    toggle_like,
    toggle_dislike,
    is_liked,
    get_user_likes,
    get_user_history,
    create_playlist,
    rename_playlist,
    get_user_playlists,
    add_song_to_playlist,
    remove_song_from_playlist,
    get_playlist_songs,
    get_user_stats,
)


class TestDatabase(unittest.TestCase):
    """Test suite verifying SQLite operations, schema creation, and user interactions."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_music.db")
        init_db(self.db_path)
        self.user = get_or_create_default_user(
            username="TestUser", email="test@test.local", db_path=self.db_path
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_user_creation_and_retrieval(self):
        user2 = get_or_create_default_user(
            username="TestUser", db_path=self.db_path
        )
        self.assertEqual(self.user["id"], user2["id"])
        self.assertEqual(user2["username"], "TestUser")

    def test_likes_and_dislikes(self):
        song_id = "song_123"

        # Initially not liked
        self.assertFalse(is_liked(self.user["id"], song_id, db_path=self.db_path))

        # Like the song
        status = toggle_like(self.user["id"], song_id, db_path=self.db_path)
        self.assertTrue(status)
        self.assertTrue(is_liked(self.user["id"], song_id, db_path=self.db_path))
        self.assertIn(song_id, get_user_likes(self.user["id"], db_path=self.db_path))

        # Unlike the song
        status = toggle_like(self.user["id"], song_id, db_path=self.db_path)
        self.assertFalse(status)
        self.assertFalse(is_liked(self.user["id"], song_id, db_path=self.db_path))

        # Dislike the song
        dislike_status = toggle_dislike(self.user["id"], song_id, db_path=self.db_path)
        self.assertTrue(dislike_status)

    def test_listening_history(self):
        record_history(self.user["id"], "track_1", action="PLAY", db_path=self.db_path)
        record_history(self.user["id"], "track_2", action="PLAY", db_path=self.db_path)

        history = get_user_history(self.user["id"], limit=10, db_path=self.db_path)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["song_id"], "track_2")
        self.assertEqual(history[1]["song_id"], "track_1")

    def test_playlists_management(self):
        pl_id = create_playlist(self.user["id"], "My Rock Mix", db_path=self.db_path)
        self.assertGreater(pl_id, 0)

        playlists = get_user_playlists(self.user["id"], db_path=self.db_path)
        self.assertEqual(len(playlists), 1)
        self.assertEqual(playlists[0]["playlist_name"], "My Rock Mix")

        # Add song to playlist
        added = add_song_to_playlist(pl_id, "track_100", db_path=self.db_path)
        self.assertTrue(added)

        # Duplicate addition should return False
        added_dup = add_song_to_playlist(pl_id, "track_100", db_path=self.db_path)
        self.assertFalse(added_dup)

        songs = get_playlist_songs(pl_id, db_path=self.db_path)
        self.assertEqual(len(songs), 1)
        self.assertEqual(songs[0]["song_id"], "track_100")

        # Rename playlist
        renamed = rename_playlist(pl_id, self.user["id"], "Classic Rock Mix", db_path=self.db_path)
        self.assertTrue(renamed)
        updated_playlists = get_user_playlists(self.user["id"], db_path=self.db_path)
        self.assertEqual(updated_playlists[0]["playlist_name"], "Classic Rock Mix")

        # Remove song
        removed = remove_song_from_playlist(pl_id, "track_100", db_path=self.db_path)
        self.assertTrue(removed)
        self.assertEqual(len(get_playlist_songs(pl_id, db_path=self.db_path)), 0)

    def test_clear_listening_history(self):
        record_history(self.user["id"], "track_1", action="PLAY", db_path=self.db_path)
        record_history(self.user["id"], "track_2", action="PLAY", db_path=self.db_path)
        self.assertEqual(len(get_user_history(self.user["id"], db_path=self.db_path)), 2)

        cleared = clear_user_history(self.user["id"], db_path=self.db_path)
        self.assertTrue(cleared)
        self.assertEqual(len(get_user_history(self.user["id"], db_path=self.db_path)), 0)

    def test_user_stats(self):
        record_history(self.user["id"], "t1", action="PLAY", db_path=self.db_path)
        record_history(self.user["id"], "t2", action="PLAY", db_path=self.db_path)
        toggle_like(self.user["id"], "t1", db_path=self.db_path)
        create_playlist(self.user["id"], "Chill", db_path=self.db_path)

        stats = get_user_stats(self.user["id"], db_path=self.db_path)
        self.assertEqual(stats["total_plays"], 2)
        self.assertEqual(stats["total_likes"], 1)
        self.assertEqual(stats["total_playlists"], 1)


if __name__ == "__main__":
    unittest.main()

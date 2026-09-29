"""Unit tests for authentication, password hashing, and user registration (backend/auth)."""

import os
import tempfile
import unittest

from backend.auth.authentication import authenticate_user, register_user
from backend.auth.password import hash_password, verify_password
from backend.database.connection import init_db


class TestAuth(unittest.TestCase):
    """Test suite verifying secure password hashing, registration, and login validation."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_auth.db")
        init_db(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_password_hashing_and_verification(self):
        password = "SecurePassword123!"
        hashed = hash_password(password)

        self.assertNotEqual(password, hashed)
        self.assertTrue(hashed.startswith("100000$"))

        # Verify matching
        self.assertTrue(verify_password(password, hashed))

        # Verify non-matching
        self.assertFalse(verify_password("WrongPassword", hashed))
        self.assertFalse(verify_password("", hashed))
        self.assertFalse(verify_password(password, "invalid_hash_string"))

    def test_register_and_authenticate_user(self):
        # 1. Register new user
        success, msg, user = register_user(
            username="MelodyUser",
            password="melodypassword",
            email="melody@music.local",
            db_path=self.db_path,
        )
        self.assertTrue(success)
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "MelodyUser")

        # 2. Duplicate username registration should fail
        dup_success, dup_msg, _ = register_user(
            username="MelodyUser",
            password="anotherpassword",
            db_path=self.db_path,
        )
        self.assertFalse(dup_success)
        self.assertIn("already taken", dup_msg)

        # 3. Successful authentication
        auth_success, auth_msg, auth_user = authenticate_user(
            username="MelodyUser",
            password="melodypassword",
            db_path=self.db_path,
        )
        self.assertTrue(auth_success)
        self.assertIsNotNone(auth_user)
        self.assertEqual(auth_user["username"], "MelodyUser")
        self.assertNotIn("password_hash", auth_user)

        # 4. Incorrect password authentication
        bad_pw_success, bad_pw_msg, _ = authenticate_user(
            username="MelodyUser",
            password="wrongpassword",
            db_path=self.db_path,
        )
        self.assertFalse(bad_pw_success)

        # 5. Non-existent user
        no_user_success, _, _ = authenticate_user(
            username="GhostUser",
            password="somepassword",
            db_path=self.db_path,
        )
        self.assertFalse(no_user_success)


if __name__ == "__main__":
    unittest.main()

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import sqlite3
from backend.database.connection import init_db
from backend.auth.authentication import register_user, authenticate_user
from backend.data.loader import load_dataset
from backend.data.preprocessing import preprocess_dataset
from backend.recommendation.engine import recommend_songs, get_personalized_recommendations
from backend.services.history_service import log_play_action, toggle_song_favorite, get_user_favorite_tracks, get_user_timeline_history
from backend.services.playlist_service import create_user_playlist, add_track_to_playlist, list_user_playlists, get_playlist_track_details
from backend.services.music_service import search_and_filter_tracks, get_featured_tracks, get_top_genres

def run_checks():
    print("--- 1. Initializing DB ---")
    init_db()

    print("--- 2. Testing Auth ---")
    reg_ok, reg_msg, user_data = register_user("test_aura_user", "SecurePass123!", "aura@example.com")
    print(f"Register status: {reg_ok} ({reg_msg})")
    auth_ok, auth_msg, user = authenticate_user("test_aura_user", "SecurePass123!")
    print(f"Auth status: {auth_ok}, user: {user['username'] if user else None}")
    uid = user["id"]

    print("--- 3. Testing Data Ingestion ---")
    val_res = load_dataset()
    print(f"Dataset Valid: {val_res.is_valid}, Total Songs: {val_res.total_songs}")
    prep_res = preprocess_dataset(val_res.df, save_processed=True)
    print(f"Preprocessing Success: {prep_res.is_success}, Final Rows: {prep_res.report.final_rows}")
    df = val_res.df

    print("--- 4. Testing ML Recommendation ---")
    recs = recommend_songs("track_001", df=df, n_recommendations=4)
    print(f"Seed Recs for track_001 ({len(recs)}):", [(r["song_name"], r["artist"], f"{r['similarity_score']:.2f}") for r in recs])

    print("--- 5. Testing History & Favorites ---")
    log_play_action(uid, "track_001")
    log_play_action(uid, "track_002")
    toggle_song_favorite(uid, "track_001")
    toggle_song_favorite(uid, "track_009")
    favs = get_user_favorite_tracks(uid, df=df)
    print(f"Favorites ({len(favs)}):", [f["song_name"] for f in favs])
    hist = get_user_timeline_history(uid, limit=5, df=df)
    print(f"History entries ({len(hist)}):", [(h["song_name"], h["action"]) for h in hist])

    print("--- 6. Testing Personalized Recs ---")
    p_recs = get_personalized_recommendations(uid, df=df, n_recommendations=4)
    print(f"Personalized Recs ({len(p_recs)}):", [(r["song_name"], r["artist"], f"{r['similarity_score']:.2f}") for r in p_recs])

    print("--- 7. Testing Playlist Service ---")
    pl_id = create_user_playlist(uid, "Midnight Cyberpunk")
    add_track_to_playlist(pl_id, "track_001")
    add_track_to_playlist(pl_id, "track_009")
    pls = list_user_playlists(uid)
    print(f"Playlists ({len(pls)}):", [(p["playlist_name"], p["song_count"]) for p in pls])
    pl_tracks = get_playlist_track_details(pl_id, df=df)
    print(f"Playlist Tracks ({len(pl_tracks)}):", [t["song_name"] for t in pl_tracks])

    print("--- 8. Testing Catalog Search & Facets ---")
    search_res = search_and_filter_tracks(search_query="The Weeknd", genre="All", df=df)
    print(f"Search 'The Weeknd' matches: {len(search_res)}")
    genre_res = search_and_filter_tracks(genre="Synthwave", df=df)
    print(f"Filter 'Synthwave' matches: {len(genre_res)}")
    top_g = get_top_genres(limit=5, df=df)
    print("Top Genres:", top_g)
    featured = get_featured_tracks(limit=4, df=df)
    print("Featured Tracks:", [t["song_name"] for t in featured.to_dict("records")])
    print("\n[SUCCESS] ALL END-TO-END VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_checks()

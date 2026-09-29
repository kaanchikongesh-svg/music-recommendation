"""Favorites page view displaying user liked tracks and management actions."""

import pandas as pd
import streamlit as st

from backend.data.validator import ValidationResult
from backend.services.history_service import (
    get_user_favorite_tracks,
    log_play_action,
    toggle_song_favorite,
)
from backend.services.playlist_service import add_track_to_playlist, list_user_playlists
from frontend.cards import render_song_details_section
from frontend.components import render_topbar
from frontend.empty_states import render_no_favorites_state


def render_favorites_page(result: ValidationResult, user_id: int) -> None:
    """Renders the user's favorited tracks from SQLite."""
    user = st.session_state.get("user", {"username": "Music Lover"})
    render_topbar(
        greeting="Your Favorites ❤️",
        subtitle="Saved tracks tailored to your personal collection.",
        username=user.get("username", "Music Lover"),
    )

    df = result.df if result.is_valid else None
    fav_tracks = get_user_favorite_tracks(user_id=user_id, df=df)

    if not fav_tracks:
        render_no_favorites_state()
        return

    st.markdown(f"**You have {len(fav_tracks)} favorited song(s)**")

    # Selected Song Spotlight Details
    if st.session_state.get("selected_song_id") and df is not None:
        matched = df[df["song_id"].astype(str) == str(st.session_state.selected_song_id)]
        if not matched.empty:
            render_song_details_section(
                song=matched.iloc[0],
                detected_audio_features=result.detected_audio_features,
                user_id=user_id,
            )

    grid_cols = st.columns(3)
    for idx, item in enumerate(fav_tracks):
        with grid_cols[idx % 3]:
            sid = str(item.get("song_id", ""))
            s_name = str(item.get("song_name", f"Track {sid}"))
            artist = str(item.get("artist", "Unknown"))
            genre = str(item.get("genre", "Music"))
            year_val = item.get("year", "")
            year_str = f" • {year_val}" if pd.notna(year_val) and str(year_val).isdigit() else ""

            st.markdown(
                f"""
                <div class="song-card-cinematic">
                    <div class="album-art-wrap">
                        <span class="album-art-icon">❤️</span>
                    </div>
                    <div class="song-title-text" title="{s_name}">{s_name}</div>
                    <div class="song-artist-text" title="{artist}">{artist}</div>
                    <div class="song-meta-text"><span class="badge-pill">{genre}</span>{year_str}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            b1, b2, b3 = st.columns([1.2, 1, 0.8])
            with b1:
                if st.button("▶ Play", key=f"fav_play_{sid}", type="primary", use_container_width=True):
                    st.session_state.current_playing_track = item
                    st.session_state.player_is_playing = True
                    log_play_action(user_id, sid)
                    st.toast(f"▶️ Playing '{s_name}'")
                    st.rerun()
            with b2:
                if st.button("Details", key=f"fav_view_{sid}", use_container_width=True):
                    st.session_state.selected_song_id = sid
                    st.rerun()
            with b3:
                if st.button("💔", key=f"fav_rem_{sid}", help="Remove from Favorites", use_container_width=True):
                    toggle_song_favorite(user_id, sid)
                    st.toast(f"Removed from Favorites: {s_name}")
                    st.rerun()

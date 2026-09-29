"""Presentation cards for songs, playlists, recommendations, and detail views."""

from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st

from backend.database.repository import is_liked
from backend.recommendation.engine import recommend_songs
from backend.services.history_service import log_play_action, toggle_song_favorite
from backend.services.playlist_service import (
    add_track_to_playlist,
    list_user_playlists,
)
from frontend.components import render_audio_radar_chart
from frontend.empty_states import render_no_recommendations_state


def render_song_card(
    song: pd.Series,
    user_id: int,
    key_prefix: str = "card",
) -> None:
    """Renders a single cinematic song card with album art, metadata, and action buttons."""
    sid = str(song["song_id"])
    s_name = str(song["song_name"])
    artist = str(song["artist"])
    genre = str(song.get("genre", "Unknown"))
    language = str(song.get("language", "Unknown"))
    year_val = song.get("year", "")
    year_str = f" • {year_val}" if pd.notna(year_val) and str(year_val).isdigit() else ""

    liked = is_liked(user_id, sid)
    heart_icon = "❤️" if liked else "🤍"

    st.markdown(
        f"""
        <div class="song-card-cinematic">
            <div class="album-art-wrap">
                <span class="album-art-icon">🎵</span>
            </div>
            <div class="song-title-text" title="{s_name}">{s_name}</div>
            <div class="song-artist-text" title="{artist}">{artist}</div>
            <div class="song-meta-text"><span class="badge-pill">{genre}</span> • {language}{year_str}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    b1, b2, b3 = st.columns([1.2, 1, 0.8])
    with b1:
        if st.button("▶ Play", key=f"{key_prefix}_play_{sid}", type="primary", use_container_width=True):
            st.session_state.current_playing_track = song.to_dict()
            st.session_state.player_is_playing = True
            log_play_action(user_id, sid)
            st.toast(f"▶️ Now Playing '{s_name}'")
            st.rerun()
    with b2:
        if st.button("Details", key=f"{key_prefix}_det_{sid}", use_container_width=True):
            st.session_state.selected_song_id = sid
            log_play_action(user_id, sid)
            st.rerun()
    with b3:
        if st.button(heart_icon, key=f"{key_prefix}_like_{sid}", use_container_width=True):
            status = toggle_song_favorite(user_id, sid)
            msg = "Added to Favorites" if status else "Removed from Favorites"
            st.toast(f"{msg}: {s_name}")
            st.rerun()


def render_recommendation_card(
    rec: Dict[str, Any],
    user_id: int,
    key_prefix: str = "rec",
) -> None:
    """Renders a recommendation card with similarity score badge and quick play/detail actions."""
    sid = str(rec["song_id"])
    s_name = str(rec["song_name"])
    artist = str(rec["artist"])
    genre = str(rec.get("genre", "Unknown"))
    score = rec.get("similarity_score", 0.0)

    liked = is_liked(user_id, sid)
    heart_icon = "❤️" if liked else "🤍"

    st.markdown(
        f"""
        <div class="song-card-cinematic">
            <div class="album-art-wrap" style="height: 100px;">
                <span class="album-art-icon" style="font-size: 1.8rem;">✨</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="max-width: 65%;">
                    <div class="song-title-text" title="{s_name}">{s_name}</div>
                    <div class="song-artist-text" title="{artist}">{artist}</div>
                </div>
                <div>
                    <span class="score-pill">{int(score * 100)}% Match</span>
                </div>
            </div>
            <div class="song-meta-text" style="margin-top: 6px;">
                <span class="badge-pill">{genre}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    b1, b2, b3 = st.columns([1.2, 1, 0.8])
    with b1:
        if st.button("▶ Play", key=f"{key_prefix}_play_{sid}", type="primary", use_container_width=True):
            st.session_state.current_playing_track = rec
            st.session_state.player_is_playing = True
            log_play_action(user_id, sid)
            st.toast(f"▶️ Playing '{s_name}'")
            st.rerun()
    with b2:
        if st.button("Details", key=f"{key_prefix}_view_{sid}", use_container_width=True):
            st.session_state.selected_song_id = sid
            log_play_action(user_id, sid)
            st.rerun()
    with b3:
        if st.button(heart_icon, key=f"{key_prefix}_like_{sid}", use_container_width=True):
            toggle_song_favorite(user_id, sid)
            st.rerun()


def render_song_details_section(
    song: pd.Series,
    detected_audio_features: List[str],
    user_id: int,
) -> None:
    """Renders expanded song details, audio radar chart, action buttons, and recommendation results."""
    sid = str(song["song_id"])
    s_name = str(song["song_name"])
    artist = str(song["artist"])
    album = str(song.get("album", "Unknown"))
    genre = str(song.get("genre", "Unknown"))
    language = str(song.get("language", "Unknown"))
    year_val = song.get("year", "Unknown")

    st.markdown("---")
    st.subheader(f"🎶 Track Spotlight: {s_name}")
    st.caption(f"by **{artist}** • Album: *{album}*")

    col1, col2 = st.columns([1.2, 1])

    with col1:
        meta_c1, meta_c2, meta_c3 = st.columns(3)
        with meta_c1:
            st.markdown(f"**Genre:** `{genre}`")
        with meta_c2:
            st.markdown(f"**Language:** `{language}`")
        with meta_c3:
            st.markdown(f"**Year:** `{year_val}`")

        # Action Buttons
        st.markdown("#### Controls & Actions")
        liked = is_liked(user_id, sid)
        btn_c1, btn_c2, btn_c3 = st.columns(3)

        with btn_c1:
            if st.button("▶️ Play Now", key=f"det_play_btn_{sid}", type="primary", use_container_width=True):
                st.session_state.current_playing_track = song.to_dict()
                st.session_state.player_is_playing = True
                log_play_action(user_id, sid)
                st.toast(f"▶️ Playing '{s_name}'")
                st.rerun()

        with btn_c2:
            like_label = "❤️ Favorited" if liked else "🤍 Favorite"
            if st.button(like_label, key=f"det_like_btn_{sid}", use_container_width=True):
                new_status = toggle_song_favorite(user_id, sid)
                msg = "Added to Favorites" if new_status else "Removed from Favorites"
                st.toast(f"{msg}: {s_name}")
                st.rerun()

        with btn_c3:
            if st.button("✕ Close View", key=f"det_close_btn_{sid}", use_container_width=True):
                st.session_state.selected_song_id = None
                st.rerun()

        # Add to playlist
        playlists = list_user_playlists(user_id)
        if playlists:
            with st.expander("➕ Add to Playlist"):
                pl_names = {p["playlist_name"]: p["id"] for p in playlists}
                chosen_pl = st.selectbox("Select Playlist", list(pl_names.keys()), key=f"det_pl_sel_{sid}")
                if st.button("Add to Playlist", key=f"det_add_pl_btn_{sid}"):
                    pl_id = pl_names[chosen_pl]
                    added = add_track_to_playlist(pl_id, sid)
                    if added:
                        st.success(f"Added to '{chosen_pl}'")
                    else:
                        st.info("Song is already in this playlist.")

    with col2:
        if detected_audio_features:
            fig = render_audio_radar_chart(song.to_dict(), detected_audio_features)
            if fig:
                st.markdown("#### Audio Feature Profile")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Audio features are not numeric for this track.")

    # Recommendations for this specific track
    st.markdown("#### ✨ Similar Songs (Machine Learning Recommendations)")
    recs = recommend_songs(sid, n_recommendations=6)
    if recs:
        rec_cols = st.columns(3)
        for idx, rec_item in enumerate(recs):
            with rec_cols[idx % 3]:
                render_recommendation_card(rec_item, user_id, key_prefix=f"sub_rec_{idx}")
    else:
        render_no_recommendations_state()

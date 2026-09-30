"""Persistent Mini Music Player component docked at the bottom of the dashboard."""

from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st

from backend.database.repository import is_liked
from backend.services.history_service import log_play_action, toggle_song_favorite


def render_music_player(user_id: int, df: Optional[pd.DataFrame] = None) -> None:
    """Renders the persistent dark-cinematic bottom music player dock."""
    current_track = st.session_state.get("current_playing_track")

    # If no explicit track set, try falling back to selected_song_id if available
    if current_track is None and st.session_state.get("selected_song_id") and df is not None and not df.empty:
        matched = df[df["song_id"].astype(str) == str(st.session_state.selected_song_id)]
        if not matched.empty:
            current_track = matched.iloc[0].to_dict()

    if "player_is_playing" not in st.session_state:
        st.session_state.player_is_playing = True if current_track else False

    # Dock Container
    st.markdown(
        """
        <div class="player-dock-spacer"></div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown(
            """
            <div class="player-dock-container">
            """,
            unsafe_allow_html=True,
        )

        if current_track:
            sid = str(current_track.get("song_id", ""))
            sname = str(current_track.get("song_name", "Unknown Track"))
            artist = str(current_track.get("artist", "Unknown Artist"))
            genre = str(current_track.get("genre", "Music"))
            is_fav = is_liked(user_id, sid)
            heart_icon = "❤️" if is_fav else "🤍"
            play_icon = "⏸️" if st.session_state.player_is_playing else "▶️"

            # 3-column layout: Left (Track Info), Center (Controls), Right (Actions/Status)
            p_col1, p_col2, p_col3 = st.columns([1.2, 2, 1.2])

            with p_col1:
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div class="player-vinyl-art">
                            <span style="font-size: 1.2rem;">🎵</span>
                        </div>
                        <div style="overflow: hidden;">
                            <div class="player-song-name">{sname}</div>
                            <div class="player-song-artist">{artist} • <span style="color:#a78bfa;">{genre}</span></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with p_col2:
                # Playback Controls
                c_prev, c_play, c_next = st.columns([1, 1.2, 1])
                with c_prev:
                    if st.button("⏮️", key="player_prev_btn", help="Previous Track", use_container_width=True):
                        # Pick previous track from library if available
                        if df is not None and not df.empty:
                            curr_idx = df[df["song_id"].astype(str) == sid].index
                            if len(curr_idx) > 0 and curr_idx[0] > 0:
                                prev_track = df.iloc[curr_idx[0] - 1].to_dict()
                                st.session_state.current_playing_track = prev_track
                                log_play_action(user_id, prev_track["song_id"])
                                st.rerun()

                with c_play:
                    if st.button(play_icon, key="player_toggle_btn", help="Play / Pause", use_container_width=True):
                        st.session_state.player_is_playing = not st.session_state.player_is_playing
                        st.rerun()

                with c_next:
                    if st.button("⏭️", key="player_next_btn", help="Next Track", use_container_width=True):
                        # Pick next track from library if available
                        if df is not None and not df.empty:
                            curr_idx = df[df["song_id"].astype(str) == sid].index
                            if len(curr_idx) > 0 and curr_idx[0] < len(df) - 1:
                                next_track = df.iloc[curr_idx[0] + 1].to_dict()
                                st.session_state.current_playing_track = next_track
                                log_play_action(user_id, next_track["song_id"])
                                st.rerun()

                # Progress Track timeline
                st.markdown(
                    """
                    <div style="display: flex; align-items: center; gap: 8px; margin-top: 2px;">
                        <span style="font-size: 0.72rem; color: #64748b;">0:42</span>
                        <div class="player-progress-bar">
                            <div class="player-progress-fill" style="width: 35%;"></div>
                        </div>
                        <span style="font-size: 0.72rem; color: #64748b;">3:28</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with p_col3:
                r1, r2, r3 = st.columns([1, 1.8, 1])
                with r1:
                    if st.button(heart_icon, key=f"player_fav_{sid}", help="Favorite Track", use_container_width=True):
                        status = toggle_song_favorite(user_id, sid)
                        msg = "Added to Favorites" if status else "Removed from Favorites"
                        st.toast(f"{msg}: {sname}")
                        st.rerun()
                with r2:
                    st.markdown(
                        """
                        <div class="player-mode-pill" title="Preview Mode">
                            ⚡ Catalog Stream
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with r3:
                    if st.button("✕", key="player_close_btn", help="Close Player", use_container_width=True):
                        st.session_state.current_playing_track = None
                        st.session_state.player_is_playing = False
                        st.rerun()
        else:
            # Idle empty player dock
            st.markdown(
                """
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 4px 10px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 1.1rem; color: #818cf8;">🎧</span>
                        <span style="font-size: 0.88rem; color: #94a3b8; font-weight: 500;">
                            No track playing • Click <strong style="color:#f8fafc;">▶ Play</strong> on any song to start listening.
                        </span>
                    </div>
                    <div class="player-mode-pill">Ready to Stream</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            </div>
            """,
            unsafe_allow_html=True,
        )

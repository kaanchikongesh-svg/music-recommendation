"""Listening history page view rendering chronological user interactions with clear history support."""

import streamlit as st

from backend.data.validator import ValidationResult
from backend.services.history_service import (
    clear_listening_history,
    get_user_timeline_history,
    log_play_action,
)
from frontend.components import render_topbar
from frontend.empty_states import render_no_history_state


def render_history_page(result: ValidationResult, user_id: int) -> None:
    """Renders the chronological listening history timeline with playback and clear actions."""
    user = st.session_state.get("user", {"username": "Music Lover"})
    render_topbar(
        greeting="Listening History 📜",
        subtitle="Track and manage your listening activity across the platform.",
        username=user.get("username", "Music Lover"),
    )

    df = result.df if result.is_valid else None
    history = get_user_timeline_history(user_id=user_id, limit=50, df=df)

    if not history:
        render_no_history_state()
        return

    # Header with count and Clear History button
    h_col1, h_col2 = st.columns([3, 1])
    with h_col1:
        st.markdown(f"**Recent Interactions ({len(history)})**")
    with h_col2:
        if st.button("🗑️ Clear History", key="clear_hist_btn", type="secondary", use_container_width=True):
            clear_listening_history(user_id=user_id)
            st.toast("Listening history cleared.")
            st.rerun()

    for item in history:
        sid = item["song_id"]
        action = item["action"]
        played_at = item["played_at"]
        song_name = item.get("song_name", f"Track {sid}")
        artist = item.get("artist", "Unknown Artist")
        genre = item.get("genre", "Music")

        action_badge = (
            "▶️ Played"
            if action == "PLAY"
            else ("❤️ Liked" if action == "LIKE" else "👎 Disliked")
        )

        st.markdown(
            f"""
            <div class="song-card-cinematic" style="margin-bottom: 10px; padding: 14px 18px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="display:flex; align-items:center; gap: 12px;">
                        <span style="font-size: 1.25rem;">🎵</span>
                        <div>
                            <div class="song-title-text">{song_name}</div>
                            <div class="song-artist-text">{artist} • <span class="badge-pill">{genre}</span></div>
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <span class="badge-pill">{action_badge}</span>
                        <div style="font-size:0.75rem; color:#64748b; margin-top:4px;">{played_at}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

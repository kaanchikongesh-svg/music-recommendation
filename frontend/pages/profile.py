"""User profile page view displaying personal metrics, tastes, and listening analytics."""

import streamlit as st

from backend.data.validator import ValidationResult
from backend.services.user_service import get_user_profile_analytics
from frontend.components import render_topbar


def render_profile_page(result: ValidationResult, user_id: int) -> None:
    """Renders user profile statistics derived from actual database records and catalog matching."""
    user = st.session_state.get("user", {"username": "Music Lover", "email": "user@musicrecommender.local"})
    username = user.get("username", "Music Lover")
    initial = (username[0] if username else "U").upper()

    render_topbar(
        greeting="Profile & Insights 👤",
        subtitle="Your listening metrics, activity history, and taste breakdown.",
        username=username,
    )

    df = result.df if result.is_valid else None
    analytics = get_user_profile_analytics(user_id=user_id, df=df)

    st.markdown(
        f"""
        <div class="user-profile-header">
            <div style="display: flex; align-items: center; gap: 16px;">
                <div class="user-avatar-circle" style="width: 54px; height: 54px; font-size: 1.4rem;">
                    {initial}
                </div>
                <div>
                    <div style="font-size:1.6rem; font-weight:800; color:#f8fafc; letter-spacing: -0.02em;">{username}</div>
                    <div style="color:#a78bfa; font-size:0.92rem; margin-top:2px;">{user.get('email') or 'Personal Account'}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Activity Statistics
    st.subheader("📊 Activity Summary")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-number">{analytics["total_plays"]}</div><div class="metric-label">Songs Played</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-number">{analytics["total_likes"]}</div><div class="metric-label">Favorites / Likes</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="metric-card"><div class="metric-number">{analytics["total_playlists"]}</div><div class="metric-label">Playlists Created</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Taste Analytics
    st.subheader("🎧 Music Taste Insights")
    st.caption("Calculated dynamically from your actual listening history and favorited tracks.")
    t1, t2 = st.columns(2)
    with t1:
        st.markdown(
            f"""
            <div class="song-card-cinematic" style="padding: 22px;">
                <div class="metric-label" style="margin-bottom:8px;">Top Interacted Genre</div>
                <div style="font-size:1.45rem; font-weight:800; color:#a5b4fc;">
                    🎸 {analytics["favorite_genre"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with t2:
        st.markdown(
            f"""
            <div class="song-card-cinematic" style="padding: 22px;">
                <div class="metric-label" style="margin-bottom:8px;">Top Interacted Artist</div>
                <div style="font-size:1.45rem; font-weight:800; color:#c084fc;">
                    🎤 {analytics["favorite_artist"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

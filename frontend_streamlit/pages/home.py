"""Home page view featuring topbar greeting, search, hero banner, genre chips, and track feeds."""

import streamlit as st

from backend.data.loader import (
    DEFAULT_RAW_DATA_PATH,
    get_dataset_statistics,
)
from backend.data.validator import (
    OPTIONAL_AUDIO_FEATURES,
    REQUIRED_COLUMNS,
    ValidationResult,
)
from backend.recommendation.engine import get_personalized_recommendations
from backend.services.history_service import get_user_timeline_history
from backend.services.music_service import get_featured_tracks, get_top_genres
from frontend_streamlit.cards import (
    render_recommendation_card,
    render_song_card,
    render_song_details_section,
)
from frontend_streamlit.components import (
    render_dataset_upload_widget,
    render_hero,
    render_metrics_grid,
    render_topbar,
)
from frontend_streamlit.empty_states import render_empty_state, render_no_dataset_state


def render_home_page(result: ValidationResult, user_id: int) -> None:
    """Renders the dark-cinematic Home dashboard view."""
    user = st.session_state.get("user", {"username": "Music Lover"})
    username = user.get("username", "Music Lover")

    # 1. Top Greeting Bar
    render_topbar(
        subtitle="Discover music that matches your taste.",
        username=username,
    )

    # 2. Global Search Bar on Home
    search_col1, search_col2 = st.columns([4, 1])
    with search_col1:
        home_query = st.text_input(
            "Search Catalog",
            placeholder="🔍 Search songs, artists, albums or genres...",
            label_visibility="collapsed",
            key="home_global_search_input",
        )
    with search_col2:
        if st.button("Search 🔍", key="home_search_submit_btn", use_container_width=True, type="primary"):
            if home_query.strip():
                st.session_state.search_query = home_query.strip()
                st.session_state.active_tab = "🔎 Discover"
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Check dataset availability
    if not result.is_valid or result.df is None:
        render_no_dataset_state(expected_path=DEFAULT_RAW_DATA_PATH)

        with st.expander("📋 View Dataset Requirements & Schema", expanded=False):
            st.markdown("Your CSV must contain the following mandatory columns:")
            for col in REQUIRED_COLUMNS:
                st.markdown(f"- **`{col}`**")
            st.markdown("Optional audio features automatically supported:")
            for col in OPTIONAL_AUDIO_FEATURES:
                st.markdown(f"- `{col}`")

        render_dataset_upload_widget(result)

        if st.button("🔄 Refresh Library", key="home_refresh_btn"):
            st.cache_data.clear()
            st.rerun()
        return

    df = result.df
    stats = get_dataset_statistics(df)

    # 4. Cinematic Hero Banner
    render_hero(
        title="Your sound. Your mood. Your discovery.",
        subtitle="Personalized recommendations powered by your listening preferences.",
    )

    # 5. Metrics Grid
    render_metrics_grid(stats)

    st.markdown("<br>", unsafe_allow_html=True)

    # 6. Quick Genre Mood Section
    top_genres = get_top_genres(limit=8, df=df)
    if top_genres:
        st.subheader("🎧 Explore by mood")
        st.caption("Click any mood/genre to filter the entire catalog.")
        g_cols = st.columns(len(top_genres))
        for idx, g in enumerate(top_genres):
            with g_cols[idx]:
                if st.button(f"🎵 {g}", key=f"home_genre_chip_{idx}", use_container_width=True):
                    st.session_state.genre_filter = g
                    st.session_state.active_tab = "🔎 Discover"
                    st.rerun()

    # 7. Active Selected Song Details (if clicked)
    if st.session_state.get("selected_song_id"):
        matched = df[df["song_id"].astype(str) == str(st.session_state.selected_song_id)]
        if not matched.empty:
            render_song_details_section(
                song=matched.iloc[0],
                detected_audio_features=result.detected_audio_features,
                user_id=user_id,
            )

    st.markdown("---")

    # 8. Recommended For You (Powered by Real ML)
    st.subheader("✨ Recommended for you")
    st.caption("Picked based on your music taste & preferences")
    personal_recs = get_personalized_recommendations(user_id=user_id, df=df, n_recommendations=6)
    if personal_recs:
        rec_cols = st.columns(3)
        for idx, rec_item in enumerate(personal_recs):
            with rec_cols[idx % 3]:
                render_recommendation_card(rec_item, user_id=user_id, key_prefix=f"home_rec_{idx}")
    else:
        st.info("Start listening to tracks to unlock personalized algorithmic recommendations.")

    st.markdown("---")

    # 9. Popular Right Now / Featured Tracks
    st.subheader("🔥 Popular right now")
    st.caption("Trending tracks across the music catalog")
    featured_df = get_featured_tracks(limit=6, df=df)
    f_cols = st.columns(3)
    for idx, (_, row) in enumerate(featured_df.iterrows()):
        with f_cols[idx % 3]:
            render_song_card(row, user_id=user_id, key_prefix=f"home_feat_{idx}")

    st.markdown("---")

    # 10. Recently Played
    st.subheader("⏳ Recently played")
    recent_history = get_user_timeline_history(user_id=user_id, limit=4, df=df)
    if recent_history:
        for item in recent_history:
            st.markdown(
                f"""
                <div class="song-card-cinematic" style="min-height: auto; padding: 12px 18px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <span style="font-size: 1.2rem;">🎵</span>
                            <div>
                                <span style="font-weight: 700; color: #f8fafc;">{item['song_name']}</span>
                                <span style="color: #94a3b8; font-size: 0.88rem;"> • {item['artist']}</span>
                                <span class="badge-pill" style="margin-left: 8px;">{item['genre']}</span>
                            </div>
                        </div>
                        <div style="font-size: 0.75rem; color: #64748b;">
                            <span class="badge-pill">{item['action']}</span> {item['played_at']}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        render_empty_state(
            icon="📜",
            title="No listening history yet",
            message="Start exploring music and your recently played songs will appear here.",
        )
        if st.button("🚀 Discover Music", key="home_no_hist_disc_btn", type="primary"):
            st.session_state.active_tab = "🔎 Discover"
            st.rerun()

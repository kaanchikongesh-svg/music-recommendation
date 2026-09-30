"""Dedicated Recommendations page providing categorized ML recommendation feeds."""

import streamlit as st

from backend.data.loader import DEFAULT_RAW_DATA_PATH
from backend.data.validator import ValidationResult
from backend.recommendation.engine import (
    get_personalized_recommendations,
    recommend_songs,
)
from backend.services.history_service import (
    get_user_favorite_tracks,
    get_user_timeline_history,
)
from frontend_streamlit.cards import (
    render_recommendation_card,
    render_song_details_section,
)
from frontend_streamlit.components import render_dataset_upload_widget, render_topbar
from frontend_streamlit.empty_states import (
    render_no_dataset_state,
    render_no_recommendations_state,
)


def render_recommendations_page(result: ValidationResult, user_id: int) -> None:
    """Renders the AI recommendation hub with contextual ML feeds."""
    user = st.session_state.get("user", {"username": "Music Lover"})
    render_topbar(
        greeting="Your Recommendations ✨",
        subtitle="Algorithmic music discovery powered by Content-Based Filtering & Audio Vector Blending.",
        username=user.get("username", "Music Lover"),
    )

    if not result.is_valid or result.df is None:
        render_no_dataset_state(expected_path=DEFAULT_RAW_DATA_PATH)
        render_dataset_upload_widget(result)
        return

    df = result.df

    # Selected Song Spotlight Details
    if st.session_state.get("selected_song_id"):
        matched = df[df["song_id"].astype(str) == str(st.session_state.selected_song_id)]
        if not matched.empty:
            render_song_details_section(
                song=matched.iloc[0],
                detected_audio_features=result.detected_audio_features,
                user_id=user_id,
            )

    rec_tab1, rec_tab2 = st.tabs(["🎧 Personalized Taste Feed", "🎯 Seed Track Explorer"])

    with rec_tab1:
        # 1. Feed: Based on Recent Listening History
        recent_history = get_user_timeline_history(user_id=user_id, limit=1, df=df)
        if recent_history:
            seed_song = recent_history[0]
            st.subheader(f"Because you listened to '{seed_song['song_name']}'")
            st.caption(f"Similar tracks matching {seed_song['artist']} ({seed_song['genre']})")

            recent_seed_recs = recommend_songs(seed_song["song_id"], df=df, n_recommendations=3)
            if recent_seed_recs:
                s_cols = st.columns(3)
                for idx, rec_item in enumerate(recent_seed_recs):
                    with s_cols[idx % 3]:
                        render_recommendation_card(rec_item, user_id=user_id, key_prefix=f"recent_seed_rec_{idx}")

            st.markdown("---")

        # 2. Feed: Overall Personalized Recommendations
        st.subheader("Picked for your music profile")
        st.caption("Constructed from your overall favorite and interaction centroid vectors.")

        personal_recs = get_personalized_recommendations(user_id=user_id, df=df, n_recommendations=6)
        if personal_recs:
            p_cols = st.columns(3)
            for idx, rec_item in enumerate(personal_recs):
                with p_cols[idx % 3]:
                    render_recommendation_card(rec_item, user_id=user_id, key_prefix=f"pers_feed_rec_{idx}")
        else:
            render_no_recommendations_state()

    with rec_tab2:
        st.subheader("🎯 Interactive Seed Track Recommender")
        st.caption("Select any track to discover acoustic and lyrical sister tracks.")

        song_options = {}
        for _, row in df.iterrows():
            label = f"{row['song_name']} — {row['artist']} [{row.get('genre', 'Music')}]"
            song_options[label] = str(row["song_id"])

        selected_label = st.selectbox(
            "Select Track from Catalog",
            list(song_options.keys()),
            key="rec_seed_dropdown",
        )

        n_count = st.slider("Recommendations count", min_value=3, max_value=18, value=6, step=3)

        if st.button("✨ Compute Similar Tracks", key="compute_rec_btn", type="primary"):
            target_song_id = song_options[selected_label]
            with st.spinner("Analyzing TF-IDF vectors & audio acoustic profiles..."):
                recs = recommend_songs(target_song_id, df=df, n_recommendations=n_count)
                if recs:
                    st.success(f"Discovered {len(recs)} highly similar tracks!")
                    rec_cols = st.columns(3)
                    for idx, rec_item in enumerate(recs):
                        with rec_cols[idx % 3]:
                            render_recommendation_card(
                                rec_item, user_id=user_id, key_prefix=f"interactive_rec_{idx}"
                            )
                else:
                    render_no_recommendations_state()

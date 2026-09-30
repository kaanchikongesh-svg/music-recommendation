"""Discover page view for searching, multi-factor filtering, and exploring catalog tracks."""

import streamlit as st

from backend.data.loader import (
    DEFAULT_RAW_DATA_PATH,
    get_dataset_statistics,
)
from backend.data.validator import ValidationResult
from backend.services.music_service import search_and_filter_tracks
from frontend_streamlit.cards import render_song_card, render_song_details_section
from frontend_streamlit.components import render_dataset_upload_widget, render_topbar
from frontend_streamlit.empty_states import (
    render_no_dataset_state,
    render_no_search_results_state,
)


def render_discover_page(result: ValidationResult, user_id: int) -> None:
    """Renders the comprehensive Discover page with interactive search and filters."""
    user = st.session_state.get("user", {"username": "Music Lover"})
    render_topbar(
        greeting="Discover 🔎",
        subtitle="Explore songs, albums, and genres across your library.",
        username=user.get("username", "Music Lover"),
    )

    if not result.is_valid or result.df is None:
        render_no_dataset_state(expected_path=DEFAULT_RAW_DATA_PATH)
        render_dataset_upload_widget(result)
        return

    df = result.df
    stats = get_dataset_statistics(df)

    # 1. Search Box
    initial_search = st.session_state.get("search_query", "")
    search_query = st.text_input(
        "Search Catalog",
        value=initial_search,
        placeholder="🔍 Search track title, artist, or album...",
        key="disc_search_input",
        label_visibility="collapsed",
    )

    # 2. Multi-Filter Controls (Genre, Language, Artist, Album, Year)
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        default_genre = st.session_state.get("genre_filter", "All")
        genre_options = ["All"] + stats["genres_list"]
        genre_idx = genre_options.index(default_genre) if default_genre in genre_options else 0
        selected_genre = st.selectbox("Genre / Mood", genre_options, index=genre_idx, key="disc_sel_genre")

    with f2:
        selected_artist = st.selectbox(
            "Artist", ["All"] + stats["artists_list"], key="disc_sel_artist"
        )

    with f3:
        selected_lang = st.selectbox(
            "Language", ["All"] + stats["languages_list"], key="disc_sel_lang"
        )

    with f4:
        min_y, max_y = stats["years_range"]
        if min_y < max_y:
            selected_years = st.slider(
                "Release Year",
                min_value=min_y,
                max_value=max_y,
                value=(min_y, max_y),
                key="disc_sel_year",
            )
        else:
            selected_years = (min_y, max_y)

    # 3. Filter Execution
    filtered_df = search_and_filter_tracks(
        search_query=search_query,
        artist=selected_artist,
        genre=selected_genre,
        language=selected_lang,
        year_range=selected_years,
        df=df,
    )

    # Result Header & Reset Button
    hdr_c1, hdr_c2 = st.columns([4, 1])
    with hdr_c1:
        st.markdown(f"**Showing {len(filtered_df):,} matching tracks**")
    with hdr_c2:
        if st.button("Reset Filters", key="disc_reset_filters_btn", use_container_width=True):
            st.session_state.search_query = ""
            st.session_state.genre_filter = "All"
            st.rerun()

    # 4. Selected Song Expanded Spotlight Details
    if st.session_state.get("selected_song_id"):
        matched = df[df["song_id"].astype(str) == str(st.session_state.selected_song_id)]
        if not matched.empty:
            render_song_details_section(
                song=matched.iloc[0],
                detected_audio_features=result.detected_audio_features,
                user_id=user_id,
            )

    # 5. Empty Results Check
    if filtered_df.empty:
        render_no_search_results_state()
        return

    # 6. Grid of Song Cards
    display_subset = filtered_df.head(24)
    grid_cols = st.columns(3)

    for idx, (_, row) in enumerate(display_subset.iterrows()):
        with grid_cols[idx % 3]:
            render_song_card(row, user_id=user_id, key_prefix=f"disc_card_{idx}")

"""Reusable presentation components for topbar, hero banners, metric cards, and charts."""

from datetime import datetime
from typing import Any, Dict, List, Optional
import plotly.graph_objects as go
import streamlit as st

from backend.data.loader import save_uploaded_dataset
from backend.data.validator import (
    OPTIONAL_AUDIO_FEATURES,
    REQUIRED_COLUMNS,
    ValidationResult,
)


def get_time_greeting() -> str:
    """Calculates time-of-day greeting (e.g., 'Good morning', 'Good afternoon', 'Good evening')."""
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning ☀️"
    elif 12 <= hour < 18:
        return "Good afternoon 🌤️"
    else:
        return "Good evening 🌙"


def render_topbar(
    greeting: Optional[str] = None,
    subtitle: str = "Discover music that matches your taste.",
    username: str = "Music Lover",
) -> None:
    """Renders the top greeting bar with user status and shortcuts."""
    g = greeting or get_time_greeting()
    initial = (username[0] if username else "U").upper()

    col_left, col_right = st.columns([3, 1])

    with col_left:
        st.markdown(
            f"""
            <div>
                <div class="topbar-greeting">{g}</div>
                <div class="topbar-sub">{subtitle}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: flex-end; align-items: center; gap: 12px; height: 100%;">
                <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 1rem; color: #94a3b8;">
                    🔔
                </div>
                <div class="user-avatar-circle" style="width: 36px; height: 36px; font-size: 0.9rem;">
                    {initial}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_hero(
    title: str = "Your sound. Your mood. Your discovery.",
    subtitle: str = "Personalized recommendations powered by your listening preferences.",
) -> None:
    """Renders the cinematic hero section with working action buttons."""
    st.markdown(
        f"""
        <div class="hero-cinematic">
            <div class="hero-cinematic-title">{title}</div>
            <div class="hero-cinematic-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    btn_col1, btn_col2, _ = st.columns([1.2, 1.4, 2])
    with btn_col1:
        if st.button("🚀 Discover Music", key="hero_disc_btn", type="primary", use_container_width=True):
            st.session_state.active_tab = "🔎 Discover"
            st.rerun()
    with btn_col2:
        if st.button("✨ Explore Recommendations", key="hero_rec_btn", use_container_width=True):
            st.session_state.active_tab = "✨ Recommendations"
            st.rerun()


def render_metrics_grid(stats: Dict[str, Any]) -> None:
    """Renders the 5-column metric statistics cards for catalog metadata."""
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-number">{stats.get("total_songs", 0):,}</div><div class="metric-label">Songs</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-number">{stats.get("total_artists", 0):,}</div><div class="metric-label">Artists</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="metric-card"><div class="metric-number">{stats.get("total_albums", 0):,}</div><div class="metric-label">Albums</div></div>',
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f'<div class="metric-card"><div class="metric-number">{stats.get("total_genres", 0):,}</div><div class="metric-label">Genres</div></div>',
            unsafe_allow_html=True,
        )
    with c5:
        st.markdown(
            f'<div class="metric-card"><div class="metric-number">{stats.get("total_languages", 0):,}</div><div class="metric-label">Languages</div></div>',
            unsafe_allow_html=True,
        )


def render_audio_radar_chart(
    song_dict: Dict[str, Any], detected_features: List[str]
) -> Optional[go.Figure]:
    """Generates a sleek Plotly polar radar chart for song audio features."""
    normalized_features = [
        f
        for f in detected_features
        if f
        in [
            "danceability",
            "energy",
            "valence",
            "acousticness",
            "instrumentalness",
            "speechiness",
        ]
    ]

    if not normalized_features:
        return None

    values = []
    categories = []
    for f in normalized_features:
        try:
            val = float(song_dict.get(f, 0))
            values.append(val)
            categories.append(f.capitalize())
        except (ValueError, TypeError):
            continue

    if not values:
        return None

    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill="toself",
            fillcolor="rgba(168, 85, 247, 0.28)",
            line=dict(color="#c084fc", width=2.5),
            name="Audio Profile",
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                showticklabels=False,
                linecolor="rgba(255, 255, 255, 0.1)",
                gridcolor="rgba(255, 255, 255, 0.1)",
            ),
            angularaxis=dict(
                color="#94a3b8",
                linecolor="rgba(255, 255, 255, 0.1)",
                gridcolor="rgba(255, 255, 255, 0.1)",
            ),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=30, t=20, b=20),
        height=280,
        showlegend=False,
    )
    return fig


def render_dataset_upload_widget(result: ValidationResult) -> None:
    """Renders the CSV uploader widget with auto-adapting support."""
    with st.expander("📥 Import Music Dataset (CSV / Kaggle)", expanded=not result.is_valid):
        st.markdown(
            "Upload a custom music CSV or Kaggle dataset. It will be validated, adapted, and saved to `data/raw/songs.csv`."
        )
        uploaded = st.file_uploader(
            "Choose a CSV file",
            type=["csv"],
            key="shared_dataset_uploader",
            help="Supported columns: song_name, artist, album, genre, language, year, and audio features.",
        )
        if uploaded is not None:
            with st.spinner("Validating and importing dataset..."):
                upload_result = save_uploaded_dataset(uploaded, auto_adapt=True)
                if upload_result.is_valid:
                    st.success("✅ Dataset imported and validated successfully!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("❌ Dataset validation failed:")
                    for err in upload_result.errors:
                        st.markdown(f"- {err}")

"""UI utilities, custom CSS styling, and visualization helpers."""

from typing import Any, Dict, List, Optional
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def inject_custom_css() -> None:
    """Injects custom sleek dark theme styles for the Music Recommendation System."""
    custom_css = """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Container background subtle gradient */
    .stApp {
        background-color: #0d0f12;
        color: #e2e8f0;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #12161c;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }

    /* Hero Header */
    .hero-container {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.12) 50%, rgba(236, 72, 153, 0.08) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        backdrop-filter: blur(12px);
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ffffff, #c7d2fe, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        font-weight: 400;
        margin-bottom: 0;
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.4);
        background: rgba(255, 255, 255, 0.05);
    }

    .metric-number {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 4px;
    }

    .metric-label {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }

    /* Song Card */
    .song-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
    }

    .song-card:hover {
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(168, 85, 247, 0.3);
    }

    .song-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 4px;
    }

    .song-artist {
        font-size: 0.9rem;
        color: #a78bfa;
        font-weight: 500;
        margin-bottom: 6px;
    }

    .song-meta {
        font-size: 0.8rem;
        color: #64748b;
    }

    /* Badge Pills */
    .badge-pill {
        display: inline-block;
        background: rgba(99, 102, 241, 0.15);
        color: #a5b4fc;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
        border: 1px solid rgba(99, 102, 241, 0.25);
    }

    /* Empty State Container */
    .empty-state-box {
        background: rgba(255, 255, 255, 0.02);
        border: 1px dashed rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 40px 24px;
        text-align: center;
        margin: 20px 0;
    }

    .empty-state-icon {
        font-size: 3rem;
        margin-bottom: 12px;
    }

    .empty-state-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 8px;
    }

    .empty-state-desc {
        color: #94a3b8;
        font-size: 0.95rem;
        max-width: 500px;
        margin: 0 auto 16px auto;
        line-height: 1.5;
    }

    /* Genre Card */
    .genre-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px 16px;
        text-align: center;
        font-weight: 600;
        color: #e2e8f0;
        transition: all 0.2s ease;
    }
    .genre-card:hover {
        background: rgba(99, 102, 241, 0.2);
        border-color: rgba(99, 102, 241, 0.5);
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def render_empty_state(
    icon: str,
    title: str,
    message: str,
    expected_path: Optional[str] = None,
) -> None:
    """Renders a styled, professional empty state container."""
    path_html = (
        f"<p style='color:#6366f1; font-family:monospace; margin-top:8px;'>Expected: {expected_path}</p>"
        if expected_path
        else ""
    )

    st.markdown(
        f"""
        <div class="empty-state-box">
            <div class="empty-state-icon">{icon}</div>
            <div class="empty-state-title">{title}</div>
            <div class="empty-state-desc">{message}</div>
            {path_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_audio_features_radar(
    song_dict: Dict[str, Any], detected_features: List[str]
) -> Optional[go.Figure]:
    """Generates a Plotly radar/bar chart for audio features if available."""
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

    # Complete polygon for radar
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill="toself",
            fillcolor="rgba(168, 85, 247, 0.25)",
            line=dict(color="#a855f7", width=2),
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

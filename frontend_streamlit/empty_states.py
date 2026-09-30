"""Reusable styled empty state UI components."""

from pathlib import Path
from typing import Optional, Union
import streamlit as st


def render_empty_state(
    icon: str,
    title: str,
    message: str,
    expected_path: Optional[Union[str, Path]] = None,
) -> None:
    """Renders a styled, modern empty state container."""
    path_html = (
        f"<p style='color:#818cf8; font-family:monospace; margin-top:10px; font-size:0.85rem;'>Location: {expected_path}</p>"
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


def render_no_dataset_state(expected_path: Optional[Union[str, Path]] = None) -> None:
    """Renders empty state when music library dataset is missing."""
    render_empty_state(
        icon="🎵",
        title="Music Library Empty",
        message="Upload or install a music catalog dataset (CSV) to start discovering tracks and generating machine learning recommendations.",
        expected_path=expected_path or "data/raw/songs.csv",
    )


def render_no_favorites_state() -> None:
    """Renders empty state when user has no liked tracks."""
    render_empty_state(
        icon="❤️",
        title="No Favorites Yet",
        message="Songs you like while discovering or playing will appear here for instant playback.",
    )


def render_no_history_state() -> None:
    """Renders empty state when listening history is empty."""
    render_empty_state(
        icon="📜",
        title="No Listening History",
        message="Start exploring and playing songs to build your personalized history timeline.",
    )


def render_no_playlists_state() -> None:
    """Renders empty state when no playlists have been created."""
    render_empty_state(
        icon="📁",
        title="Create Your First Playlist",
        message="Organize your favorite songs by mood, genre, or activity with custom playlists.",
    )


def render_no_recommendations_state() -> None:
    """Renders empty state when no recommendations are available."""
    render_empty_state(
        icon="✨",
        title="Recommendations Will Appear Here",
        message="Select a song to discover similar tracks or play music to unlock personalized suggestions.",
    )


def render_no_search_results_state() -> None:
    """Renders empty state when search/filter returns zero records."""
    render_empty_state(
        icon="🔍",
        title="No Matching Songs Found",
        message="Try adjusting your search query, genre, artist, or release year filters.",
    )

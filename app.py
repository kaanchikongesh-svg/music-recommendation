"""TuneSphere - Music Recommendation System - Main Application Entrypoint."""

import pandas as pd
import streamlit as st

from backend.data.loader import (
    DEFAULT_RAW_DATA_PATH,
    load_dataset,
)
from backend.data.preprocessing import (
    DEFAULT_PROCESSED_DATA_PATH,
    PreprocessingResult,
    preprocess_dataset,
)
from backend.data.validator import (
    OPTIONAL_AUDIO_FEATURES,
    ValidationResult,
)
from backend.database.connection import init_db
from backend.services.user_service import get_default_user
from frontend.components import render_dataset_upload_widget
from frontend.pages.discover import render_discover_page
from frontend.pages.favorites import render_favorites_page
from frontend.pages.history import render_history_page
from frontend.pages.home import render_home_page
from frontend.pages.login import render_login_page
from frontend.pages.playlists import render_playlists_page
from frontend.pages.profile import render_profile_page
from frontend.pages.recommendations import render_recommendations_page
from frontend.player import render_music_player
from frontend.sidebar import render_sidebar
from frontend.theme import inject_custom_css

# Streamlit Page Configuration
st.set_page_config(
    page_title="TuneSphere - AI Music Dashboard",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner="Loading music library...")
def cached_load_dataset(file_path: str = str(DEFAULT_RAW_DATA_PATH)) -> ValidationResult:
    """Loads and validates the music library dataset with caching."""
    return load_dataset(file_path)


@st.cache_data(show_spinner="Preprocessing dataset...")
def cached_preprocess_dataset(df: pd.DataFrame) -> PreprocessingResult:
    """Caches dataset preprocessing and combined feature construction."""
    return preprocess_dataset(df, save_processed=True)


def init_session_state() -> None:
    """Initializes and verifies session state variables."""
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "🏠 Home"
    if "selected_song_id" not in st.session_state:
        st.session_state.selected_song_id = None
    if "current_playing_track" not in st.session_state:
        st.session_state.current_playing_track = None
    if "player_is_playing" not in st.session_state:
        st.session_state.player_is_playing = False
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state or st.session_state.user is None:
        st.session_state.user = get_default_user()
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""


def render_settings_page(result: ValidationResult) -> None:
    """Renders system settings, Kaggle dataset status, and preprocessing pipeline health."""
    st.title("⚙️ System & Dataset Settings")
    st.markdown("Manage dataset sources, Kaggle adapters, and cache indices.")

    st.subheader("📁 Dataset Status")
    if result.is_valid and result.df is not None:
        st.success(f"✅ Active Raw Dataset: `{DEFAULT_RAW_DATA_PATH}` ({result.total_songs:,} songs)")

        prep = cached_preprocess_dataset(result.df)
        if prep.is_success:
            st.markdown("#### ⚡ Preprocessing Pipeline Status")
            p1, p2, p3 = st.columns(3)
            with p1:
                st.metric("Raw Tracks", f"{prep.report.original_rows:,}")
            with p2:
                st.metric("Processed Tracks", f"{prep.report.final_rows:,}")
            with p3:
                st.metric("Duplicates Removed", f"{prep.report.duplicates_removed:,}")

            st.caption(f"Processed dataset saved to: `{DEFAULT_PROCESSED_DATA_PATH}`")

            st.markdown("#### 🎧 Audio Features Support")
            af_cols = st.columns(3)
            for idx, feat in enumerate(OPTIONAL_AUDIO_FEATURES):
                with af_cols[idx % 3]:
                    if feat in prep.report.available_audio_features:
                        st.markdown(f"✅ **`{feat}`** *(Detected)*")
                    else:
                        st.markdown(f"❌ `{feat}` *(Not present)*")
    else:
        st.warning(f"⚠️ Dataset currently unavailable at `{DEFAULT_RAW_DATA_PATH}`.")

    render_dataset_upload_widget(result)

    st.markdown("---")
    st.subheader("🔄 Cache Management")
    if st.button("Clear Cache & Reload Catalog", key="clear_cache_btn"):
        st.cache_data.clear()
        st.success("Cache cleared successfully!")
        st.rerun()


def main() -> None:
    """Main application execution flow."""
    inject_custom_css()
    init_db()
    init_session_state()

    user = st.session_state.user or get_default_user()
    user_id = user["id"]
    username = user.get("username", "Music Lover")
    is_authenticated = st.session_state.get("authenticated", False)

    # Render Sidebar navigation
    selected_nav = render_sidebar(is_authenticated=is_authenticated, username=username)
    if st.session_state.active_tab != "⚙️ Settings" and st.session_state.active_tab != "🔐 Login":
        st.session_state.active_tab = selected_nav

    result = cached_load_dataset()
    tab = st.session_state.active_tab

    # View Router
    if tab == "🏠 Home":
        render_home_page(result, user_id=user_id)
    elif tab == "🔎 Discover":
        render_discover_page(result, user_id=user_id)
    elif tab == "✨ Recommendations":
        render_recommendations_page(result, user_id=user_id)
    elif tab == "❤️ Favorites":
        render_favorites_page(result, user_id=user_id)
    elif tab == "📜 History":
        render_history_page(result, user_id=user_id)
    elif tab == "🎵 Playlists":
        render_playlists_page(result, user_id=user_id)
    elif tab == "👤 Profile":
        render_profile_page(result, user_id=user_id)
    elif tab == "⚙️ Settings":
        render_settings_page(result)
    elif tab == "🔐 Login":
        render_login_page()

    # Render Persistent Mini Music Player at the bottom across all views
    render_music_player(user_id=user_id, df=result.df if result.is_valid else None)


if __name__ == "__main__":
    main()

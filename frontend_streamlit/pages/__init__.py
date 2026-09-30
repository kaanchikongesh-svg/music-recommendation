"""Frontend page views package."""

from frontend_streamlit.pages.discover import render_discover_page
from frontend_streamlit.pages.favorites import render_favorites_page
from frontend_streamlit.pages.history import render_history_page
from frontend_streamlit.pages.home import render_home_page
from frontend_streamlit.pages.login import render_login_page
from frontend_streamlit.pages.playlists import render_playlists_page
from frontend_streamlit.pages.profile import render_profile_page
from frontend_streamlit.pages.recommendations import render_recommendations_page

__all__ = [
    "render_home_page",
    "render_discover_page",
    "render_recommendations_page",
    "render_favorites_page",
    "render_history_page",
    "render_playlists_page",
    "render_profile_page",
    "render_login_page",
]

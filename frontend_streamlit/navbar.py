"""Top navigation header bar and breadcrumbs utility."""

from typing import Optional
import streamlit as st


def render_navbar(active_page_title: str, user_info: Optional[dict] = None) -> None:
    """Renders a top navigation bar with page title and active user state."""
    username = user_info.get("username", "Guest") if user_info else "Guest"
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.06);">
            <div style="font-size: 1.1rem; font-weight: 700; color: #f8fafc;">
                {active_page_title}
            </div>
            <div style="font-size: 0.85rem; color: #94a3b8;">
                User: <span style="color: #a78bfa; font-weight: 600;">{username}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

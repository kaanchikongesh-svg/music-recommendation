"""Sidebar navigation and session status rendering for TuneSphere."""

from typing import Optional
import streamlit as st


def render_sidebar(is_authenticated: bool = False, username: str = "Music Lover") -> str:
    """Renders the dark cinematic TuneSphere sidebar and returns the selected navigation view."""
    with st.sidebar:
        # App Logo & Branding
        st.markdown(
            """
            <div style="padding: 10px 4px 18px 4px; display: flex; align-items: center; gap: 10px;">
                <div style="width: 38px; height: 38px; border-radius: 10px; background: linear-gradient(135deg, #6366f1, #a855f7); display: flex; align-items: center; justify-content: center; font-size: 1.25rem; box-shadow: 0 0 14px rgba(168, 85, 247, 0.4);">
                    🎵
                </div>
                <div>
                    <div style="font-size: 1.35rem; font-weight: 800; color: #f8fafc; letter-spacing: -0.02em; line-height: 1.1;">TuneSphere</div>
                    <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 500;">AI Music Discovery</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-section-title">Main</div>', unsafe_allow_html=True)

        nav_options = [
            "🏠 Home",
            "🔎 Discover",
            "✨ Recommendations",
            "❤️ Favorites",
            "📜 History",
            "🎵 Playlists",
        ]

        current_tab = st.session_state.get("active_tab", "🏠 Home")
        default_index = nav_options.index(current_tab) if current_tab in nav_options else 0

        selected_nav = st.radio(
            "Main Navigation",
            nav_options,
            index=default_index,
            label_visibility="collapsed",
        )

        st.markdown('<div class="sidebar-section-title">Library</div>', unsafe_allow_html=True)
        col_lib1, col_lib2 = st.columns(2)
        with col_lib1:
            if st.button("📁 Library", key="sb_lib_btn", use_container_width=True):
                st.session_state.active_tab = "🔎 Discover"
                st.rerun()
        with col_lib2:
            if st.button("⏳ Recent", key="sb_rec_btn", use_container_width=True):
                st.session_state.active_tab = "📜 History"
                st.rerun()

        st.markdown('<div class="sidebar-section-title">Account</div>', unsafe_allow_html=True)

        col_acc1, col_acc2 = st.columns(2)
        with col_acc1:
            if st.button("👤 Profile", key="sb_prof_btn", use_container_width=True):
                st.session_state.active_tab = "👤 Profile"
                st.rerun()
        with col_acc2:
            if st.button("⚙️ Settings", key="sb_sett_btn", use_container_width=True):
                st.session_state.active_tab = "⚙️ Settings"
                st.rerun()

        if is_authenticated:
            if st.button("🚪 Logout", key="sb_logout_btn", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.session_state.active_tab = "🔐 Login"
                st.rerun()
        else:
            if st.button("🔐 Sign In", key="sb_login_btn", use_container_width=True, type="primary"):
                st.session_state.active_tab = "🔐 Login"
                st.rerun()

        st.markdown("---")

        # Bottom User Status Card
        initial = (username[0] if username else "U").upper()
        status_dot = "🟢" if is_authenticated else "⚪"
        status_label = "Active Account" if is_authenticated else "Guest Session"

        st.markdown(
            f"""
            <div class="sidebar-user-card">
                <div class="user-avatar-circle">{initial}</div>
                <div style="overflow: hidden;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #f8fafc; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        {username}
                    </div>
                    <div style="font-size: 0.72rem; color: #94a3b8;">
                        {status_dot} {status_label}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return selected_nav

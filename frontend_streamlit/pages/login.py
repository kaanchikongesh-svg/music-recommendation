"""Authentication page providing dark-cinematic login, registration, and session management."""

import streamlit as st

from backend.auth.authentication import authenticate_user, register_user


def render_login_page() -> None:
    """Renders the centered glassmorphic login and user registration card."""
    st.markdown(
        """
        <div style="text-align: center; margin-top: 20px; margin-bottom: 24px;">
            <div style="width: 52px; height: 52px; border-radius: 14px; background: linear-gradient(135deg, #6366f1, #a855f7); display: inline-flex; align-items: center; justify-content: center; font-size: 1.6rem; box-shadow: 0 0 20px rgba(168, 85, 247, 0.45); margin-bottom: 12px;">
                🎵
            </div>
            <div style="font-size: 1.8rem; font-weight: 900; color: #f8fafc; letter-spacing: -0.03em;">TuneSphere</div>
            <div style="font-size: 0.92rem; color: #94a3b8;">Your Personalized AI Music Dashboard</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_wrap1, col_center, col_wrap2 = st.columns([1, 2, 1])

    with col_center:
        st.markdown('<div class="login-glass-card">', unsafe_allow_html=True)
        tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                st.subheader("Welcome Back")
                st.caption("Sign in to access your recommendations, playlists, and history.")
                username = st.text_input("Username", key="login_username_input", placeholder="Enter your username")
                password = st.text_input("Password", type="password", key="login_pw_input", placeholder="••••••••")
                submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)

                if submitted:
                    if not username.strip() or not password:
                        st.error("Please provide both username and password.")
                    else:
                        success, msg, user_data = authenticate_user(username=username, password=password)
                        if success and user_data:
                            st.session_state.authenticated = True
                            st.session_state.user = user_data
                            st.session_state.active_tab = "🏠 Home"
                            st.success(f"Welcome back, {user_data['username']}!")
                            st.rerun()
                        else:
                            st.error(msg or "Invalid username or password.")

        with tab_register:
            with st.form("register_form", clear_on_submit=True):
                st.subheader("Join TuneSphere")
                st.caption("Create a free profile to unlock personalized AI recommendations.")
                new_username = st.text_input("Choose Username", key="reg_username_input", placeholder="e.g., AudioPhile")
                new_email = st.text_input("Email (Optional)", key="reg_email_input", placeholder="e.g., user@example.com")
                new_pw = st.text_input("Password", type="password", key="reg_pw_input", placeholder="Minimum 4 characters")
                new_pw_confirm = st.text_input("Confirm Password", type="password", key="reg_pw_confirm_input", placeholder="Re-enter password")
                reg_submitted = st.form_submit_button("Create Free Account", type="primary", use_container_width=True)

                if reg_submitted:
                    if new_pw != new_pw_confirm:
                        st.error("Passwords do not match.")
                    else:
                        success, msg, user_data = register_user(
                            username=new_username,
                            password=new_pw,
                            email=new_email if new_email.strip() else None,
                        )
                        if success and user_data:
                            st.session_state.authenticated = True
                            st.session_state.user = user_data
                            st.session_state.active_tab = "🏠 Home"
                            st.success("Account created successfully! Welcome to TuneSphere.")
                            st.rerun()
                        else:
                            st.error(msg or "Failed to register account.")

        st.markdown('</div>', unsafe_allow_html=True)

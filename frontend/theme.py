"""Theme configuration, dark-cinematic CSS styling, and design tokens for TuneSphere."""

import streamlit as st


def inject_custom_css() -> None:
    """Injects custom sleek, dark-cinematic theme styles for TuneSphere Music Dashboard."""
    custom_css = """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap');

    html, body, [class*="css"], [class*="st-"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Main Container background subtle gradient */
    .stApp {
        background: radial-gradient(circle at 15% 15%, rgba(99, 102, 241, 0.08) 0%, transparent 40%),
                    radial-gradient(circle at 85% 25%, rgba(168, 85, 247, 0.06) 0%, transparent 45%),
                    #08090d;
        color: #f1f5f9;
    }

    /* Custom Scrollbars */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #08090d;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(168, 85, 247, 0.5);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0c0e14 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }

    /* Sidebar Category Headers */
    .sidebar-section-title {
        font-size: 0.72rem;
        font-weight: 700;
        color: #64748b;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin: 18px 0 8px 6px;
    }

    /* User Profile Card in Sidebar */
    .sidebar-user-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 12px 14px;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 14px;
    }

    .user-avatar-circle {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6366f1, #a855f7);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        color: #ffffff;
        font-size: 0.95rem;
        box-shadow: 0 0 12px rgba(168, 85, 247, 0.35);
    }

    /* Cinematic Hero Banner */
    .hero-cinematic {
        position: relative;
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.7) 0%, rgba(88, 28, 135, 0.5) 50%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(168, 85, 247, 0.2);
        border-radius: 20px;
        padding: 38px 42px;
        margin-bottom: 28px;
        backdrop-filter: blur(20px);
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        overflow: hidden;
    }

    .hero-cinematic::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 280px;
        height: 280px;
        background: radial-gradient(circle, rgba(168, 85, 247, 0.25) 0%, transparent 70%);
        pointer-events: none;
    }

    .hero-cinematic-title {
        font-size: 2.6rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        line-height: 1.15;
        background: linear-gradient(90deg, #ffffff 0%, #e2e8f0 40%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }

    .hero-cinematic-subtitle {
        color: #cbd5e1;
        font-size: 1.05rem;
        font-weight: 400;
        max-width: 600px;
        line-height: 1.6;
        margin-bottom: 20px;
    }

    /* Topbar Header */
    .topbar-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 16px;
        margin-bottom: 20px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    .topbar-greeting {
        font-size: 1.5rem;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: -0.02em;
    }

    .topbar-sub {
        font-size: 0.9rem;
        color: #94a3b8;
        margin-top: 2px;
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 20px 16px;
        text-align: center;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
    }

    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(168, 85, 247, 0.4);
        background: rgba(255, 255, 255, 0.04);
        box-shadow: 0 8px 24px rgba(168, 85, 247, 0.15);
    }

    .metric-number {
        font-size: 1.85rem;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 4px;
        letter-spacing: -0.02em;
    }

    .metric-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 700;
    }

    /* Song & Music Cards */
    .song-card-cinematic {
        position: relative;
        background: rgba(255, 255, 255, 0.025);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        overflow: hidden;
    }

    .song-card-cinematic:hover {
        background: rgba(255, 255, 255, 0.055);
        border-color: rgba(168, 85, 247, 0.4);
        transform: translateY(-3px);
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.4), 0 0 16px rgba(168, 85, 247, 0.12);
    }

    /* Album Artwork Placeholder with Vinyl Glow */
    .album-art-wrap {
        width: 100%;
        height: 120px;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(168, 85, 247, 0.3) 50%, rgba(236, 72, 153, 0.2) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 12px;
        position: relative;
        overflow: hidden;
    }

    .album-art-icon {
        font-size: 2.2rem;
        filter: drop-shadow(0 0 10px rgba(168, 85, 247, 0.5));
    }

    .song-title-text {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 3px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .song-artist-text {
        font-size: 0.88rem;
        color: #a78bfa;
        font-weight: 500;
        margin-bottom: 6px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .song-meta-text {
        font-size: 0.78rem;
        color: #64748b;
        font-weight: 500;
    }

    /* Badge Pills */
    .badge-pill {
        display: inline-block;
        background: rgba(99, 102, 241, 0.14);
        color: #a5b4fc;
        padding: 3px 9px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-right: 6px;
        border: 1px solid rgba(99, 102, 241, 0.25);
    }

    .score-pill {
        display: inline-block;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(5, 150, 105, 0.2));
        color: #6ee7b7;
        padding: 3px 9px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        border: 1px solid rgba(16, 185, 129, 0.35);
    }

    /* Genre Mood Chips */
    .mood-chip {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 10px 14px;
        text-align: center;
        font-weight: 600;
        font-size: 0.9rem;
        color: #e2e8f0;
        transition: all 0.2s ease;
    }

    .mood-chip:hover {
        background: rgba(168, 85, 247, 0.2);
        border-color: rgba(168, 85, 247, 0.5);
        color: #ffffff;
        transform: translateY(-2px);
    }

    /* Persistent Bottom Player Dock */
    .player-dock-spacer {
        height: 90px;
    }

    .player-dock-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(12, 14, 20, 0.94);
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(24px);
        padding: 12px 28px;
        z-index: 999999;
        box-shadow: 0 -10px 30px rgba(0, 0, 0, 0.6);
    }

    .player-vinyl-art {
        width: 44px;
        height: 44px;
        border-radius: 10px;
        background: linear-gradient(135deg, #6366f1, #a855f7);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        box-shadow: 0 0 12px rgba(168, 85, 247, 0.4);
    }

    .player-song-name {
        font-size: 0.95rem;
        font-weight: 700;
        color: #f8fafc;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .player-song-artist {
        font-size: 0.8rem;
        color: #94a3b8;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .player-progress-bar {
        height: 4px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        position: relative;
        flex: 1;
        cursor: pointer;
    }

    .player-progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #6366f1, #a855f7);
        border-radius: 4px;
        box-shadow: 0 0 8px rgba(168, 85, 247, 0.6);
    }

    .player-mode-pill {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 4px 10px;
        font-size: 0.72rem;
        color: #94a3b8;
        text-align: center;
    }

    /* Centered Login Glass Card */
    .login-glass-card {
        background: rgba(16, 20, 29, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 36px 32px;
        backdrop-filter: blur(24px);
        box-shadow: 0 20px 48px rgba(0, 0, 0, 0.5), 0 0 24px rgba(168, 85, 247, 0.15);
        max-width: 480px;
        margin: 40px auto;
    }

    /* Buttons Styling */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        border: none !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(168, 85, 247, 0.35) !important;
    }

    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(168, 85, 247, 0.5) !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

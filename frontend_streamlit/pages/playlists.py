"""Playlists page view for managing collections, tracklists, and playlist renaming."""

import streamlit as st

from backend.data.validator import ValidationResult
from backend.services.history_service import log_play_action
from backend.services.playlist_service import (
    create_user_playlist,
    delete_user_playlist,
    get_playlist_track_details,
    list_user_playlists,
    remove_track_from_playlist,
    rename_user_playlist,
)
from frontend_streamlit.components import render_topbar
from frontend_streamlit.empty_states import render_no_playlists_state


def render_playlists_page(result: ValidationResult, user_id: int) -> None:
    """Renders the dark-cinematic playlist manager interface."""
    user = st.session_state.get("user", {"username": "Music Lover"})
    render_topbar(
        greeting="Your Playlists 🎵",
        subtitle="Organize, curate, and replay your favorite music collections.",
        username=user.get("username", "Music Lover"),
    )

    # 1. Create Playlist Form
    col_form, _ = st.columns([1.5, 1])
    with col_form:
        with st.form("create_pl_form", clear_on_submit=True):
            pl_name = st.text_input("New Playlist Name", placeholder="e.g., Midnight Vibes, Cyberpunk Beats")
            submitted = st.form_submit_button("➕ Create Playlist", type="primary")
            if submitted:
                if pl_name.strip():
                    pl_id = create_user_playlist(user_id=user_id, playlist_name=pl_name.strip())
                    if pl_id:
                        st.success(f"Created playlist '{pl_name.strip()}'!")
                        st.rerun()
                else:
                    st.warning("Please enter a valid playlist name.")

    playlists = list_user_playlists(user_id=user_id)
    if not playlists:
        render_no_playlists_state()
        return

    st.markdown("---")
    st.subheader(f"Your Collections ({len(playlists)})")

    df = result.df if result.is_valid else None
    pl_cols = st.columns(3)

    for idx, pl in enumerate(playlists):
        with pl_cols[idx % 3]:
            st.markdown(
                f"""
                <div class="song-card-cinematic">
                    <div class="album-art-wrap" style="height: 90px;">
                        <span class="album-art-icon" style="font-size: 1.8rem;">📁</span>
                    </div>
                    <div class="song-title-text">{pl['playlist_name']}</div>
                    <div class="song-artist-text">{pl['song_count']} track(s)</div>
                    <div class="song-meta-text">Created: {pl['created_at']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander(f"Manage '{pl['playlist_name']}' ({pl['song_count']} tracks)"):
                # Rename section
                r_col1, r_col2 = st.columns([2.5, 1])
                with r_col1:
                    new_title = st.text_input(
                        "Rename",
                        value=pl["playlist_name"],
                        key=f"ren_input_{pl['id']}",
                        label_visibility="collapsed",
                    )
                with r_col2:
                    if st.button("Rename", key=f"ren_btn_{pl['id']}", use_container_width=True):
                        if new_title.strip() and new_title.strip() != pl["playlist_name"]:
                            rename_user_playlist(pl["id"], user_id=user_id, new_name=new_title.strip())
                            st.toast(f"Renamed playlist to '{new_title.strip()}'")
                            st.rerun()

                st.markdown("---")

                # Tracklist
                tracks = get_playlist_track_details(pl["id"], df=df)
                if not tracks:
                    st.caption("No tracks added yet. Use 'Add to Playlist' on any song card.")
                else:
                    for t_item in tracks:
                        tc1, tc2, tc3 = st.columns([2.5, 1, 1])
                        with tc1:
                            st.write(f"🎵 **{t_item['song_name']}** — {t_item['artist']}")
                        with tc2:
                            if st.button("▶ Play", key=f"pl_play_{pl['id']}_{t_item['song_id']}", use_container_width=True):
                                st.session_state.current_playing_track = t_item
                                st.session_state.player_is_playing = True
                                log_play_action(user_id, t_item["song_id"])
                                st.toast(f"▶️ Playing '{t_item['song_name']}'")
                                st.rerun()
                        with tc3:
                            if st.button("✕", key=f"rem_pl_{pl['id']}_{t_item['song_id']}", help="Remove track", use_container_width=True):
                                remove_track_from_playlist(pl["id"], t_item["song_id"])
                                st.rerun()

                st.markdown("---")
                if st.button(f"🗑️ Delete Collection", key=f"del_pl_{pl['id']}", type="secondary"):
                    delete_user_playlist(pl["id"], user_id=user_id)
                    st.toast(f"Deleted playlist '{pl['playlist_name']}'")
                    st.rerun()

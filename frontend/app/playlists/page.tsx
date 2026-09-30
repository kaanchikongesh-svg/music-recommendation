"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { apiPlaylists, apiCreatePlaylist, apiPlaylistSongs, Playlist, Song } from "@/lib/api";
import { useAuth } from "@/lib/useAuth";
import SongCard from "@/components/SongCard";

export default function PlaylistsPage() {
  const [playlists, setPlaylists] = useState<Playlist[]>([]);
  const [selectedPlaylist, setSelectedPlaylist] = useState<Playlist | null>(null);
  const [playlistSongs, setPlaylistSongs] = useState<Song[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const { user } = useAuth();

  const loadPlaylists = () => {
    setLoading(true);
    apiPlaylists()
      .then((res) => {
        const list = res.playlists || [];
        setPlaylists(list);
        if (list.length > 0 && !selectedPlaylist) {
          selectPlaylist(list[0]);
        }
      })
      .catch(() => setPlaylists([]))
      .finally(() => setLoading(false));
  };

  const selectPlaylist = (pl: Playlist) => {
    setSelectedPlaylist(pl);
    apiPlaylistSongs(pl.id)
      .then((res) => setPlaylistSongs(res.songs || []))
      .catch(() => setPlaylistSongs([]));
  };

  useEffect(() => {
    loadPlaylists();
  }, [user]);

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    try {
      const res = await apiCreatePlaylist(newTitle.trim(), newDesc.trim() || undefined);
      setNewTitle("");
      setNewDesc("");
      setModalOpen(false);
      loadPlaylists();
      if (res && res.playlist) {
        selectPlaylist(res.playlist);
      }
    } catch (err) {
      console.error("Create playlist failed", err);
    }
  };

  return (
    <div className="playlists-segment-view">
      {/* ── Hero Banner ── */}
      <section className="hero-card">
        <div className="hero-ambient-glow" />
        <div className="hero-inner">
          <h1 className="hero-brand-title">Playlists</h1>
          <p className="hero-subtitle">
            Create custom mixes, organize your favorite sounds, and build your catalog.
          </p>

          <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
            <button
              type="button"
              className="btn-accent-theme"
              onClick={() => setModalOpen(true)}
            >
              ➕ Create Playlist
            </button>
            <Link href="/discover" className="btn-secondary-pill">
              🔍 Explore Songs
            </Link>
          </div>
        </div>
      </section>

      {/* ── Playlists Content ── */}
      <section className="catalog-section">
        {loading ? (
          <div className="catalog-empty-card">
            <div className="empty-cylinder-icon">
              <svg viewBox="0 0 24 24">
                <line x1="8" y1="6" x2="21" y2="6" />
                <line x1="8" y1="12" x2="21" y2="12" />
                <line x1="8" y1="18" x2="21" y2="18" />
                <line x1="3" y1="6" x2="3.01" y2="6" />
                <line x1="3" y1="12" x2="3.01" y2="12" />
                <line x1="3" y1="18" x2="3.01" y2="18" />
              </svg>
            </div>
            <h3 className="catalog-empty-title">Loading playlists...</h3>
          </div>
        ) : playlists.length === 0 ? (
          <div className="catalog-empty-card">
            <div className="empty-cylinder-icon">
              <svg viewBox="0 0 24 24">
                <line x1="8" y1="6" x2="21" y2="6" />
                <line x1="8" y1="12" x2="21" y2="12" />
                <line x1="8" y1="18" x2="21" y2="18" />
                <line x1="3" y1="6" x2="3.01" y2="6" />
                <line x1="3" y1="12" x2="3.01" y2="12" />
                <line x1="3" y1="18" x2="3.01" y2="18" />
              </svg>
            </div>
            <h3 className="catalog-empty-title">No playlists created yet</h3>
            <p className="catalog-empty-desc">
              Organize your music collection by creating your first playlist.{" "}
              <button
                type="button"
                onClick={() => setModalOpen(true)}
                className="accent-theme-link"
              >
                Create now
              </button>
            </p>
          </div>
        ) : (
          <div>
            {/* Playlist Tabs / Chips */}
            <div className="chips-container" style={{ marginBottom: "24px" }}>
              {playlists.map((pl) => (
                <button
                  key={pl.id}
                  type="button"
                  className={`chip-item ${selectedPlaylist?.id === pl.id ? "active" : ""}`}
                  onClick={() => selectPlaylist(pl)}
                >
                  🗂️ {pl.name} ({pl.song_count ?? 0})
                </button>
              ))}
            </div>

            {selectedPlaylist && (
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "18px" }}>
                  <div>
                    <h2 style={{ fontSize: "1.2rem", fontWeight: 700, color: "#fff" }}>
                      {selectedPlaylist.name}
                    </h2>
                    {selectedPlaylist.description && (
                      <p style={{ color: "var(--text-secondary)", fontSize: "0.88rem" }}>
                        {selectedPlaylist.description}
                      </p>
                    )}
                  </div>
                </div>

                {playlistSongs.length === 0 ? (
                  <div className="catalog-empty-card" style={{ padding: "40px" }}>
                    <p className="catalog-empty-desc">
                      This playlist is currently empty. Add tracks from{" "}
                      <Link href="/discover" className="accent-theme-link">
                        Discover
                      </Link>
                      .
                    </p>
                  </div>
                ) : (
                  <div className="songs-grid-wrapper">
                    {playlistSongs.map((song) => (
                      <SongCard key={song.song_id} song={song} />
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </section>

      {/* ── Create Playlist Modal ── */}
      {modalOpen && (
        <div className="modal-backdrop" onClick={() => setModalOpen(false)}>
          <div className="modal-content-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header-row">
              <h3 className="modal-title">Create New Playlist</h3>
              <button className="modal-close-btn" onClick={() => setModalOpen(false)}>
                ✕
              </button>
            </div>
            <form onSubmit={handleCreateSubmit}>
              <div style={{ marginBottom: "16px" }}>
                <label style={{ display: "block", color: "var(--text-secondary)", fontSize: "0.85rem", marginBottom: "6px" }}>
                  Playlist Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Midnight Beats, Chill Vibes"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  style={{
                    width: "100%",
                    background: "#080a11",
                    border: "1px solid #1a2030",
                    borderRadius: "8px",
                    padding: "10px 14px",
                    color: "#fff",
                    fontSize: "0.95rem",
                    outline: "none",
                  }}
                />
              </div>

              <div style={{ marginBottom: "24px" }}>
                <label style={{ display: "block", color: "var(--text-secondary)", fontSize: "0.85rem", marginBottom: "6px" }}>
                  Description (Optional)
                </label>
                <textarea
                  placeholder="Briefly describe your mix..."
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  rows={3}
                  style={{
                    width: "100%",
                    background: "#080a11",
                    border: "1px solid #1a2030",
                    borderRadius: "8px",
                    padding: "10px 14px",
                    color: "#fff",
                    fontSize: "0.95rem",
                    outline: "none",
                    resize: "none",
                  }}
                />
              </div>

              <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end" }}>
                <button
                  type="button"
                  className="btn-secondary-pill"
                  onClick={() => setModalOpen(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn-accent-theme">
                  Create Playlist
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

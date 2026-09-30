"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiListSongs, apiFeatured, Song } from "@/lib/api";
import { usePlayer } from "@/lib/usePlayer";

export default function HomePage() {
  const router = useRouter();
  const { play } = usePlayer();
  const [searchQuery, setSearchQuery] = useState("");
  const [songs, setSongs] = useState<Song[]>([]);
  const [loading, setLoading] = useState(true);
  const [adminModalOpen, setAdminModalOpen] = useState(false);
  const [importStatus, setImportStatus] = useState<string | null>(null);

  useEffect(() => {
    async function loadCatalog() {
      try {
        const res = await apiFeatured(8).catch(() => ({ featured: [] }));
        setSongs(res.featured || []);
      } catch {
        setSongs([]);
      } finally {
        setLoading(false);
      }
    }
    loadCatalog();
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/discover?query=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const handleLoadSampleData = async () => {
    setImportStatus("Importing songs from dataset...");
    try {
      const res = await apiListSongs({ limit: 12 });
      if (res && res.songs && res.songs.length > 0) {
        setSongs(res.songs);
        setImportStatus("Catalog loaded successfully!");
        setTimeout(() => setAdminModalOpen(false), 800);
      } else {
        setImportStatus("Ready to search or stream.");
      }
    } catch (e) {
      setImportStatus("Import error. Ensure FastAPI backend is active.");
    }
  };

  return (
    <div className="home-dashboard-view">
      {/* ── Hero Card ── */}
      <section className="hero-card">
        <div className="hero-ambient-glow" />
        <div className="hero-inner">
          <h1 className="hero-brand-title">TuneSphere</h1>
          <p className="hero-subtitle">Discover your next favorite song.</p>

          <form onSubmit={handleSearchSubmit} className="hero-search-bar">
            <svg
              className="search-icon-svg"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle cx="11" cy="11" r="7" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input
              type="text"
              className="search-input-field"
              placeholder="Songs, artists, albums, genres..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button type="submit" className="hero-search-btn">
              Search
            </button>
          </form>
        </div>
      </section>

      {/* ── Catalog Section ── */}
      <section className="catalog-section">
        {loading ? (
          <div className="catalog-empty-card">
            <div className="empty-cylinder-icon">
              <svg viewBox="0 0 24 24">
                <ellipse cx="12" cy="5" rx="9" ry="3" />
                <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
                <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
              </svg>
            </div>
            <h3 className="catalog-empty-title">Loading catalog...</h3>
          </div>
        ) : songs.length === 0 ? (
          <div className="catalog-empty-card">
            <div className="empty-cylinder-icon">
              <svg viewBox="0 0 24 24">
                <ellipse cx="12" cy="5" rx="9" ry="3" />
                <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
                <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
              </svg>
            </div>
            <h3 className="catalog-empty-title">The catalog is empty</h3>
            <p className="catalog-empty-desc">
              No songs have been imported yet.{" "}
              <button
                type="button"
                onClick={() => setAdminModalOpen(true)}
                className="accent-orange-link"
              >
                Open catalog admin
              </button>
            </p>
          </div>
        ) : (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
              <h2 style={{ fontSize: "1.2rem", fontWeight: 700, color: "#fff" }}>Featured Catalog</h2>
              <Link href="/discover" className="accent-orange-link" style={{ fontSize: "0.9rem" }}>
                Browse All →
              </Link>
            </div>
            <div className="songs-grid-wrapper">
              {songs.map((song) => (
                <div key={song.song_id} className="song-item-card">
                  <div className="song-card-header">
                    <div
                      className="song-cover-thumb"
                      onClick={() => play(song)}
                      title="Play preview"
                    >
                      ▶
                    </div>
                    <div className="song-card-meta">
                      <div className="song-title-text" title={song.song_name}>
                        {song.song_name}
                      </div>
                      <div className="song-artist-text">{song.artist}</div>
                    </div>
                  </div>
                  <div className="song-tags-row">
                    {song.genre && (
                      <span className="badge-tag accent">{song.genre}</span>
                    )}
                    {song.year && (
                      <span className="badge-tag">{song.year}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* ── Catalog Admin Modal ── */}
      {adminModalOpen && (
        <div className="modal-backdrop" onClick={() => setAdminModalOpen(false)}>
          <div
            className="modal-content-card"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-header-row">
              <h3 className="modal-title">Catalog Administration</h3>
              <button
                className="modal-close-btn"
                onClick={() => setAdminModalOpen(false)}
              >
                ✕
              </button>
            </div>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem", marginBottom: "20px" }}>
              Initialize or reload tracks from the backend machine learning dataset into your active session.
            </p>
            {importStatus && (
              <div
                style={{
                  background: "#151928",
                  padding: "10px 16px",
                  borderRadius: "8px",
                  fontSize: "0.85rem",
                  color: "var(--accent-orange)",
                  marginBottom: "16px",
                }}
              >
                {importStatus}
              </div>
            )}
            <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end" }}>
              <button
                type="button"
                onClick={() => setAdminModalOpen(false)}
                style={{
                  background: "transparent",
                  color: "#94a3b8",
                  border: "1px solid #1e2538",
                  borderRadius: "8px",
                  padding: "8px 18px",
                  cursor: "pointer",
                }}
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleLoadSampleData}
                style={{
                  background: "var(--accent-orange)",
                  color: "#000",
                  fontWeight: 700,
                  border: "none",
                  borderRadius: "8px",
                  padding: "8px 20px",
                  cursor: "pointer",
                }}
              >
                Sync Catalog
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

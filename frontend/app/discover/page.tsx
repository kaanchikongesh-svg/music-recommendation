"use client";

import React, { useEffect, useState } from "react";
import SongCard from "@/components/SongCard";
import { apiListSongs, apiGenres, Song } from "@/lib/api";

export default function DiscoverPage() {
  const [songs, setSongs] = useState<Song[]>([]);
  const [genres, setGenres] = useState<string[]>([]);
  const [selectedGenre, setSelectedGenre] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [total, setTotal] = useState<number>(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGenres()
      .then((res) => setGenres(res.genres || []))
      .catch((err) => console.error("Failed to load genres", err));
  }, []);

  useEffect(() => {
    let isCancelled = false;
    setLoading(true);

    apiListSongs({
      query: searchQuery || undefined,
      genre: selectedGenre || undefined,
      page: page,
      limit: 18,
    })
      .then((res) => {
        if (!isCancelled) {
          setSongs(res.songs || []);
          setTotalPages(res.total_pages || 1);
          setTotal(res.total || 0);
        }
      })
      .catch((err) => console.error("Error loading songs:", err))
      .finally(() => {
        if (!isCancelled) setLoading(false);
      });

    return () => {
      isCancelled = true;
    };
  }, [searchQuery, selectedGenre, page]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
  };

  return (
    <div className="discover-segment-view">
      {/* ── Hero Banner ── */}
      <section className="hero-card">
        <div className="hero-ambient-glow" />
        <div className="hero-inner">
          <h1 className="hero-brand-title">Discover</h1>
          <p className="hero-subtitle">Explore the music catalog and filter by audio genres.</p>

          <form onSubmit={handleSearchSubmit} className="hero-search-bar">
            <svg className="search-icon-svg" viewBox="0 0 24 24" aria-hidden="true">
              <circle cx="11" cy="11" r="7" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input
              type="text"
              className="search-input-field"
              placeholder="Search by title, artist, or album..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setPage(1);
              }}
            />
            <button type="submit" className="btn-accent-theme">
              Search
            </button>
          </form>

          {/* Genre Chips */}
          <div className="chips-container">
            <button
              type="button"
              className={`chip-item ${selectedGenre === "" ? "active" : ""}`}
              onClick={() => {
                setSelectedGenre("");
                setPage(1);
              }}
            >
              All Genres
            </button>
            {genres.map((g) => (
              <button
                key={g}
                type="button"
                className={`chip-item ${selectedGenre === g ? "active" : ""}`}
                onClick={() => {
                  setSelectedGenre(g);
                  setPage(1);
                }}
              >
                {g}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* ── Catalog Grid Section ── */}
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
            <h3 className="catalog-empty-title">Loading tracks...</h3>
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
            <h3 className="catalog-empty-title">No songs found</h3>
            <p className="catalog-empty-desc">
              Try adjusting your search query or{" "}
              <button
                type="button"
                onClick={() => {
                  setSearchQuery("");
                  setSelectedGenre("");
                  setPage(1);
                }}
                className="accent-theme-link"
              >
                reset filters
              </button>
            </p>
          </div>
        ) : (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "18px" }}>
              <h2 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#fff" }}>
                Found {total} Tracks {selectedGenre && `• ${selectedGenre}`}
              </h2>
            </div>

            <div className="songs-grid-wrapper">
              {songs.map((song) => (
                <SongCard key={song.song_id} song={song} />
              ))}
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: "16px", marginTop: "32px" }}>
                <button
                  type="button"
                  className="btn-secondary-pill"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  style={{ opacity: page <= 1 ? 0.4 : 1, cursor: page <= 1 ? "default" : "pointer" }}
                >
                  ← Previous
                </button>
                <span style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
                  Page {page} of {totalPages}
                </span>
                <button
                  type="button"
                  className="btn-secondary-pill"
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  style={{ opacity: page >= totalPages ? 0.4 : 1, cursor: page >= totalPages ? "default" : "pointer" }}
                >
                  Next →
                </button>
              </div>
            )}
          </div>
        )}
      </section>
    </div>
  );
}

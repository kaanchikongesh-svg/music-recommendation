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

  // Fetch available genres once
  useEffect(() => {
    apiGenres()
      .then((res) => setGenres(res.genres || []))
      .catch((err) => console.error("Failed to load genres", err));
  }, []);

  // Fetch songs on query, genre, or page change
  useEffect(() => {
    let isCancelled = false;
    setLoading(true);

    apiListSongs({
      query: searchQuery || undefined,
      genre: selectedGenre || undefined,
      page: page,
      limit: 16,
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

  return (
    <div className="discover-container">
      <header className="page-header">
        <h1 className="page-title">
          Explore <span className="gradient-text">Catalog</span>
        </h1>
        <p className="page-subtitle">
          Search through real audio tracks, filter by genre, and discover new sounds.
        </p>
      </header>

      {/* Filters & Search */}
      <div className="filter-bar">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search by song name or artist..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setPage(1);
            }}
            className="search-input"
          />
          {searchQuery && (
            <button
              className="clear-btn"
              onClick={() => {
                setSearchQuery("");
                setPage(1);
              }}
            >
              ✕
            </button>
          )}
        </div>

        {/* Genre Pill Selector */}
        <div className="genre-pills">
          <button
            className={`pill ${selectedGenre === "" ? "active" : ""}`}
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
              className={`pill ${selectedGenre === g ? "active" : ""}`}
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

      {/* Results Header */}
      <div className="results-header">
        <span className="results-count">
          Showing {songs.length} of {total} songs
        </span>
      </div>

      {/* Song Grid */}
      {loading ? (
        <div className="loading-grid">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="skeleton-card" />
          ))}
        </div>
      ) : songs.length > 0 ? (
        <>
          <div className="song-grid">
            {songs.map((song) => (
              <SongCard key={song.song_id} song={song} />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="pagination">
              <button
                className="btn btn-secondary"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                ← Previous
              </button>
              <span className="page-indicator">
                Page {page} of {totalPages}
              </span>
              <button
                className="btn btn-secondary"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              >
                Next →
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="empty-box">
          <p>No songs match your search or filter.</p>
        </div>
      )}
    </div>
  );
}

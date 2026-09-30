"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import SongCard from "@/components/SongCard";
import { apiFavorites, Song } from "@/lib/api";
import { useAuth } from "@/lib/useAuth";

export default function FavoritesPage() {
  const [favorites, setFavorites] = useState<Song[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  const loadFavorites = () => {
    setLoading(true);
    apiFavorites()
      .then((res) => setFavorites(res.favorites || []))
      .catch(() => setFavorites([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadFavorites();
  }, [user]);

  return (
    <div className="favorites-segment-view">
      {/* ── Hero Banner ── */}
      <section className="hero-card">
        <div className="hero-ambient-glow" />
        <div className="hero-inner">
          <h1 className="hero-brand-title">Favorites</h1>
          <p className="hero-subtitle">
            Your collection of loved tracks and curated sound bookmarks.
          </p>

          <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
            <Link href="/discover" className="btn-accent-theme">
              🔍 Find More Tracks
            </Link>
          </div>
        </div>
      </section>

      {/* ── Favorites Grid Section ── */}
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
            <h3 className="catalog-empty-title">Loading your favorites...</h3>
          </div>
        ) : favorites.length === 0 ? (
          <div className="catalog-empty-card">
            <div className="empty-cylinder-icon">
              <svg viewBox="0 0 24 24">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
              </svg>
            </div>
            <h3 className="catalog-empty-title">No favorites yet</h3>
            <p className="catalog-empty-desc">
              Tap the heart icon on any song in{" "}
              <Link href="/discover" className="accent-theme-link">
                Discover
              </Link>{" "}
              to save it here.
            </p>
          </div>
        ) : (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "18px" }}>
              <h2 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#fff" }}>
                Saved Tracks ({favorites.length})
              </h2>
            </div>

            <div className="songs-grid-wrapper">
              {favorites.map((song) => (
                <SongCard
                  key={song.song_id}
                  song={song}
                  isFav={true}
                  onFavToggle={loadFavorites}
                />
              ))}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

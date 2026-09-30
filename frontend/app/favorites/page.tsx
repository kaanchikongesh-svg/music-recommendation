"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import SongCard from "@/components/SongCard";
import { useAuth } from "@/lib/useAuth";
import { apiFavorites, Song } from "@/lib/api";

export default function FavoritesPage() {
  const { user, loading: authLoading } = useAuth();
  const [favorites, setFavorites] = useState<Song[]>([]);
  const [loading, setLoading] = useState(true);

  const loadFavs = async () => {
    if (!user) return;
    setLoading(true);
    try {
      const res = await apiFavorites();
      setFavorites(res.favorites || []);
    } catch (err) {
      console.error("Failed to fetch favorites:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) loadFavs();
  }, [user]);

  if (authLoading) return <div className="p-8 text-center text-muted">Checking authentication...</div>;

  if (!user) {
    return (
      <div className="auth-required-box">
        <h2>🔒 Sign In Required</h2>
        <p>Please log in to view and save your favorite songs.</p>
        <Link href="/login" className="btn btn-primary mt-4">
          Sign In
        </Link>
      </div>
    );
  }

  return (
    <div className="favorites-container">
      <header className="page-header">
        <h1 className="page-title">
          Your <span className="gradient-text">Favorites</span>
        </h1>
        <p className="page-subtitle">Tracks you saved for quick access and recommendation tuning.</p>
      </header>

      {loading ? (
        <div className="loading-grid">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="skeleton-card" />
          ))}
        </div>
      ) : favorites.length > 0 ? (
        <div className="song-grid">
          {favorites.map((song) => (
            <SongCard key={song.song_id} song={song} isFav={true} onFavToggle={loadFavs} />
          ))}
        </div>
      ) : (
        <div className="empty-box">
          <p>You haven&apos;t added any favorites yet.</p>
          <Link href="/discover" className="btn btn-secondary mt-4">
            Discover Songs
          </Link>
        </div>
      )}
    </div>
  );
}

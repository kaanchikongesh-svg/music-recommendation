"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import SongCard from "@/components/SongCard";
import { apiFeatured, apiRecommendations, apiCatalogStats, Song, Recommendation } from "@/lib/api";

export default function HomePage() {
  const [featured, setFeatured] = useState<Song[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [stats, setStats] = useState<{ total_songs?: number; total_genres?: number; total_artists?: number }>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [featRes, recRes, statsRes] = await Promise.all([
          apiFeatured(8).catch(() => ({ featured: [] })),
          apiRecommendations(undefined, 8).catch(() => ({ recommendations: [], type: "" })),
          apiCatalogStats().catch(() => ({})),
        ]);
        setFeatured(featRes.featured || []);
        setRecommendations(recRes.recommendations || []);
        setStats(statsRes);
      } catch (err) {
        console.error("Error loading homepage data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="home-container">
      {/* Hero Banner */}
      <section className="hero-banner">
        <div className="hero-content">
          <span className="hero-badge font-mono">✨ POWERED BY TF-IDF ENGINE</span>
          <h1 className="hero-title">
            Discover Your Next <span className="gradient-text">Musical Obsession</span>
          </h1>
          <p className="hero-subtitle">
            Smart content-based music recommendations powered by vector similarity across thousands of real tracks.
          </p>

          <div className="hero-actions">
            <Link href="/recommendations" className="btn btn-primary">
              ⚡ Get Recommendations
            </Link>
            <Link href="/discover" className="btn btn-secondary">
              🔍 Explore Catalog
            </Link>
          </div>
        </div>

        {/* Stats Row */}
        <div className="stats-row">
          <div className="stat-card">
            <span className="stat-val">{stats.total_songs ?? "1,000+"}</span>
            <span className="stat-label">Tracks Analyzed</span>
          </div>
          <div className="stat-card">
            <span className="stat-val">{stats.total_genres ?? "15+"}</span>
            <span className="stat-label">Genres</span>
          </div>
          <div className="stat-card">
            <span className="stat-val">100%</span>
            <span className="stat-label">Real Dataset</span>
          </div>
        </div>
      </section>

      {/* Recommended For You */}
      <section className="section">
        <div className="section-header">
          <div>
            <h2 className="section-title">🔥 Top Recommendations</h2>
            <p className="section-subtitle">Handpicked based on audio feature similarities</p>
          </div>
          <Link href="/recommendations" className="view-all-link">
            View engine →
          </Link>
        </div>

        {loading ? (
          <div className="loading-grid">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="skeleton-card" />
            ))}
          </div>
        ) : recommendations.length > 0 ? (
          <div className="song-grid">
            {recommendations.map((song) => (
              <SongCard key={song.song_id} song={song} />
            ))}
          </div>
        ) : (
          <div className="empty-box">
            <p>No recommendations loaded yet. Make sure the backend is running!</p>
          </div>
        )}
      </section>

      {/* Featured Songs */}
      <section className="section">
        <div className="section-header">
          <div>
            <h2 className="section-title">🎵 Featured Catalog Tracks</h2>
            <p className="section-subtitle">Popular selections from the library</p>
          </div>
          <Link href="/discover" className="view-all-link">
            Browse all →
          </Link>
        </div>

        {loading ? (
          <div className="loading-grid">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="skeleton-card" />
            ))}
          </div>
        ) : featured.length > 0 ? (
          <div className="song-grid">
            {featured.map((song) => (
              <SongCard key={song.song_id} song={song} />
            ))}
          </div>
        ) : (
          <div className="empty-box">
            <p>No songs found in catalog.</p>
          </div>
        )}
      </section>
    </div>
  );
}

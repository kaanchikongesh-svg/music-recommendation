"use client";

import React, { useEffect, useState, useTransition } from "react";
import SongCard from "@/components/SongCard";
import SongDetailsModal from "@/components/SongDetailsModal";
import { apiTamilSongs, apiRecommendations, Song, Recommendation } from "@/lib/api";
import { Sparkles, Music2, Search, Disc3, Mic2 } from "lucide-react";

const POPULAR_TAMIL_ARTISTS = [
  "All",
  "Ilaiyaraaja",
  "A. R. Rahman",
  "D. Imman",
  "Anirudh",
  "Yuvan Shankar Raja",
  "Harris Jayaraj",
  "G. V. Prakash Kumar",
  "S. P. Balasubramaniam",
  "Sid Sriram",
];

export default function TamilMusicPage() {
  const [songs, setSongs] = useState<Song[]>([]);
  const [featuredTamil, setFeaturedTamil] = useState<Song[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedArtist, setSelectedArtist] = useState("All");
  const [selectedSongDetails, setSelectedSongDetails] = useState<Song | Recommendation | null>(null);
  const [, startTransition] = useTransition();

  const loadTamilSongs = async (pageNum: number, query = searchQuery, artist = selectedArtist) => {
    setLoading(true);
    try {
      const res = await apiTamilSongs({
        page: pageNum,
        limit: 24,
        query: query.trim() || undefined,
        artist: artist !== "All" ? artist : undefined,
      });
      setSongs(res.songs || []);
      setTotal(res.total || 0);
      setTotalPages(res.total_pages || 1);
    } catch (e) {
      console.error("Error loading Tamil songs:", e);
      setSongs([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial featured load
    apiTamilSongs(1, 4)
      .then((res) => setFeaturedTamil(res.songs || []))
      .catch(() => {});
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      loadTamilSongs(page, searchQuery, selectedArtist);
    }, 250);
    return () => clearTimeout(timer);
  }, [page, searchQuery, selectedArtist]);

  const handleArtistSelect = (artist: string) => {
    startTransition(() => {
      setSelectedArtist(artist);
      setPage(1);
    });
  };

  return (
    <div className="section-container">
      {/* ── Tamil Hero Banner ── */}
      <div
        className="hero-card"
        style={{
          background: "linear-gradient(135deg, rgba(245, 130, 32, 0.16) 0%, rgba(10, 12, 20, 0.95) 100%)",
          border: "1px solid var(--accent-border)",
          marginBottom: 32,
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div className="hero-ambient-glow" />
        <div style={{ position: "relative", zIndex: 2 }}>
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 6,
              padding: "4px 12px",
              borderRadius: "var(--radius-pill)",
              background: "var(--accent-soft)",
              border: "1px solid var(--accent-border)",
              color: "var(--accent-color)",
              fontSize: "0.78rem",
              fontWeight: 800,
              letterSpacing: "0.06em",
              marginBottom: 12,
            }}
          >
            <Sparkles size={13} />
            REAL TAMIL MUSIC CATALOG & AI ENGINE
          </div>
          <h1 className="hero-brand-title" style={{ fontSize: "2.8rem", marginBottom: 8 }}>
            Explore Tamil Music
          </h1>
          <p className="hero-subtitle" style={{ maxWidth: 620, color: "#cbd5e1" }}>
            Discover Tamil songs and artists with intelligent recommendations.
          </p>

          {/* Search Tamil songs (Supports Tamil Unicode and English) */}
          <div style={{ position: "relative", maxWidth: 540, marginTop: 20 }}>
            <Search
              size={18}
              style={{
                position: "absolute",
                left: 16,
                top: "50%",
                transform: "translateY(-50%)",
                color: "var(--text-muted)",
              }}
            />
            <input
              type="text"
              className="search-input-field"
              style={{ paddingLeft: 46, height: 48, fontSize: "0.95rem" }}
              placeholder="Search Tamil songs, artists, lyrics (தமிழ் / English)..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setPage(1);
              }}
            />
          </div>
        </div>
      </div>

      {/* ── Tamil Artists Section ── */}
      <section style={{ marginBottom: 32 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
          <Mic2 size={16} style={{ color: "var(--accent-color)" }} />
          <h2 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#fff", margin: 0 }}>
            Tamil Artists
          </h2>
        </div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {POPULAR_TAMIL_ARTISTS.map((art) => (
            <button
              key={art}
              type="button"
              className={`filter-pill ${selectedArtist === art ? "active" : ""}`}
              onClick={() => handleArtistSelect(art)}
            >
              {art}
            </button>
          ))}
        </div>
      </section>

      {/* ── Recommended For You / Featured Tamil Picks ── */}
      {featuredTamil.length > 0 && selectedArtist === "All" && !searchQuery && (
        <section style={{ marginBottom: 40 }}>
          <div className="section-header" style={{ marginBottom: 16 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <Sparkles size={18} style={{ color: "var(--accent-color)" }} />
              <h2 className="section-title">Recommended for You</h2>
            </div>
            <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
              Acoustic & lyrical highlights
            </span>
          </div>
          <div className="songs-grid">
            {featuredTamil.map((song) => (
              <SongCard
                key={`feat-${song.song_id}`}
                song={song}
                onViewDetails={(s) => setSelectedSongDetails(s)}
              />
            ))}
          </div>
        </section>
      )}

      {/* ── Tamil Songs Catalog Results ── */}
      <section>
        <div className="section-header" style={{ marginBottom: 16 }}>
          <h2 className="section-title">
            Tamil Songs {total > 0 ? `(${total.toLocaleString()})` : ""}
          </h2>
          {totalPages > 1 && (
            <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
              Page {page} of {totalPages}
            </span>
          )}
        </div>

        {loading ? (
          <div style={{ padding: "60px 0", textAlign: "center", color: "var(--text-secondary)" }}>
            <div className="animate-spin" style={{ display: "inline-block", marginBottom: 12 }}>
              <Disc3 size={32} style={{ color: "var(--accent-color)" }} />
            </div>
            <div>Loading Tamil songs from catalog...</div>
          </div>
        ) : songs.length > 0 ? (
          <>
            <div className="songs-grid">
              {songs.map((song) => (
                <SongCard
                  key={song.song_id}
                  song={song}
                  onViewDetails={(s) => setSelectedSongDetails(s)}
                />
              ))}
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div
                style={{
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  gap: 12,
                  marginTop: 36,
                }}
              >
                <button
                  type="button"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  className="filter-pill"
                  style={{ opacity: page <= 1 ? 0.4 : 1, cursor: page <= 1 ? "not-allowed" : "pointer" }}
                >
                  Previous
                </button>
                <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                  Page {page} of {totalPages}
                </span>
                <button
                  type="button"
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  className="filter-pill"
                  style={{
                    opacity: page >= totalPages ? 0.4 : 1,
                    cursor: page >= totalPages ? "not-allowed" : "pointer",
                  }}
                >
                  Next
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="empty-catalog-card">
            <div className="empty-icon-box">
              <Music2 size={32} />
            </div>
            <h3 className="empty-title">No matching Tamil songs found</h3>
            <p className="empty-desc">
              Try searching with different Tamil keywords or artist filters.
            </p>
          </div>
        )}
      </section>

      {/* ── Song Details & Recommendations Modal ── */}
      {selectedSongDetails && (
        <SongDetailsModal
          song={selectedSongDetails}
          onClose={() => setSelectedSongDetails(null)}
          onSelectSong={(newSong) => setSelectedSongDetails(newSong)}
        />
      )}
    </div>
  );
}

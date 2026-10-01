"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import SongCard from "@/components/SongCard";
import SongDetailsModal from "@/components/SongDetailsModal";
import { apiFeatured, apiLanguages, apiTamilSongs, Song, Recommendation } from "@/lib/api";
import { Search, Sparkles, Music, ArrowRight, Globe } from "lucide-react";

export default function HomePage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");
  const [featuredSongs, setFeaturedSongs] = useState<Song[]>([]);
  const [tamilSongs, setTamilSongs] = useState<Song[]>([]);
  const [languages, setLanguages] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSongDetails, setSelectedSongDetails] = useState<Song | Recommendation | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [featRes, tamilRes, langRes] = await Promise.all([
          apiFeatured(8).catch(() => ({ featured: [] })),
          apiTamilSongs(1, 4).catch(() => ({ songs: [] })),
          apiLanguages().catch(() => ({ languages: [] })),
        ]);
        setFeaturedSongs(featRes.featured || []);
        setTamilSongs(tamilRes.songs || []);
        setLanguages(langRes.languages || []);
      } catch (err) {
        console.error("Failed to load home catalog:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/discover?query=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <div className="section-container">
      {/* ── Hero Card ── */}
      <section className="hero-card" style={{ marginBottom: 36 }}>
        <div className="hero-ambient-glow" />
        <div className="hero-inner" style={{ position: "relative", zIndex: 2 }}>
          <h1 className="hero-brand-title">TuneSphere</h1>
          <p className="hero-subtitle" style={{ fontSize: "1.2rem", fontWeight: 600, color: "#ffffff", marginBottom: 4 }}>
            Discover your next favorite song.
          </p>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.92rem", marginBottom: 24, maxWidth: 520 }}>
            Explore music powered by real data and intelligent recommendations.
          </p>

          <form onSubmit={handleSearchSubmit} className="hero-search-bar" style={{ maxWidth: 540 }}>
            <Search
              size={18}
              style={{
                position: "absolute",
                left: 18,
                top: "50%",
                transform: "translateY(-50%)",
                color: "var(--text-muted)",
              }}
            />
            <input
              type="text"
              className="search-input-field"
              style={{ paddingLeft: 46 }}
              placeholder="Songs, artists, lyrics, Tamil (தமிழ்)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button type="submit" className="hero-search-btn">
              Search
            </button>
          </form>
        </div>
      </section>

      {/* ── Tamil Music Highlight ── */}
      <section style={{ marginBottom: 40 }}>
        <div
          style={{
            padding: "24px 28px",
            borderRadius: "var(--radius-card)",
            background: "linear-gradient(135deg, rgba(245, 130, 32, 0.12) 0%, rgba(14, 17, 26, 0.8) 100%)",
            border: "1px solid var(--accent-border)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: 16,
            marginBottom: 16,
          }}
        >
          <div>
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
                color: "var(--accent-color)",
                fontSize: "0.78rem",
                fontWeight: 800,
                letterSpacing: "0.05em",
                marginBottom: 6,
              }}
            >
              <Sparkles size={13} />
              TAMIL MUSIC
            </div>
            <h2 style={{ fontSize: "1.4rem", fontWeight: 800, color: "#fff", marginBottom: 4 }}>
              Explore Tamil Music
            </h2>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.88rem" }}>
              Explore Tamil songs and discover similar music.
            </p>
          </div>
          <Link
            href="/tamil-music"
            className="accent-orange-link"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 6,
              padding: "10px 20px",
              borderRadius: "var(--radius-pill)",
              background: "var(--accent-color)",
              color: "#000",
              fontWeight: 700,
              fontSize: "0.88rem",
              textDecoration: "none",
            }}
          >
            View All Tamil Music →
            <ArrowRight size={16} />
          </Link>
        </div>

        {tamilSongs.length > 0 && (
          <div className="songs-grid" style={{ marginTop: 16 }}>
            {tamilSongs.map((song) => (
              <SongCard
                key={song.song_id}
                song={song}
                onViewDetails={(s) => setSelectedSongDetails(s)}
              />
            ))}
          </div>
        )}
      </section>

      {/* ── Discover by Language ── */}
      {languages.length > 0 && (
        <section style={{ marginBottom: 40 }}>
          <div className="section-header" style={{ marginBottom: 16 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <Globe size={18} style={{ color: "var(--accent-color)" }} />
              <h2 className="section-title">Discover by Language</h2>
            </div>
          </div>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            <Link
              href="/discover"
              className="filter-pill active"
              style={{ textDecoration: "none" }}
            >
              All
            </Link>
            {languages.map((lang) => (
              <Link
                key={lang}
                href={lang.toLowerCase() === "tamil" ? "/tamil-music" : `/discover?language=${encodeURIComponent(lang)}`}
                className="filter-pill"
                style={{ textDecoration: "none" }}
              >
                {lang}
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* ── Featured Music Catalog ── */}
      <section>
        <div className="section-header" style={{ marginBottom: 16 }}>
          <h2 className="section-title">Recommended for You</h2>
          <Link href="/discover" className="accent-orange-link" style={{ fontSize: "0.88rem" }}>
            Browse All (61,900+) →
          </Link>
        </div>

        {loading ? (
          <div style={{ padding: "60px 0", textAlign: "center", color: "var(--text-secondary)" }}>
            Loading real catalog...
          </div>
        ) : featuredSongs.length > 0 ? (
          <div className="songs-grid">
            {featuredSongs.map((song) => (
              <SongCard
                key={song.song_id}
                song={song}
                onViewDetails={(s) => setSelectedSongDetails(s)}
              />
            ))}
          </div>
        ) : (
          <div className="empty-catalog-card">
            <div className="empty-icon-box">
              <Music size={28} />
            </div>
            <h3 className="empty-title">The catalog is empty</h3>
            <p className="empty-desc">No songs have been imported yet.</p>
          </div>
        )}
      </section>

      {/* ── Song Details Modal ── */}
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

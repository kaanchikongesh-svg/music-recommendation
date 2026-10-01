"use client";

import React, { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import SongCard from "@/components/SongCard";
import SongDetailsModal from "@/components/SongDetailsModal";
import { apiListSongs, apiGenres, apiLanguages, Song, Recommendation } from "@/lib/api";
import { Search, Globe, Music2, Disc3 } from "lucide-react";
import { useRouter } from "next/navigation";

function DiscoverContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("query") || "";
  const initialLang = searchParams.get("language") || "";

  const [songs, setSongs] = useState<Song[]>([]);
  const [genres, setGenres] = useState<string[]>([]);
  const [languages, setLanguages] = useState<string[]>([]);
  const [selectedGenre, setSelectedGenre] = useState<string>("");
  const [selectedLanguage, setSelectedLanguage] = useState<string>(initialLang);
  const [searchQuery, setSearchQuery] = useState<string>(initialQuery);
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [total, setTotal] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [selectedSongDetails, setSelectedSongDetails] = useState<Song | Recommendation | null>(null);

  useEffect(() => {
    Promise.all([
      apiGenres().catch(() => ({ genres: [] })),
      apiLanguages().catch(() => ({ languages: [] })),
    ]).then(([genreRes, langRes]) => {
      setGenres(genreRes.genres || []);
      setLanguages(langRes.languages || []);
    });
  }, []);

  useEffect(() => {
    let isCancelled = false;
    setLoading(true);

    apiListSongs({
      query: searchQuery || undefined,
      genre: selectedGenre || undefined,
      language: selectedLanguage || undefined,
      page: page,
      limit: 24,
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
  }, [searchQuery, selectedGenre, selectedLanguage, page]);

  return (
    <div className="section-container">
      {/* Hero Card */}
      <section className="hero-card" style={{ marginBottom: 32 }}>
        <div className="hero-ambient-glow" />
        <div className="hero-inner" style={{ position: "relative", zIndex: 2 }}>
          <h1 className="hero-brand-title">Discover</h1>
          <p className="hero-subtitle">
            Explore {total.toLocaleString()} tracks across artists, lyrics, and languages.
          </p>

          <div className="hero-search-bar" style={{ maxWidth: 540 }}>
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
              placeholder="Search by title, artist, or lyrics..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setPage(1);
              }}
            />
          </div>
        </div>
      </section>

      {/* Real Language Filter (Only languages present in DB) */}
      {languages.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8, fontSize: "0.82rem", color: "var(--text-secondary)", fontWeight: 600 }}>
            <Globe size={14} style={{ color: "var(--accent-color)" }} />
            <span>Language:</span>
          </div>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <button
              type="button"
              className={`filter-pill ${selectedLanguage === "" ? "active" : ""}`}
              onClick={() => {
                setSelectedLanguage("");
                setPage(1);
              }}
            >
              All Languages
            </button>
            {languages.map((lang) => (
              <button
                key={lang}
                type="button"
                className={`filter-pill ${selectedLanguage === lang ? "active" : ""}`}
                onClick={() => {
                  if (lang.toLowerCase() === "tamil") {
                    router.push("/tamil-music");
                  } else {
                    setSelectedLanguage(lang);
                    setPage(1);
                  }
                }}
              >
                {lang}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Real Genre Filter (Only genres present in DB) */}
      {genres.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8, fontSize: "0.82rem", color: "var(--text-secondary)", fontWeight: 600 }}>
            <Music2 size={14} style={{ color: "var(--accent-color)" }} />
            <span>Genre:</span>
          </div>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <button
              type="button"
              className={`filter-pill ${selectedGenre === "" ? "active" : ""}`}
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
                className={`filter-pill ${selectedGenre === g ? "active" : ""}`}
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
      )}

      {/* Results Header */}
      <div className="section-header" style={{ marginBottom: 16 }}>
        <h2 className="section-title">Tracks ({total.toLocaleString()})</h2>
        {totalPages > 1 && (
          <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
            Page {page} of {totalPages}
          </span>
        )}
      </div>

      {/* Songs Grid */}
      {loading ? (
        <div style={{ padding: "60px 0", textAlign: "center", color: "var(--text-secondary)" }}>
          <div className="animate-spin" style={{ display: "inline-block", marginBottom: 12 }}>
            <Disc3 size={32} style={{ color: "var(--accent-color)" }} />
          </div>
          <div>Loading catalog tracks...</div>
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
          <h3 className="empty-title">No matching songs found</h3>
          <p className="empty-desc">
            Try adjusting your search query, language, or genre filters.
          </p>
        </div>
      )}

      {/* Song Details Modal */}
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

export default function DiscoverPage() {
  return (
    <Suspense fallback={<div style={{ padding: 40, color: "#94a3b8" }}>Loading Discover...</div>}>
      <DiscoverContent />
    </Suspense>
  );
}

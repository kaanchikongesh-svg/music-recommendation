"use client";

import React, { useEffect, useState } from "react";
import SongCard from "@/components/SongCard";
import { apiRecommendations, apiListSongs, Recommendation, Song } from "@/lib/api";

export default function ForYouPage() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [candidateSongs, setCandidateSongs] = useState<Song[]>([]);
  const [selectedSeedId, setSelectedSeedId] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [recType, setRecType] = useState<string>("personalized");
  const [languageMode, setLanguageMode] = useState<"same" | "any">("same");

  useEffect(() => {
    apiListSongs({ limit: 10 })
      .then((res) => setCandidateSongs(res.songs || []))
      .catch(() => {});
  }, []);

  useEffect(() => {
    fetchRecommendations(selectedSeedId, languageMode);
  }, [selectedSeedId, languageMode]);

  const fetchRecommendations = async (seedId?: string, mode: "same" | "any" = languageMode) => {
    setLoading(true);
    try {
      const res = await apiRecommendations(seedId || undefined, 12, mode);
      setRecommendations(res.recommendations || []);
      setRecType(res.type || "personalized");
    } catch {
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="for-you-segment-view">
      {/* ── Hero Banner ── */}
      <section className="hero-card">
        <div className="hero-ambient-glow" />
        <div className="hero-inner">
          <h1 className="hero-brand-title">For You</h1>
          <p className="hero-subtitle">
            AI-driven recommendations tailored to your taste profile and acoustic similarities.
          </p>

          <div style={{ display: "flex", gap: "12px", alignItems: "center", flexWrap: "wrap" }}>
            <button
              type="button"
              className="btn-accent-theme"
              onClick={() => {
                setSelectedSeedId("");
                fetchRecommendations("");
              }}
            >
              ⚡ Personalized Taste Radar
            </button>
            <button
              type="button"
              className="btn-secondary-pill"
              onClick={() => {
                if (candidateSongs.length > 0) {
                  const randomSong = candidateSongs[Math.floor(Math.random() * candidateSongs.length)];
                  setSelectedSeedId(randomSong.song_id);
                }
              }}
            >
              🎲 Surprise Me (Random Seed)
            </button>

            {/* Language Recommendation Mode Toggle */}
            <div style={{ display: "inline-flex", background: "rgba(255,255,255,0.06)", borderRadius: "20px", padding: "3px", border: "1px solid rgba(255,255,255,0.12)", marginLeft: "auto" }}>
              <button
                type="button"
                style={{
                  background: languageMode === "same" ? "var(--signature-accent, #6366f1)" : "transparent",
                  color: languageMode === "same" ? "#fff" : "var(--text-secondary)",
                  border: "none",
                  borderRadius: "16px",
                  padding: "6px 14px",
                  fontSize: "0.8rem",
                  fontWeight: 600,
                  cursor: "pointer",
                  transition: "all 0.2s ease"
                }}
                onClick={() => setLanguageMode("same")}
              >
                🌐 Same Language Mode
              </button>
              <button
                type="button"
                style={{
                  background: languageMode === "any" ? "var(--signature-accent, #6366f1)" : "transparent",
                  color: languageMode === "any" ? "#fff" : "var(--text-secondary)",
                  border: "none",
                  borderRadius: "16px",
                  padding: "6px 14px",
                  fontSize: "0.8rem",
                  fontWeight: 600,
                  cursor: "pointer",
                  transition: "all 0.2s ease"
                }}
                onClick={() => setLanguageMode("any")}
              >
                🔀 Cross-Language Mode
              </button>
            </div>
          </div>

          {/* Seed track selection chips */}
          {candidateSongs.length > 0 && (
            <div style={{ marginTop: "24px" }}>
              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "8px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Select Seed Track for Vector Matching:
              </div>
              <div className="chips-container">
                <button
                  type="button"
                  className={`chip-item ${selectedSeedId === "" ? "active" : ""}`}
                  onClick={() => setSelectedSeedId("")}
                >
                  Taste Centroid
                </button>
                {candidateSongs.slice(0, 6).map((s) => (
                  <button
                    key={s.song_id}
                    type="button"
                    className={`chip-item ${selectedSeedId === s.song_id ? "active" : ""}`}
                    onClick={() => setSelectedSeedId(s.song_id)}
                  >
                    🎵 {s.song_name}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </section>

      {/* ── Recommendations Grid ── */}
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
            <h3 className="catalog-empty-title">Computing vector similarities...</h3>
          </div>
        ) : recommendations.length === 0 ? (
          <div className="catalog-empty-card">
            <div className="empty-cylinder-icon">
              <svg viewBox="0 0 24 24">
                <ellipse cx="12" cy="5" rx="9" ry="3" />
                <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
                <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
              </svg>
            </div>
            <h3 className="catalog-empty-title">No recommendations computed</h3>
            <p className="catalog-empty-desc">
              Listen to tracks or add favorites to build your taste profile, or{" "}
              <button
                type="button"
                onClick={() => fetchRecommendations()}
                className="accent-theme-link"
              >
                refresh engine
              </button>
            </p>
          </div>
        ) : (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "18px" }}>
              <h2 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#fff" }}>
                {selectedSeedId ? "⚡ Track-Based Recommendations" : "✨ Personalized For You"} ({recommendations.length} Tracks)
              </h2>
            </div>

            <div className="songs-grid-wrapper">
              {recommendations.map((song) => (
                <SongCard key={song.song_id} song={song} />
              ))}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

"use client";

import React, { useEffect, useState } from "react";
import SongCard from "@/components/SongCard";
import { apiListSongs, apiRecommendations, Song, Recommendation } from "@/lib/api";

export default function RecommendationsPage() {
  const [allSongs, setAllSongs] = useState<Song[]>([]);
  const [selectedSeed, setSelectedSeed] = useState<string>("");
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [engineType, setEngineType] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [limit, setLimit] = useState(8);

  // Load a sample list of songs for the seed dropdown
  useEffect(() => {
    apiListSongs({ limit: 50 })
      .then((res) => setAllSongs(res.songs || []))
      .catch((err) => console.error("Failed to load catalog for seed selection:", err));
  }, []);

  // Fetch recommendations whenever selectedSeed or limit changes
  const fetchRecs = async (seedId?: string) => {
    setLoading(true);
    try {
      const res = await apiRecommendations(seedId || selectedSeed || undefined, limit);
      setRecommendations(res.recommendations || []);
      setEngineType(res.type || "Content-Based Filtering (TF-IDF + Audio Features)");
    } catch (err) {
      console.error("Error generating recommendations:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecs();
  }, [limit]);

  const handleSeedChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setSelectedSeed(val);
    fetchRecs(val);
  };

  return (
    <div className="recommendations-container">
      <header className="page-header">
        <h1 className="page-title">
          Recommendation <span className="gradient-text">Engine</span>
        </h1>
        <p className="page-subtitle">
          Select a seed track from the catalog to generate instant TF-IDF content-based recommendations, or let the system analyze your profile.
        </p>
      </header>

      {/* Control Box */}
      <div className="glass-card control-card">
        <div className="control-row">
          <div className="control-group flex-1">
            <label className="input-label">Select Seed Track:</label>
            <select
              value={selectedSeed}
              onChange={handleSeedChange}
              className="select-input"
            >
              <option value="">-- Personal / Default Profile Recommendations --</option>
              {allSongs.map((s) => (
                <option key={s.song_id} value={s.song_id}>
                  {s.song_name} — {s.artist} ({s.genre || "Music"})
                </option>
              ))}
            </select>
          </div>

          <div className="control-group">
            <label className="input-label">Count:</label>
            <select
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
              className="select-input"
            >
              <option value={4}>4 Songs</option>
              <option value={8}>8 Songs</option>
              <option value={12}>12 Songs</option>
            </select>
          </div>

          <div className="control-group self-end">
            <button className="btn btn-primary" onClick={() => fetchRecs()} disabled={loading}>
              ⚡ Refresh
            </button>
          </div>
        </div>

        {engineType && (
          <div className="engine-badge font-mono">
            <span>Algorithm:</span> <strong>{engineType}</strong>
          </div>
        )}
      </div>

      {/* Recommendations Grid */}
      {loading ? (
        <div className="loading-grid">
          {[...Array(limit)].map((_, i) => (
            <div key={i} className="skeleton-card" />
          ))}
        </div>
      ) : recommendations.length > 0 ? (
        <div className="song-grid">
          {recommendations.map((rec) => (
            <SongCard key={rec.song_id} song={rec} />
          ))}
        </div>
      ) : (
        <div className="empty-box">
          <p>No recommendations generated. Try selecting a different seed track.</p>
        </div>
      )}
    </div>
  );
}

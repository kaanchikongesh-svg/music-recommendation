"use client";

import React, { useState } from "react";
import { usePlayer } from "@/lib/usePlayer";
import { useAuth } from "@/lib/useAuth";
import { useTheme } from "@/lib/useTheme";
import { apiAddFavorite, apiRemoveFavorite, Song, Recommendation } from "@/lib/api";
import { Heart, Music, Sparkles } from "lucide-react";

interface SongCardProps {
  song: Song | Recommendation;
  isFav?: boolean;
  onFavToggle?: () => void;
  onViewDetails?: (song: Song | Recommendation) => void;
}

export default function SongCard({
  song,
  isFav: initialFav = false,
  onFavToggle,
  onViewDetails,
}: SongCardProps) {
  const { currentTrack, isPlaying, play, togglePlay } = usePlayer();
  const { user } = useAuth();
  const { visualTheme } = useTheme();
  const [isFav, setIsFav] = useState(initialFav);
  const [favLoading, setFavLoading] = useState(false);

  const songId = "song_id" in song ? song.song_id : (song as Song).song_id || "";
  const title = "song_name" in song ? song.song_name : "";
  const artist = song.artist || "Unknown Artist";
  const album = "album" in song && song.album && song.album.toLowerCase() !== "unknown" ? song.album : undefined;
  const year = "year" in song && song.year ? song.year : undefined;
  const genre = "genre" in song && song.genre && song.genre.toLowerCase() !== "unknown" ? song.genre : undefined;
  const language = "language" in song && song.language && song.language.toLowerCase() !== "unknown" ? song.language : undefined;
  const matchScore = "similarity_score" in song && typeof song.similarity_score === "number"
    ? song.similarity_score
    : "score" in song && typeof song.score === "number"
    ? song.score
    : undefined;
  const reason = "similarity_reason" in song && song.similarity_reason
    ? song.similarity_reason
    : "reason" in song && song.reason
    ? song.reason
    : undefined;

  const isCurrent = currentTrack?.song_id === songId;
  const is3D = visualTheme === "3d";

  const handlePlay = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (isCurrent) {
      togglePlay();
    } else {
      play({
        song_id: songId,
        song_name: title,
        artist: artist,
        genre: genre,
      });
    }
  };

  const handleFavorite = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!user || favLoading) return;
    setFavLoading(true);
    try {
      if (isFav) {
        await apiRemoveFavorite(songId);
        setIsFav(false);
      } else {
        await apiAddFavorite(songId);
        setIsFav(true);
      }
      onFavToggle?.();
    } catch (err) {
      console.error("Favorite toggle failed:", err);
    } finally {
      setFavLoading(false);
    }
  };

  return (
    <div
      className={`song-item-card ${is3D ? "song-card-3d" : ""} ${isCurrent ? "playing" : ""}`}
      style={{
        cursor: "pointer",
        position: "relative",
      }}
      onClick={() => onViewDetails ? onViewDetails(song) : handlePlay({ stopPropagation: () => {} } as React.MouseEvent)}
    >
      <div className="song-card-header">
        <div
          className={`song-cover-thumb ${is3D ? "artwork-3d" : ""}`}
          title={isCurrent && isPlaying ? "Pause preview" : "Play track"}
          onClick={handlePlay}
        >
          {isCurrent && isPlaying ? "⏸" : "▶"}
        </div>
        <div className="song-card-meta">
          <div className="song-title-text" title={title}>
            {title}
          </div>
          <div className="song-artist-text" title={artist}>
            {artist}
          </div>
          {(album || year) && (
            <div style={{ fontSize: "0.74rem", color: "var(--text-muted)", marginTop: 2, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
              {[year, album].filter(Boolean).join(" • ")}
            </div>
          )}
        </div>
      </div>

      <div className="song-tags-row" style={{ marginTop: 10 }}>
        <div style={{ display: "flex", gap: "6px", alignItems: "center", flexWrap: "wrap" }}>
          {language && (
            <span
              className="badge-tag"
              style={{
                background: language.toLowerCase() === "tamil" ? "var(--accent-soft)" : "rgba(255,255,255,0.06)",
                color: language.toLowerCase() === "tamil" ? "var(--accent-color)" : "#cbd5e1",
                borderColor: language.toLowerCase() === "tamil" ? "var(--accent-border)" : "transparent",
              }}
            >
              {language}
            </span>
          )}
          {genre && <span className="badge-tag accent">{genre}</span>}
          {matchScore !== undefined && (
            <span className="badge-tag" style={{ background: "rgba(16, 185, 129, 0.12)", color: "#10b981" }}>
              {(matchScore * 100).toFixed(0)}% Match
            </span>
          )}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 6, marginLeft: "auto" }}>
          {onViewDetails && (
            <button
              type="button"
              className="action-icon-btn"
              onClick={(e) => {
                e.stopPropagation();
                onViewDetails(song);
              }}
              title="View Song Details & Similar Recommendations"
            >
              <Sparkles size={14} style={{ color: "var(--accent-color)" }} />
            </button>
          )}

          {user && (
            <button
              type="button"
              className={`action-icon-btn ${isFav ? "active" : ""}`}
              onClick={handleFavorite}
              disabled={favLoading}
              title={isFav ? "Remove from Favorites" : "Add to Favorites"}
            >
              <Heart size={14} fill={isFav ? "var(--accent-color)" : "none"} />
            </button>
          )}
        </div>
      </div>

      {reason && (
        <div
          style={{
            marginTop: 8,
            fontSize: "0.72rem",
            color: "var(--text-muted)",
            display: "flex",
            alignItems: "center",
            gap: 4,
          }}
        >
          <Sparkles size={11} style={{ color: "var(--accent-color)" }} />
          <span>{reason}</span>
        </div>
      )}
    </div>
  );
}

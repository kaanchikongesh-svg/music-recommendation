"use client";

import React, { useState } from "react";
import { usePlayer } from "@/lib/usePlayer";
import { useAuth } from "@/lib/useAuth";
import { apiAddFavorite, apiRemoveFavorite, Song, Recommendation } from "@/lib/api";

interface SongCardProps {
  song: Song | Recommendation;
  isFav?: boolean;
  onFavToggle?: () => void;
}

export default function SongCard({ song, isFav: initialFav = false, onFavToggle }: SongCardProps) {
  const { currentTrack, isPlaying, play, togglePlay } = usePlayer();
  const { user } = useAuth();
  const [isFav, setIsFav] = useState(initialFav);
  const [favLoading, setFavLoading] = useState(false);

  const songId = "song_id" in song ? song.song_id : (song as Song).song_id || "";
  const title = "song_name" in song ? song.song_name : "";
  const artist = song.artist || "Unknown Artist";
  const genre = "genre" in song ? song.genre : undefined;

  const isCurrent = currentTrack?.song_id === songId;

  const handlePlay = () => {
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

  // Generate a deterministic gradient based on title for album art backdrop
  const hash = title.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const hue1 = hash % 360;
  const hue2 = (hue1 + 60) % 360;

  return (
    <div className={`song-card ${isCurrent ? "playing" : ""}`}>
      <div
        className="song-card-art"
        style={{
          background: `linear-gradient(135deg, hsl(${hue1}, 70%, 20%), hsl(${hue2}, 80%, 12%))`,
        }}
      >
        <div className="art-overlay">
          <button className="play-btn" onClick={handlePlay} title={isCurrent && isPlaying ? "Pause" : "Play"}>
            {isCurrent && isPlaying ? "⏸" : "▶"}
          </button>
        </div>

        {/* Music icon artwork */}
        <div className="art-icon">🎵</div>
      </div>

      <div className="song-card-info">
        <h4 className="song-title" title={title}>
          {title}
        </h4>
        <p className="song-artist">{artist}</p>

        <div className="song-card-footer">
          {genre && <span className="genre-badge">{genre}</span>}
          {"score" in song && song.score !== undefined && (
            <span className="match-badge">{(song.score * 100).toFixed(0)}% Match</span>
          )}

          {user && (
            <button
              className={`fav-btn ${isFav ? "active" : ""}`}
              onClick={handleFavorite}
              disabled={favLoading}
              title={isFav ? "Remove from Favorites" : "Add to Favorites"}
            >
              {isFav ? "♥" : "♡"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

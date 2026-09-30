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

  return (
    <div className={`song-item-card ${isCurrent ? "playing" : ""}`}>
      <div className="song-card-header">
        <div
          className="song-cover-thumb"
          onClick={handlePlay}
          title={isCurrent && isPlaying ? "Pause preview" : "Play preview"}
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
        </div>
      </div>

      <div className="song-tags-row">
        <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
          {genre && <span className="badge-tag accent">{genre}</span>}
          {"score" in song && song.score !== undefined && (
            <span className="badge-tag">{(song.score * 100).toFixed(0)}% Match</span>
          )}
        </div>

        {user && (
          <button
            className={`action-icon-btn ${isFav ? "active" : ""}`}
            onClick={handleFavorite}
            disabled={favLoading}
            title={isFav ? "Remove from Favorites" : "Add to Favorites"}
          >
            {isFav ? "♥" : "♡"}
          </button>
        )}
      </div>
    </div>
  );
}

"use client";

import React, { useEffect, useState } from "react";
import { Song, Recommendation, apiSeedRecommendations, apiAddFavorite, apiRemoveFavorite, apiPlaylists, apiAddToPlaylist, Playlist } from "@/lib/api";
import { useAuth } from "@/lib/useAuth";
import { usePlayer } from "@/lib/usePlayer";
import { Sparkles, Heart, Plus, Disc, Calendar, Globe, Music, X, ArrowRight } from "lucide-react";

interface SongDetailsModalProps {
  song: Song | Recommendation | null;
  onClose: () => void;
  onSelectSong?: (song: Song | Recommendation) => void;
}

export default function SongDetailsModal({ song, onClose, onSelectSong }: SongDetailsModalProps) {
  const { user } = useAuth();
  const { play } = usePlayer();
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loadingRecs, setLoadingRecs] = useState(false);
  const [languageMode, setLanguageMode] = useState<"same" | "any">("same");
  const [isFav, setIsFav] = useState(false);
  const [playlists, setPlaylists] = useState<Playlist[]>([]);
  const [showPlaylistPicker, setShowPlaylistPicker] = useState(false);
  const [playlistNotice, setPlaylistNotice] = useState("");

  useEffect(() => {
    if (!song) return;
    const songId = song.song_id;
    setLoadingRecs(true);
    apiSeedRecommendations(songId, 6, languageMode)
      .then((res) => {
        setRecommendations(res.recommendations || []);
      })
      .catch(() => setRecommendations([]))
      .finally(() => setLoadingRecs(false));
  }, [song, languageMode]);

  useEffect(() => {
    if (user) {
      apiPlaylists()
        .then((res) => setPlaylists(res.playlists || []))
        .catch(() => {});
    }
  }, [user]);

  if (!song) return null;

  const title = song.song_name;
  const artist = song.artist || "Unknown Artist";
  const album = "album" in song && song.album && song.album.toLowerCase() !== "unknown" ? song.album : undefined;
  const year = "year" in song && song.year ? song.year : undefined;
  const language = "language" in song && song.language && song.language.toLowerCase() !== "unknown" ? song.language : undefined;
  const genre = "genre" in song && song.genre && song.genre.toLowerCase() !== "unknown" ? song.genre : undefined;
  const lyrics = "lyrics" in song && song.lyrics ? song.lyrics : undefined;

  // Format lyrics preview (first 8 lines)
  const lyricsPreview = lyrics
    ? lyrics
        .split("\n")
        .filter((l) => l.trim().length > 0)
        .slice(0, 8)
        .join("\n")
    : null;

  const handleFavorite = async () => {
    if (!user) return;
    try {
      if (isFav) {
        await apiRemoveFavorite(song.song_id);
        setIsFav(false);
      } else {
        await apiAddFavorite(song.song_id);
        setIsFav(true);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleAddToPlaylist = async (playlistId: number) => {
    try {
      await apiAddToPlaylist(playlistId, song.song_id);
      setPlaylistNotice("Added to playlist!");
      setShowPlaylistPicker(false);
      setTimeout(() => setPlaylistNotice(""), 3000);
    } catch {
      setPlaylistNotice("Already in playlist or error.");
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 9999,
        background: "rgba(0, 0, 0, 0.75)",
        backdropFilter: "blur(8px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "20px",
      }}
      onClick={onClose}
    >
      <div
        className="song-card-3d"
        style={{
          width: "100%",
          maxWidth: 680,
          maxHeight: "90vh",
          overflowY: "auto",
          background: "linear-gradient(135deg, #131622 0%, #0d0f17 100%)",
          border: "1px solid var(--border-subtle)",
          borderRadius: "var(--radius-card)",
          padding: 28,
          boxShadow: "0 20px 50px rgba(0,0,0,0.8)",
          position: "relative",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          type="button"
          onClick={onClose}
          style={{
            position: "absolute",
            top: 18,
            right: 18,
            background: "rgba(255,255,255,0.06)",
            border: "none",
            borderRadius: "50%",
            width: 32,
            height: 32,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#94a3b8",
            cursor: "pointer",
          }}
        >
          <X size={18} />
        </button>

        {/* Header Metadata */}
        <div style={{ display: "flex", gap: 20, marginBottom: 24, alignItems: "flex-start" }}>
          <div
            className="artwork-3d"
            style={{
              width: 80,
              height: 80,
              borderRadius: 14,
              background: "linear-gradient(135deg, var(--accent-color) 0%, #0d0f17 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#fff",
              flexShrink: 0,
              boxShadow: "0 8px 24px var(--accent-glow)",
            }}
          >
            <Music size={36} />
          </div>

          <div style={{ flex: 1, minWidth: 0 }}>
            <h2
              style={{
                fontSize: "1.45rem",
                fontWeight: 800,
                color: "#fff",
                marginBottom: 6,
                wordBreak: "break-word",
              }}
            >
              {title}
            </h2>
            <div style={{ fontSize: "1rem", color: "var(--accent-color)", fontWeight: 600, marginBottom: 8 }}>
              {artist}
            </div>

            <div style={{ display: "flex", gap: 10, flexWrap: "wrap", fontSize: "0.82rem", color: "var(--text-secondary)" }}>
              {album && (
                <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                  <Disc size={13} />
                  <span>{album}</span>
                </div>
              )}
              {year && (
                <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                  <Calendar size={13} />
                  <span>{year}</span>
                </div>
              )}
              {language && (
                <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                  <Globe size={13} />
                  <span
                    style={{
                      background: language.toLowerCase() === "tamil" ? "var(--accent-soft)" : "rgba(255,255,255,0.06)",
                      color: language.toLowerCase() === "tamil" ? "var(--accent-color)" : "#cbd5e1",
                      padding: "1px 8px",
                      borderRadius: 6,
                      fontWeight: 700,
                    }}
                  >
                    {language}
                  </span>
                </div>
              )}
              {genre && (
                <span style={{ background: "rgba(255,255,255,0.06)", padding: "1px 8px", borderRadius: 6 }}>
                  {genre}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Action Controls */}
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 24, alignItems: "center" }}>
          <button
            type="button"
            className="btn-accent-theme"
            onClick={() => {
              play({
                song_id: song.song_id,
                song_name: title,
                artist: artist,
                genre: genre,
              });
            }}
          >
            ▶ Play Track
          </button>

          {user && (
            <>
              <button
                type="button"
                className={`filter-pill ${isFav ? "active" : ""}`}
                onClick={handleFavorite}
                style={{ display: "inline-flex", alignItems: "center", gap: 6 }}
              >
                <Heart size={14} fill={isFav ? "var(--accent-color)" : "none"} />
                <span>{isFav ? "Favorited" : "Favorite"}</span>
              </button>

              <div style={{ position: "relative" }}>
                <button
                  type="button"
                  className="filter-pill"
                  onClick={() => setShowPlaylistPicker(!showPlaylistPicker)}
                  style={{ display: "inline-flex", alignItems: "center", gap: 6 }}
                >
                  <Plus size={14} />
                  <span>Add to Playlist</span>
                </button>

                {showPlaylistPicker && (
                  <div
                    style={{
                      position: "absolute",
                      bottom: "100%",
                      left: 0,
                      marginBottom: 8,
                      background: "#1e293b",
                      border: "1px solid var(--border-subtle)",
                      borderRadius: "var(--radius-card)",
                      padding: 10,
                      minWidth: 180,
                      zIndex: 10,
                      boxShadow: "0 10px 25px rgba(0,0,0,0.5)",
                    }}
                  >
                    <div style={{ fontSize: "0.78rem", fontWeight: 700, color: "#94a3b8", marginBottom: 6 }}>
                      Select Playlist:
                    </div>
                    {playlists.length === 0 ? (
                      <div style={{ fontSize: "0.8rem", color: "#64748b" }}>No playlists created</div>
                    ) : (
                      playlists.map((p) => (
                        <button
                          key={p.id}
                          type="button"
                          onClick={() => handleAddToPlaylist(p.id)}
                          style={{
                            display: "block",
                            width: "100%",
                            textAlign: "left",
                            background: "transparent",
                            border: "none",
                            padding: "6px 8px",
                            borderRadius: 6,
                            color: "#fff",
                            fontSize: "0.85rem",
                            cursor: "pointer",
                          }}
                        >
                          🎵 {p.name}
                        </button>
                      ))
                    )}
                  </div>
                )}
              </div>
            </>
          )}

          {playlistNotice && (
            <span style={{ fontSize: "0.82rem", color: "var(--accent-color)", fontWeight: 600 }}>
              {playlistNotice}
            </span>
          )}
        </div>

        {/* Controlled Lyrics Preview (First 8 lines) */}
        {lyricsPreview && (
          <div
            style={{
              background: "rgba(255,255,255,0.02)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "var(--radius-card)",
              padding: "16px 20px",
              marginBottom: 24,
            }}
          >
            <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "var(--text-secondary)", marginBottom: 8, letterSpacing: "0.05em", textTransform: "uppercase" }}>
              Lyrics Excerpt Preview:
            </div>
            <pre
              style={{
                fontFamily: "inherit",
                fontSize: "0.88rem",
                color: "#cbd5e1",
                whiteSpace: "pre-wrap",
                lineHeight: 1.6,
                margin: 0,
              }}
            >
              {lyricsPreview}
            </pre>
          </div>
        )}

        {/* Similar Songs / Recommendations Section */}
        <div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <Sparkles size={16} style={{ color: "var(--accent-color)" }} />
              <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "#fff", margin: 0 }}>
                Similar Songs & More Like This
              </h3>
            </div>

            <div style={{ display: "inline-flex", background: "rgba(255,255,255,0.04)", borderRadius: 16, padding: 2, border: "1px solid rgba(255,255,255,0.08)" }}>
              <button
                type="button"
                style={{
                  background: languageMode === "same" ? "var(--accent-color)" : "transparent",
                  color: languageMode === "same" ? "#000" : "#94a3b8",
                  border: "none",
                  borderRadius: 14,
                  padding: "4px 10px",
                  fontSize: "0.75rem",
                  fontWeight: 700,
                  cursor: "pointer",
                }}
                onClick={() => setLanguageMode("same")}
              >
                Same Language
              </button>
              <button
                type="button"
                style={{
                  background: languageMode === "any" ? "var(--accent-color)" : "transparent",
                  color: languageMode === "any" ? "#000" : "#94a3b8",
                  border: "none",
                  borderRadius: 14,
                  padding: "4px 10px",
                  fontSize: "0.75rem",
                  fontWeight: 700,
                  cursor: "pointer",
                }}
                onClick={() => setLanguageMode("any")}
              >
                Any Language
              </button>
            </div>
          </div>

          {loadingRecs ? (
            <div style={{ padding: 20, textAlign: "center", color: "#64748b", fontSize: "0.85rem" }}>
              Computing lexical and acoustic similarities...
            </div>
          ) : recommendations.length === 0 ? (
            <div style={{ padding: 20, textAlign: "center", color: "#64748b", fontSize: "0.85rem" }}>
              No similar songs computed yet.
            </div>
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: 10 }}>
              {recommendations.map((rec) => (
                <div
                  key={rec.song_id}
                  onClick={() => {
                    if (onSelectSong) {
                      onSelectSong(rec);
                    }
                  }}
                  style={{
                    background: "rgba(255,255,255,0.03)",
                    border: "1px solid var(--border-subtle)",
                    borderRadius: 10,
                    padding: "10px 14px",
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = "rgba(255,255,255,0.07)";
                    e.currentTarget.style.borderColor = "var(--accent-color)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = "rgba(255,255,255,0.03)";
                    e.currentTarget.style.borderColor = "var(--border-subtle)";
                  }}
                >
                  <div style={{ fontWeight: 700, color: "#fff", fontSize: "0.88rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {rec.song_name}
                  </div>
                  <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)", marginTop: 2 }}>
                    {rec.artist}
                  </div>
                  {rec.similarity_reason && (
                    <div style={{ fontSize: "0.7rem", color: "var(--accent-color)", marginTop: 4, display: "flex", alignItems: "center", gap: 3 }}>
                      <Sparkles size={10} />
                      <span>{rec.similarity_reason}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

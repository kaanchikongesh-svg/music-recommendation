"use client";
import { usePlayer } from "@/lib/usePlayer";

export function PlayerDock() {
  const { currentTrack, isPlaying, togglePlay, stop } = usePlayer();

  if (!currentTrack) {
    return (
      <div className="player-dock">
        <div className="player-art">🎵</div>
        <div className="player-info">
          <div className="player-song" style={{ color: "var(--text-muted)" }}>No track selected</div>
          <div className="player-artist">Pick a song to start listening</div>
        </div>
        <div className="player-controls">
          <button className="player-btn" disabled>⏮</button>
          <button className="player-play" disabled style={{ opacity: 0.4 }}>▶</button>
          <button className="player-btn" disabled>⏭</button>
        </div>
        <div className="player-progress">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: "0%" }} />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="player-dock">
      <div className="player-art">🎵</div>
      <div className="player-info">
        <div className="player-song">{currentTrack.song_name}</div>
        <div className="player-artist">{currentTrack.artist}</div>
      </div>
      <div className="player-controls">
        <button className="player-btn">⏮</button>
        <button className="player-play" onClick={togglePlay}>
          {isPlaying ? "⏸" : "▶"}
        </button>
        <button className="player-btn">⏭</button>
      </div>
      <div className="player-progress">
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: isPlaying ? "45%" : "0%" }} />
        </div>
      </div>
      <button className="btn-icon" onClick={stop} title="Stop">✕</button>
    </div>
  );
}

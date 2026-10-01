"use client";

import React from "react";
import { usePlayer } from "@/lib/usePlayer";
import { useTheme } from "@/lib/useTheme";
import { Music, VolumeX, X, Disc } from "lucide-react";

export function PlayerDock() {
  const { currentTrack, stop } = usePlayer();
  const { visualTheme } = useTheme();

  const is3D = visualTheme === "3d";

  if (!currentTrack) {
    return null;
  }

  return (
    <div
      className="bottom-player-dock"
      style={{
        position: "fixed",
        bottom: 0,
        left: "var(--sidebar-width)",
        right: 0,
        height: 72,
        background: "rgba(8, 10, 16, 0.95)",
        backdropFilter: "blur(20px)",
        borderTop: "1px solid var(--border-card)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 28px",
        zIndex: 50,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <div
          style={{
            width: 44,
            height: 44,
            borderRadius: 10,
            background: "var(--accent-soft)",
            border: "1px solid var(--accent-border)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "var(--accent-color)",
          }}
          className={is3D ? "rotating-disc" : ""}
        >
          <Disc size={22} />
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: "0.92rem", color: "#fff" }}>
            {currentTrack.song_name}
          </div>
          <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
            {currentTrack.artist}
          </div>
        </div>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
            padding: "6px 14px",
            borderRadius: "var(--radius-pill)",
            background: "rgba(255, 255, 255, 0.04)",
            border: "1px solid var(--border-subtle)",
            color: "var(--text-muted)",
            fontSize: "0.8rem",
            fontWeight: 500,
          }}
        >
          <VolumeX size={14} />
          <span>Audio preview unavailable</span>
        </div>
      </div>

      <button
        type="button"
        onClick={stop}
        title="Dismiss"
        style={{
          width: 32,
          height: 32,
          borderRadius: "50%",
          background: "transparent",
          border: "1px solid var(--border-subtle)",
          color: "var(--text-secondary)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          cursor: "pointer",
        }}
      >
        <X size={16} />
      </button>
    </div>
  );
}

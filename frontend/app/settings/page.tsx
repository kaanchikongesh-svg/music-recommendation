"use client";

import React from "react";
import { useTheme } from "@/lib/useTheme";
import { Sparkles, Box, Eye, Layers, Palette, ShieldCheck, Zap } from "lucide-react";

export default function SettingsPage() {
  const { theme, setTheme, themes, visualTheme, setVisualTheme, motion, setMotion } = useTheme();

  return (
    <div className="section-container" style={{ maxWidth: 880 }}>
        <div style={{ marginBottom: 32 }}>
          <h1 className="section-title" style={{ fontSize: "2.2rem", marginBottom: 8 }}>
            Settings
          </h1>
          <p className="section-subtitle">
            Configure visual depth, motion preferences, and personalized aesthetic themes.
          </p>
        </div>

        {/* Visual Theme Mode (Classic vs 3D) */}
        <div
          className="song-card"
          style={{
            padding: 24,
            marginBottom: 24,
            display: "flex",
            flexDirection: "column",
            gap: 16,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <Box size={22} style={{ color: "var(--accent-color)" }} />
            <div>
              <h2 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#fff" }}>Visual Mode</h2>
              <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                Choose between minimal Classic and modern 3D spatial depth.
              </p>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <button
              type="button"
              onClick={() => setVisualTheme("classic")}
              style={{
                padding: "18px 20px",
                borderRadius: "var(--radius-card)",
                background: visualTheme === "classic" ? "var(--accent-soft)" : "rgba(255,255,255,0.03)",
                border:
                  visualTheme === "classic"
                    ? "2px solid var(--accent-color)"
                    : "1px solid var(--border-subtle)",
                color: "#fff",
                cursor: "pointer",
                textAlign: "left",
                display: "flex",
                flexDirection: "column",
                gap: 6,
                transition: "var(--transition)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <span style={{ fontWeight: 700, fontSize: "1rem" }}>Classic Mode</span>
                {visualTheme === "classic" && (
                  <span
                    style={{
                      background: "var(--accent-color)",
                      color: "#000",
                      fontSize: "0.7rem",
                      fontWeight: 800,
                      padding: "2px 8px",
                      borderRadius: 12,
                    }}
                  >
                    ACTIVE
                  </span>
                )}
              </div>
              <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                Ultra-fast, minimal, sleek dark-cinematic music discovery.
              </span>
            </button>

            <button
              type="button"
              onClick={() => setVisualTheme("3d")}
              style={{
                padding: "18px 20px",
                borderRadius: "var(--radius-card)",
                background: visualTheme === "3d" ? "var(--accent-soft)" : "rgba(255,255,255,0.03)",
                border:
                  visualTheme === "3d"
                    ? "2px solid var(--accent-color)"
                    : "1px solid var(--border-subtle)",
                color: "#fff",
                cursor: "pointer",
                textAlign: "left",
                display: "flex",
                flexDirection: "column",
                gap: 6,
                transition: "var(--transition)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <Sparkles size={16} style={{ color: "var(--accent-color)" }} />
                  <span style={{ fontWeight: 700, fontSize: "1rem" }}>3D Spatial Mode</span>
                </div>
                {visualTheme === "3d" && (
                  <span
                    style={{
                      background: "var(--accent-color)",
                      color: "#000",
                      fontSize: "0.7rem",
                      fontWeight: 800,
                      padding: "2px 8px",
                      borderRadius: 12,
                    }}
                  >
                    ACTIVE
                  </span>
                )}
              </div>
              <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                Card perspective, depth hover elevations, layered artwork and subtle ambient lighting.
              </span>
            </button>
          </div>
        </div>

        {/* Motion Preference */}
        <div
          className="song-card"
          style={{
            padding: 24,
            marginBottom: 24,
            display: "flex",
            flexDirection: "column",
            gap: 16,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <Zap size={22} style={{ color: "var(--accent-color)" }} />
            <div>
              <h2 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#fff" }}>Motion Preference</h2>
              <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                Adjust interface transitions and card elevations.
              </p>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <button
              type="button"
              onClick={() => setMotion("full")}
              style={{
                padding: "16px",
                borderRadius: "var(--radius-card)",
                background: motion === "full" ? "var(--accent-soft)" : "rgba(255,255,255,0.03)",
                border:
                  motion === "full"
                    ? "2px solid var(--accent-color)"
                    : "1px solid var(--border-subtle)",
                color: "#fff",
                cursor: "pointer",
                textAlign: "left",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <div style={{ fontWeight: 700 }}>Full Motion</div>
                <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>
                  Fluid micro-interactions & depth transitions
                </div>
              </div>
              {motion === "full" && <div style={{ width: 10, height: 10, borderRadius: "50%", background: "var(--accent-color)" }} />}
            </button>

            <button
              type="button"
              onClick={() => setMotion("reduced")}
              style={{
                padding: "16px",
                borderRadius: "var(--radius-card)",
                background: motion === "reduced" ? "var(--accent-soft)" : "rgba(255,255,255,0.03)",
                border:
                  motion === "reduced"
                    ? "2px solid var(--accent-color)"
                    : "1px solid var(--border-subtle)",
                color: "#fff",
                cursor: "pointer",
                textAlign: "left",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <div style={{ fontWeight: 700 }}>Reduced Motion</div>
                <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>
                  Instant transitions, zero parallax
                </div>
              </div>
              {motion === "reduced" && <div style={{ width: 10, height: 10, borderRadius: "50%", background: "var(--accent-color)" }} />}
            </button>
          </div>
        </div>

        {/* Accent Colors */}
        <div
          className="song-card"
          style={{
            padding: 24,
            display: "flex",
            flexDirection: "column",
            gap: 16,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <Palette size={22} style={{ color: "var(--accent-color)" }} />
            <div>
              <h2 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#fff" }}>Accent Glow</h2>
              <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                Choose your signature ambient highlight color.
              </p>
            </div>
          </div>

          <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
            {themes.map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => setTheme(t.id)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  padding: "10px 18px",
                  borderRadius: "var(--radius-pill)",
                  background: theme === t.id ? t.glow : "rgba(255,255,255,0.04)",
                  border: theme === t.id ? `2px solid ${t.color}` : "1px solid var(--border-subtle)",
                  color: "#fff",
                  fontWeight: 600,
                  fontSize: "0.88rem",
                  cursor: "pointer",
                  transition: "var(--transition)",
                }}
              >
                <div
                  style={{
                    width: 14,
                    height: 14,
                    borderRadius: "50%",
                    background: t.color,
                    boxShadow: theme === t.id ? `0 0 10px ${t.color}` : "none",
                  }}
                />
                {t.name}
              </button>
            ))}
          </div>
        </div>
      </div>
  );
}

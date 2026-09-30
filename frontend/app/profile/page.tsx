"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/useAuth";
import { useTheme } from "@/lib/useTheme";
import { apiFavorites, apiHistory, apiPlaylists } from "@/lib/api";

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const { theme, setTheme, themes } = useTheme();
  const [stats, setStats] = useState({
    favoritesCount: 0,
    historyCount: 0,
    playlistsCount: 0,
  });

  useEffect(() => {
    Promise.all([
      apiFavorites().catch(() => ({ favorites: [] })),
      apiHistory(100).catch(() => ({ history: [] })),
      apiPlaylists().catch(() => ({ playlists: [] })),
    ]).then(([favs, hist, pls]) => {
      setStats({
        favoritesCount: favs.favorites?.length || 0,
        historyCount: hist.history?.length || 0,
        playlistsCount: pls.playlists?.length || 0,
      });
    });
  }, [user]);

  return (
    <div className="profile-segment-view">
      {/* ── Hero Banner ── */}
      <section className="hero-card">
        <div className="hero-ambient-glow" />
        <div className="hero-inner">
          <h1 className="hero-brand-title">Profile</h1>
          <p className="hero-subtitle">
            Manage your account, theme preferences, and listening analytics.
          </p>

          <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
            {user ? (
              <button type="button" className="btn-secondary-pill" onClick={logout}>
                🚪 Sign Out
              </button>
            ) : (
              <Link href="/login" className="btn-accent-theme">
                🔑 Sign In / Register
              </Link>
            )}
          </div>
        </div>
      </section>

      {/* ── Profile Content ── */}
      <section className="catalog-section" style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
        {/* User Details & Stats Card */}
        <div className="content-wrapper-card">
          <div style={{ display: "flex", alignItems: "center", gap: "18px", marginBottom: "24px" }}>
            <div
              style={{
                width: "56px",
                height: "56px",
                borderRadius: "16px",
                background: "var(--accent-color)",
                color: "#000",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "1.5rem",
                fontWeight: 900,
              }}
            >
              {user ? user.username[0].toUpperCase() : "👤"}
            </div>
            <div>
              <h2 style={{ fontSize: "1.3rem", fontWeight: 800, color: "#fff" }}>
                {user ? user.username : "Guest Explorer"}
              </h2>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", fontFamily: "monospace" }}>
                {user?.email || "kongesh.pad.2024@spsce.ac.in"}
              </p>
            </div>
          </div>

          {/* Activity Metrics */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "16px" }}>
            <div style={{ background: "#090c15", padding: "18px", borderRadius: "14px", border: "1px solid #161b29" }}>
              <div style={{ color: "var(--text-muted)", fontSize: "0.78rem", fontWeight: 700, textTransform: "uppercase" }}>
                Favorited Tracks
              </div>
              <div style={{ fontSize: "1.8rem", fontWeight: 900, color: "#fff", marginTop: "4px" }}>
                {stats.favoritesCount}
              </div>
            </div>

            <div style={{ background: "#090c15", padding: "18px", borderRadius: "14px", border: "1px solid #161b29" }}>
              <div style={{ color: "var(--text-muted)", fontSize: "0.78rem", fontWeight: 700, textTransform: "uppercase" }}>
                Total Listens
              </div>
              <div style={{ fontSize: "1.8rem", fontWeight: 900, color: "#fff", marginTop: "4px" }}>
                {stats.historyCount}
              </div>
            </div>

            <div style={{ background: "#090c15", padding: "18px", borderRadius: "14px", border: "1px solid #161b29" }}>
              <div style={{ color: "var(--text-muted)", fontSize: "0.78rem", fontWeight: 700, textTransform: "uppercase" }}>
                Created Playlists
              </div>
              <div style={{ fontSize: "1.8rem", fontWeight: 900, color: "#fff", marginTop: "4px" }}>
                {stats.playlistsCount}
              </div>
            </div>
          </div>
        </div>

        {/* Theme Accent Customization Card */}
        <div className="content-wrapper-card">
          <h3 style={{ fontSize: "1.15rem", fontWeight: 800, color: "#fff", marginBottom: "8px" }}>
            🎨 Dashboard Theme Accents
          </h3>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", marginBottom: "20px" }}>
            Choose an accent color for buttons, ambient glowing vectors, active highlights, and controls across the app.
          </p>

          <div style={{ display: "flex", gap: "14px", flexWrap: "wrap" }}>
            {themes.map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => setTheme(t.id)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  padding: "10px 18px",
                  borderRadius: "12px",
                  background: theme === t.id ? "#151928" : "#090c15",
                  border: theme === t.id ? `2px solid ${t.color}` : "1px solid #161b29",
                  color: theme === t.id ? "#ffffff" : "#8b99aa",
                  cursor: "pointer",
                  fontWeight: theme === t.id ? 700 : 500,
                  transition: "all 0.2s ease",
                }}
              >
                <div
                  style={{
                    width: "14px",
                    height: "14px",
                    borderRadius: "50%",
                    backgroundColor: t.color,
                    boxShadow: theme === t.id ? `0 0 10px ${t.color}` : "none",
                  }}
                />
                <span>{t.name}</span>
              </button>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

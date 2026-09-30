"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { apiHistory, HistoryItem } from "@/lib/api";
import { useAuth } from "@/lib/useAuth";

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    setLoading(true);
    apiHistory(30)
      .then((res) => setHistory(res.history || []))
      .catch(() => setHistory([]))
      .finally(() => setLoading(false));
  }, [user]);

  return (
    <div className="history-segment-view">
      {/* ── Hero Banner ── */}
      <section className="hero-card">
        <div className="hero-ambient-glow" />
        <div className="hero-inner">
          <h1 className="hero-brand-title">History</h1>
          <p className="hero-subtitle">
            Timeline of your played tracks, sessions, and interactions.
          </p>

          <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
            <Link href="/discover" className="btn-accent-theme">
              🎧 Start Listening
            </Link>
          </div>
        </div>
      </section>

      {/* ── History List Section ── */}
      <section className="catalog-section">
        {loading ? (
          <div className="catalog-empty-card">
            <div className="empty-cylinder-icon">
              <svg viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="9" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
            </div>
            <h3 className="catalog-empty-title">Loading history...</h3>
          </div>
        ) : history.length === 0 ? (
          <div className="catalog-empty-card">
            <div className="empty-cylinder-icon">
              <svg viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="9" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
            </div>
            <h3 className="catalog-empty-title">No playback history</h3>
            <p className="catalog-empty-desc">
              Tracks you play will automatically appear here. Explore songs on{" "}
              <Link href="/discover" className="accent-theme-link">
                Discover
              </Link>
              .
            </p>
          </div>
        ) : (
          <div className="content-wrapper-card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
              <h2 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#fff" }}>
                Playback Timeline ({history.length} events)
              </h2>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {history.map((item, idx) => (
                <div
                  key={idx}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "14px 18px",
                    background: "#0a0d16",
                    border: "1px solid #161b29",
                    borderRadius: "12px",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
                    <div
                      style={{
                        width: "38px",
                        height: "38px",
                        borderRadius: "8px",
                        background: "var(--accent-soft)",
                        color: "var(--accent-color)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: "0.9rem",
                        fontWeight: 700,
                      }}
                    >
                      ▶
                    </div>
                    <div>
                      <div style={{ color: "#ffffff", fontWeight: 600, fontSize: "0.95rem" }}>
                        {item.song_name}
                      </div>
                      <div style={{ color: "var(--text-secondary)", fontSize: "0.82rem" }}>
                        {item.artist} {item.genre && `• ${item.genre}`}
                      </div>
                    </div>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <span className="badge-tag">{item.action}</span>
                    <span style={{ color: "var(--text-muted)", fontSize: "0.78rem", fontFamily: "monospace" }}>
                      {item.played_at ? new Date(item.played_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "Recently"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

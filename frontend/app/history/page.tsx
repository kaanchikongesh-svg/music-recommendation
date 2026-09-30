"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/useAuth";
import { apiHistory, HistoryItem } from "@/lib/api";

export default function HistoryPage() {
  const { user, loading: authLoading } = useAuth();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;
    apiHistory(30)
      .then((res) => setHistory(res.history || []))
      .catch((err) => console.error("Error loading history:", err))
      .finally(() => setLoading(false));
  }, [user]);

  if (authLoading) return <div className="p-8 text-center text-muted">Checking authentication...</div>;

  if (!user) {
    return (
      <div className="auth-required-box">
        <h2>🔒 Sign In Required</h2>
        <p>Please log in to track your listening history.</p>
        <Link href="/login" className="btn btn-primary mt-4">
          Sign In
        </Link>
      </div>
    );
  }

  return (
    <div className="history-container">
      <header className="page-header">
        <h1 className="page-title">
          Listening <span className="gradient-text">History</span>
        </h1>
        <p className="page-subtitle">Recently played tracks and recommendations interaction log.</p>
      </header>

      {loading ? (
        <div className="p-8 text-center text-muted">Loading history...</div>
      ) : history.length > 0 ? (
        <div className="history-list glass-card">
          <table className="history-table">
            <thead>
              <tr>
                <th>Song Title</th>
                <th>Artist</th>
                <th>Genre</th>
                <th>Played At</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item, idx) => (
                <tr key={idx}>
                  <td className="font-semibold text-white">{item.song_name}</td>
                  <td className="text-muted">{item.artist}</td>
                  <td>
                    {item.genre ? (
                      <span className="genre-badge">{item.genre}</span>
                    ) : (
                      <span className="text-muted">—</span>
                    )}
                  </td>
                  <td className="font-mono text-sm text-muted">
                    {new Date(item.played_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-box">
          <p>No listening history recorded yet. Start playing tracks from Discover or Recommendations!</p>
          <Link href="/discover" className="btn btn-secondary mt-4">
            Explore Music
          </Link>
        </div>
      )}
    </div>
  );
}

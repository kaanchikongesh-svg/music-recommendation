"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/useAuth";
import { apiPlaylists, apiCreatePlaylist, Playlist } from "@/lib/api";

export default function PlaylistsPage() {
  const { user, loading: authLoading } = useAuth();
  const [playlists, setPlaylists] = useState<Playlist[]>([]);
  const [loading, setLoading] = useState(true);

  // New playlist modal state
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState("");
  const [desc, setDesc] = useState("");
  const [creating, setCreating] = useState(false);

  const loadPlaylists = async () => {
    if (!user) return;
    setLoading(true);
    try {
      const res = await apiPlaylists();
      setPlaylists(res.playlists || []);
    } catch (err) {
      console.error("Error loading playlists:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) loadPlaylists();
  }, [user]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setCreating(true);
    try {
      await apiCreatePlaylist(name.trim(), desc.trim() || undefined);
      setName("");
      setDesc("");
      setShowModal(false);
      await loadPlaylists();
    } catch (err) {
      console.error("Create playlist error:", err);
    } finally {
      setCreating(false);
    }
  };

  if (authLoading) return <div className="p-8 text-center text-muted">Checking authentication...</div>;

  if (!user) {
    return (
      <div className="auth-required-box">
        <h2>🔒 Sign In Required</h2>
        <p>Please log in to build and manage custom playlists.</p>
        <Link href="/login" className="btn btn-primary mt-4">
          Sign In
        </Link>
      </div>
    );
  }

  return (
    <div className="playlists-container">
      <header className="page-header flex-between">
        <div>
          <h1 className="page-title">
            Your <span className="gradient-text">Playlists</span>
          </h1>
          <p className="page-subtitle">Organize tracks into custom collections.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          + Create Playlist
        </button>
      </header>

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content glass-card" onClick={(e) => e.stopPropagation()}>
            <h3 className="modal-title">Create New Playlist</h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="input-label">Playlist Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Late Night Vibes"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="search-input"
                />
              </div>
              <div>
                <label className="input-label">Description (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. Chill electronic and ambient tracks"
                  value={desc}
                  onChange={(e) => setDesc(e.target.value)}
                  className="search-input"
                />
              </div>
              <div className="flex-end space-x-3">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={creating}>
                  {creating ? "Creating..." : "Create"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading ? (
        <div className="loading-grid">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="skeleton-card" />
          ))}
        </div>
      ) : playlists.length > 0 ? (
        <div className="playlist-grid">
          {playlists.map((pl) => (
            <div key={pl.id} className="playlist-card glass-card">
              <div className="playlist-cover">🎶</div>
              <h3 className="playlist-name">{pl.name}</h3>
              {pl.description && <p className="playlist-desc">{pl.description}</p>}
              <div className="playlist-footer">
                <span className="text-muted text-sm">{pl.song_count ?? 0} tracks</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-box">
          <p>No playlists created yet. Click below to create your first collection!</p>
          <button className="btn btn-primary mt-4" onClick={() => setShowModal(true)}>
            + Create Playlist
          </button>
        </div>
      )}
    </div>
  );
}

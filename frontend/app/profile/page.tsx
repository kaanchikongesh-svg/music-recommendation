"use client";

import React from "react";
import Link from "next/link";
import { useAuth } from "@/lib/useAuth";

export default function ProfilePage() {
  const { user, loading, logout } = useAuth();

  if (loading) return <div className="p-8 text-center text-muted">Checking authentication...</div>;

  if (!user) {
    return (
      <div className="auth-required-box">
        <h2>🔒 Sign In Required</h2>
        <p>Please log in to view your user profile.</p>
        <Link href="/login" className="btn btn-primary mt-4">
          Sign In
        </Link>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <header className="page-header">
        <h1 className="page-title">
          User <span className="gradient-text">Profile</span>
        </h1>
        <p className="page-subtitle">Your personal account details and preferences.</p>
      </header>

      <div className="glass-card profile-card">
        <div className="profile-avatar font-mono">
          {user.username.slice(0, 2).toUpperCase()}
        </div>

        <div className="profile-details">
          <h2>{user.username}</h2>
          <p className="text-muted">{user.email || "No email linked"}</p>

          <div className="profile-badge-row mt-4">
            <span className="badge">User ID: #{user.id}</span>
            <span className="badge">Status: Active</span>
          </div>

          <div className="profile-actions mt-6 space-x-3">
            <button className="btn btn-secondary" onClick={logout}>
              Sign Out
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

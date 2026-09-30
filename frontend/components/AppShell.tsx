"use client";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/useAuth";
import { PlayerDock } from "@/components/PlayerDock";

const NAV_MAIN = [
  { href: "/", icon: "🏠", label: "Home" },
  { href: "/discover", icon: "🔎", label: "Discover" },
  { href: "/recommendations", icon: "✨", label: "Recommendations" },
];
const NAV_LIBRARY = [
  { href: "/favorites", icon: "❤️", label: "Favorites" },
  { href: "/history", icon: "📜", label: "History" },
  { href: "/playlists", icon: "🎵", label: "Playlists" },
];
const NAV_ACCOUNT = [
  { href: "/profile", icon: "👤", label: "Profile" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const isLoginPage = pathname === "/login" || pathname === "/register";
  if (isLoginPage) {
    return <>{children}</>;
  }

  return (
    <div className="app-shell">
      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-icon">🎵</div>
          <span className="logo-text">TuneSphere</span>
        </div>

        <nav className="nav-section">
          <div className="nav-section-label">Discover</div>
          {NAV_MAIN.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`nav-item ${pathname === item.href ? "active" : ""}`}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </Link>
          ))}

          <div className="nav-section-label">Library</div>
          {NAV_LIBRARY.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`nav-item ${pathname === item.href ? "active" : ""}`}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </Link>
          ))}

          <div className="nav-section-label">Account</div>
          {NAV_ACCOUNT.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`nav-item ${pathname === item.href ? "active" : ""}`}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </Link>
          ))}
          {user && (
            <button
              onClick={logout}
              className="nav-item"
              style={{ width: "100%", background: "none", border: "none", textAlign: "left", cursor: "pointer" }}
            >
              <span className="nav-icon">🚪</span>
              Logout
            </button>
          )}
        </nav>

        {/* User card */}
        <div className="sidebar-user">
          <div className="user-avatar">
            {user ? user.username[0].toUpperCase() : "?"}
          </div>
          <div className="user-info">
            <div className="user-name">{user?.username || "Guest"}</div>
            <div className="user-role">{user ? "Member" : "Not logged in"}</div>
          </div>
        </div>
      </aside>

      {/* ── Main content ── */}
      <main className="main-content">
        {children}
      </main>

      {/* ── Persistent player ── */}
      <PlayerDock />
    </div>
  );
}

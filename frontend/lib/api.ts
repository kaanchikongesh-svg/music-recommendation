const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined"
    ? ""
    : process.env.API_URL || "http://localhost:8000");

// ── Generic fetch helper ────────────────────────────────────────────────────

async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("ts_token") : null;

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "API request failed");
  }
  return res.json();
}

// ── Types ───────────────────────────────────────────────────────────────────

export interface Song {
  song_id: string;
  song_name: string;
  artist: string;
  album?: string;
  genre?: string;
  language?: string;
  year?: number;
  lyrics?: string;
  source_link?: string;
  similarity_score?: number;
  similarity_reason?: string;
  popularity?: number;
  danceability?: number;
  energy?: number;
  valence?: number;
  tempo?: number;
  acousticness?: number;
  instrumentalness?: number;
  speechiness?: number;
  loudness?: number;
}

export interface Recommendation {
  song_id: string;
  song_name: string;
  artist: string;
  album?: string;
  genre?: string;
  language?: string;
  year?: number;
  score?: number;
  similarity_score?: number;
  reason?: string;
  similarity_reason?: string;
}

export interface User {
  id: number;
  username: string;
  email?: string;
  created_at?: string;
}

export interface AuthResponse {
  token: string;
  user: User;
  message: string;
}

export interface SongsPage {
  songs: Song[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface Playlist {
  id: number;
  name: string;
  description?: string;
  created_at?: string;
  song_count?: number;
}

export interface HistoryItem {
  song_name: string;
  artist: string;
  genre?: string;
  action: string;
  played_at: string;
}

// ── Health ──────────────────────────────────────────────────────────────────

export const apiHealth = () =>
  apiFetch<{ status: string; app: string; version: string }>("/api/health");

// ── Auth ────────────────────────────────────────────────────────────────────

export const apiRegister = (username: string, password: string, email?: string) =>
  apiFetch<AuthResponse>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ username, password, email }),
  });

export const apiLogin = (username: string, password: string) =>
  apiFetch<AuthResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });

export const apiLogout = () =>
  apiFetch<{ status: string }>("/api/auth/logout", { method: "POST" });

export const apiMe = () => apiFetch<User>("/api/auth/me");

// ── Songs ───────────────────────────────────────────────────────────────────

export const apiListSongs = (params?: {
  query?: string;
  genre?: string;
  artist?: string;
  language?: string;
  page?: number;
  limit?: number;
}) => {
  const q = new URLSearchParams();
  if (params?.query) q.set("query", params.query);
  if (params?.genre) q.set("genre", params.genre);
  if (params?.artist) q.set("artist", params.artist);
  if (params?.language) q.set("language", params.language);
  if (params?.page) q.set("page", String(params.page));
  if (params?.limit) q.set("limit", String(params.limit));
  return apiFetch<SongsPage>(`/api/songs?${q.toString()}`);
};

export const apiSearchSongs = (q: string, limit = 20) =>
  apiFetch<{ results: Song[]; total: number }>(
    `/api/search?q=${encodeURIComponent(q)}&limit=${limit}`
  );

export const apiGetSong = (songId: string) =>
  apiFetch<{ song: Song; audio_features: Record<string, number> }>(
    `/api/songs/${songId}`
  );

export const apiGenres = () =>
  apiFetch<{ genres: string[] }>("/api/genres");

export const apiLanguages = () =>
  apiFetch<{ languages: string[] }>("/api/languages");

export const apiTamilSongs = (
  pageOrParams: number | { page?: number; limit?: number; query?: string; artist?: string } = 1,
  limit = 24
) => {
  const q = new URLSearchParams();
  if (typeof pageOrParams === "object") {
    if (pageOrParams.page) q.set("page", String(pageOrParams.page));
    if (pageOrParams.limit) q.set("limit", String(pageOrParams.limit));
    if (pageOrParams.query) q.set("query", pageOrParams.query);
    if (pageOrParams.artist) q.set("artist", pageOrParams.artist);
  } else {
    q.set("page", String(pageOrParams));
    q.set("limit", String(limit));
  }
  return apiFetch<SongsPage>(`/api/tamil?${q.toString()}`);
};

export const apiFeatured = (limit = 6) =>
  apiFetch<{ featured: Song[] }>(`/api/featured?limit=${limit}`);

export const apiCatalogStats = () =>
  apiFetch<Record<string, unknown>>("/api/stats");

// ── Recommendations ─────────────────────────────────────────────────────────

export const apiRecommendations = (
  songId?: string,
  limit = 6,
  languageMode: "same" | "any" = "same"
) => {
  const q = new URLSearchParams({
    limit: String(limit),
    language_mode: languageMode,
  });
  if (songId) q.set("song_id", songId);
  return apiFetch<{ recommendations: Recommendation[]; type: string; language_mode?: string }>(
    `/api/recommendations?${q.toString()}`
  );
};

export const apiSeedRecommendations = (
  songId: string,
  limit = 6,
  languageMode: "same" | "any" = "same"
) =>
  apiFetch<{ recommendations: Recommendation[]; language_mode?: string }>(
    `/api/recommendations/seed/${songId}?limit=${limit}&language_mode=${languageMode}`
  );

// ── Favorites ───────────────────────────────────────────────────────────────

export const apiFavorites = () =>
  apiFetch<{ favorites: Song[] }>("/api/favorites");

export const apiAddFavorite = (songId: string) =>
  apiFetch<{ status: string }>("/api/favorites", {
    method: "POST",
    body: JSON.stringify({ song_id: songId }),
  });

export const apiRemoveFavorite = (songId: string) =>
  apiFetch<{ status: string }>(`/api/favorites/${songId}`, {
    method: "DELETE",
  });

// ── History ─────────────────────────────────────────────────────────────────

export const apiHistory = (limit = 20) =>
  apiFetch<{ history: HistoryItem[] }>(`/api/history?limit=${limit}`);

export const apiLogPlay = (songId: string) =>
  apiFetch<{ status: string }>("/api/history", {
    method: "POST",
    body: JSON.stringify({ song_id: songId, action: "played" }),
  });

// ── Playlists ────────────────────────────────────────────────────────────────

export const apiPlaylists = () =>
  apiFetch<{ playlists: Playlist[] }>("/api/playlists");

export const apiCreatePlaylist = (name: string, description?: string) =>
  apiFetch<{ playlist: Playlist }>("/api/playlists", {
    method: "POST",
    body: JSON.stringify({ name, description }),
  });

export const apiPlaylistSongs = (playlistId: number) =>
  apiFetch<{ songs: Song[] }>(`/api/playlists/${playlistId}/songs`);

export const apiAddToPlaylist = (playlistId: number, songId: string) =>
  apiFetch<{ status: string }>(`/api/playlists/${playlistId}/songs`, {
    method: "POST",
    body: JSON.stringify({ song_id: songId }),
  });

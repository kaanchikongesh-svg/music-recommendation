# 🎵 TuneSphere AI Sound — Next.js Frontend
> **Engineered with Antigravity AI**  
> Modern Dark-Cinematic Music Dashboard built with Next.js 16 (App Router), React 19, TypeScript, and Vanilla CSS.

---

## Overview

The TuneSphere frontend provides a high-performance music discovery experience:
- **Dark-Cinematic Design System**: Glassmorphism cards, glowing violet/electric-blue gradients, responsive layouts.
- **Audio Preview Dock**: Persistent bottom music player with smooth play/pause, seek timeline, and volume controls.
- **AI Recommendation Interface**: Seed-track recommendations with similarity score badges and reasoning.
- **Search & Multi-Filter Catalog**: Real-time debounce search, genre tags, and audio feature radar metrics.
- **Library Management**: User playlists studio, favorited tracks, and playback history analytics.
- **JWT Authentication**: User login and registration with stored session state.

---

## Getting Started

### 1. Install Dependencies
```bash
npm install
```

### 2. Run Development Server
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) with your browser.

### 3. Build for Production
```bash
npm run build
npm start
```

---

## API Connection

The frontend connects to the FastAPI backend via `/api/...` routes configured in `lib/api.ts`. In local development, ensure the backend is running on `http://localhost:8000`. On Vercel, requests to `/api/*` are routed automatically to the backend service.

---

## Credits

Engineered with **Antigravity AI** by [kaanchikongesh-svg](https://github.com/kaanchikongesh-svg).

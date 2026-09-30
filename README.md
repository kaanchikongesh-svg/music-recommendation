# 🎵 TuneSphere AI Sound — Music Recommendation System
> **Engineered with Antigravity AI**  
> Full-Stack AI-Powered Music Discovery, Content-Based Recommendation Engine, and Dark-Cinematic Web Dashboard.

---

## 1. Project Overview

**TuneSphere AI Sound** is a production-grade, full-stack music recommendation platform that combines Machine Learning (TF-IDF vectorization & Cosine Similarity) with a modern dark-cinematic web interface and scalable FastAPI backend.

Key Capabilities:
- **AI Content-Based Recommendation**: Combines multi-attribute track metadata (title, artist, album, genre, language) with acoustic audio profiles (danceability, energy, valence, tempo, acousticness).
- **Personalized Taste Modeling**: Constructs dynamic taste centroid vectors from user listening history, favorites, and playlists to discover tailored recommendations while filtering out duplicates.
- **Dual Presentation Layers**:
  1. **Next.js 16 Web Dashboard** (`frontend/`): Production React 19 UI with fluid audio preview playback, dynamic search, multi-factor filtering, playlist management, and user authentication.
  2. **Streamlit Discovery App** (`frontend_streamlit/` & `app.py`): Interactive exploration dashboard for research, dataset analysis, and real-time radar charts.
- **FastAPI REST API Backend** (`backend/`): High-performance RESTful API endpoints for catalog discovery, user auth (JWT / PBKDF2), playlists, history, and ML inferences.
- **Kaggle Dataset Ingestion & Validation**: Flexible schema adapter supporting Spotify 114k Tracks, Spotify 1.2M+ Tracks, and external music CSV datasets.

---

## 2. System Architecture

```text
                                  USER BROWSER / CLIENT
                                            │
                                            ▼
                       ┌─────────────────────────────────────────┐
                       │          VERCEL SERVICES / GATEWAY      │
                       │   /       ───► Next.js Frontend         │
                       │   /api/*  ───► FastAPI Backend          │
                       └────────────────────┬────────────────────┘
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    ▼                                               ▼
      ┌───────────────────────────┐                   ┌───────────────────────────┐
      │     NEXT.JS FRONTEND      │                   │      FASTAPI BACKEND      │
      │  - React 19 + TypeScript  │                   │  - REST API Routing       │
      │  - Dark-Cinematic Design  │  ◄─── REST ─────► │  - JWT & Password Hashing │
      │  - Persistent Audio Player│      JSON API     │  - Services Orchestrator  │
      │  - Playlist & Taste Studio│                   │  - TF-IDF ML Engine       │
      └───────────────────────────┘                   └─────────────┬─────────────┘
                                                                    │
                                                ┌───────────────────┼───────────────────┐
                                                ▼                   ▼                   ▼
                                      ┌───────────────────┐ ┌───────────────┐ ┌───────────────────┐
                                      │  SQLITE DATABASE  │ │  ML ENGINE    │ │   DATA PIPELINE   │
                                      │  - Users & Auth   │ │ - TF-IDF      │ │  - Schema Adapter │
                                      │  - Playlists      │ │ - Cosine Sim  │ │  - Validator      │
                                      │  - History & Likes│ │ - Audio Blend │ │  - Preprocessor   │
                                      │  - Repository     │ │ - Personalize │ │  - Caching Loader │
                                      └───────────────────┘ └───────────────┘ └───────────────────┘
```

---

## 3. Directory Structure

```text
music-recommendation-system/
│
├── frontend/                   # Next.js 16 Web Dashboard (Production UI)
│   ├── app/                    # Next.js App Router pages
│   │   ├── page.tsx            # Home dashboard & featured tracks
│   │   ├── discover/           # Catalog search & genre filtering
│   │   ├── recommendations/    # AI seed & personalized recommendations
│   │   ├── favorites/          # Liked tracks collection
│   │   ├── history/            # Listening history & playback logs
│   │   ├── playlists/          # Custom playlist studio
│   │   ├── login/ & register/  # User authentication pages
│   │   └── profile/            # User activity & taste analytics
│   ├── components/             # Reusable UI components (SongCard, PlayerDock, AppShell)
│   ├── lib/                    # API client, auth context, and player hooks
│   └── package.json            # Node.js dependencies
│
├── backend/                    # Core business logic & FastAPI REST API
│   ├── main.py                 # FastAPI application instance & router mounts
│   ├── api/                    # REST API endpoint modules
│   │   ├── auth.py             # Login, register, current user endpoints
│   │   ├── songs.py            # Search, genres, featured, track details
│   │   ├── recommendations.py  # Seed & personalized recommendation endpoints
│   │   ├── favorites.py        # Add, remove, list favorites
│   │   ├── history.py          # Log playback, fetch listening history
│   │   ├── playlists.py        # Playlist CRUD operations
│   │   └── users.py            # User profile and stats
│   ├── recommendation/         # Scikit-Learn TF-IDF Machine Learning Engine
│   │   ├── content_based.py    # TF-IDF vectorizer + Cosine Similarity
│   │   ├── ranking.py          # Candidate filtering & deduplication
│   │   └── engine.py           # Unified model facade & serialization
│   ├── data/                   # Data ingestion, schema mapping & normalization
│   │   ├── adapter.py          # Kaggle column mapper & aliases resolver
│   │   ├── validator.py        # Schema constraint & audio bounds checker
│   │   ├── loader.py           # CSV loader & caching mechanism
│   │   └── preprocessing.py    # Text feature engineering & normalization
│   ├── database/               # SQLite persistence layer
│   │   ├── connection.py       # Thread-safe connection & schema init
│   │   ├── models.py           # Dataclasses (User, Song, Playlist, History)
│   │   └── repository.py       # Parameterized SQL queries
│   ├── auth/                   # Authentication & security utilities
│   │   ├── password.py         # PBKDF2-HMAC-SHA256 password hashing
│   │   ├── authentication.py   # User registration & verification
│   │   └── jwt_utils.py        # JWT token generation & validation
│   └── requirements.txt        # Production backend Python dependencies
│
├── frontend_streamlit/         # Streamlit Interactive Discovery App
│   ├── theme.py                # Dark theme styling & glassmorphism
│   ├── cards.py                # Song & recommendation cards
│   ├── components.py           # Plotly radar charts & upload widgets
│   └── pages/                  # Streamlit view controllers
│
├── data/                       # Dataset storage
│   ├── raw/songs.csv           # Canonical input dataset
│   └── processed/              # Preprocessed dataset with combined features
│
├── models/                     # Serialized ML models
│   └── content_recommender.pkl # Serialized TF-IDF vectorizer & feature matrices
│
├── tests/                      # Automated test suite (41/41 tests passing)
│   ├── test_adapter.py         # Kaggle schema adapter tests
│   ├── test_auth.py            # Password hashing & JWT auth tests
│   ├── test_data_loader.py     # CSV loading & validation tests
│   ├── test_database.py        # SQLite repository tests
│   ├── test_preprocessing.py   # Feature pipeline transformation tests
│   ├── test_recommendation.py  # ML engine & ranking tests
│   ├── test_services.py        # Service orchestrator tests
│   └── test_ui_states.py       # Empty states & UI lifecycle tests
│
├── vercel.json                 # Vercel Services configuration
├── .vercelignore               # Serverless bundle optimization rules
├── requirements.txt            # Root production Python dependencies
├── requirements-streamlit.txt  # Streamlit local development dependencies
└── README.md                   # System documentation
```

---

## 4. Machine Learning Recommendation Algorithm

### 1. Unified Feature Preprocessing
The preprocessing pipeline engineers a comprehensive text representation for every song:
$$\text{combined\_features} = \text{song\_name} \oplus \text{artist} \oplus \text{album} \oplus \text{genre} \oplus \text{language}$$

### 2. TF-IDF Tokenization & Cosine Similarity
- Text features are tokenized with sublinear term frequency weighting across unigrams and bigrams.
- Pairwise cosine similarity is computed between query vectors $\vec{q}$ and the library catalog matrix $M$:
$$\text{Sim}_{\text{text}}(q, s) = \frac{\vec{q} \cdot \vec{s}}{\|\vec{q}\| \|\vec{s}\|}$$

### 3. Acoustic Audio Blending
When numeric audio features (`danceability`, `energy`, `valence`, `tempo`, `acousticness`, `instrumentalness`, `speechiness`) are present:
$$\text{Sim}_{\text{total}}(q, s) = 0.75 \times \text{Sim}_{\text{text}}(q, s) + 0.25 \times \text{Sim}_{\text{audio}}(q, s)$$

### 4. User Preference Personalization
Personalized recommendations are calculated dynamically:
- Seed tracks from user favorites and listening history are aggregated.
- A user preference centroid vector $\vec{u}_{\text{centroid}} = \frac{1}{|S|} \sum_{s \in S} \vec{s}$ is calculated.
- Top candidate songs matching the centroid are ranked, automatically excluding songs already in the user's history.

---

## 5. Getting Started & Local Development

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Clone the Repository
```bash
git clone https://github.com/kaanchikongesh-svg/tunesphere-ai-sound.git
cd tunesphere-ai-sound
```

### 2. Set Up Backend
```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate  # macOS / Linux

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Start FastAPI backend
uvicorn backend.main:app --reload --port 8000
```
Backend API will run at `http://localhost:8000` (Swagger docs at `http://localhost:8000/docs`).

### 3. Set Up Next.js Frontend
```bash
cd frontend
npm install
npm run dev
```
Open your browser at `http://localhost:3000`.

### 4. Run Streamlit App (Optional)
```bash
pip install -r requirements-streamlit.txt
python -m streamlit run app.py
```

---

## 6. Automated Testing

Run the full automated test suite:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```
All **41/41 unit and integration tests** pass across data loading, Kaggle adapter, preprocessing, SQLite repository, auth, and ML recommendation logic.

---

## 7. Deployment (Vercel)

The application is configured to deploy as a unified **Vercel Services** application:
- `/` routes to the Next.js frontend (`frontend/`)
- `/api/*` routes to the FastAPI backend (`backend/` with entrypoint `main:app`)

To deploy, connect the GitHub repository to Vercel or run `vercel deploy`.

---

## 8. Credits

Built and designed with **Antigravity AI** by [kaanchikongesh-svg](https://github.com/kaanchikongesh-svg).

# 🎵 SoundWave — Music Recommendation System

A modern, full-stack **Music Recommendation System** built with **Streamlit**, **Scikit-Learn**, and **SQLite**, featuring a decoupled Frontend/Backend architecture, Content-Based Filtering with TF-IDF and Cosine Similarity, audio feature blending, user taste personalization, playlist management, and secure user authentication.

---

## 1. Project Overview

The **SoundWave Music Recommendation System** delivers personalized track recommendations by combining:
- **Metadata Similarity**: Analysis of track titles, artists, albums, genres, and languages using TF-IDF tokenization and Cosine Similarity.
- **Acoustic Audio Profiles**: Blending normalized numeric audio features (`danceability`, `energy`, `valence`, `tempo`, `acousticness`, `instrumentalness`, `speechiness`) when available in the dataset.
- **User Preference Personalization**: User taste centroid vectors constructed dynamically from listening history and favorited tracks.
- **Interactive Dashboard**: Modern dark-themed user interface with real-time audio radar charts, search filters, and playlist controls.

---

## 2. System Architecture

The application is structured into a clean logical separation between **Frontend** presentation and **Backend** domain services, data pipelines, recommendation algorithms, and SQLite persistence.

```text
                           USER
                            │
                            ▼
              ┌───────────────────────────┐
              │     STREAMLIT FRONTEND    │
              │  - Theme & Glassmorphism  │
              │  - Pages (Home/Discover)  │
              │  - Cards, Modals & Radars │
              └─────────────┬─────────────┘
                            │
                            ▼
              ┌───────────────────────────┐
              │      BACKEND SERVICES     │
              │  - Music Catalog Service  │
              │  - User Analytics Service │
              │  - Playlist & History     │
              │  - Authentication Service │
              └─────────────┬─────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
  │ SQLITE DB     │ │  ML ENGINE    │ │  DATA LAYER   │
  │ - Users       │ │ - TF-IDF      │ │ - Adapter     │
  │ - History     │ │ - Cosine Sim  │ │ - Validator   │
  │ - Playlists   │ │ - Audio Blend │ │ - Preprocess  │
  │ - Likes       │ │ - Ranking     │ │ - Loader      │
  └───────────────┘ └───────────────┘ └───────────────┘
```

---

## 3. Directory Structure

```text
music-recommendation-system/
│
├── app.py                      # Main Streamlit application entrypoint & router
│
├── frontend/                   # UI presentation layer
│   ├── __init__.py
│   ├── theme.py                # Dark theme styling, glassmorphism, responsive CSS
│   ├── components.py           # Hero, metrics, Plotly radar chart, uploader
│   ├── navbar.py               # Top breadcrumbs and status bar
│   ├── sidebar.py              # Navigation sidebar and session badge
│   ├── cards.py                # Song cards, recommendation cards, details modal
│   ├── empty_states.py         # Standardized empty state containers
│   └── pages/                  # Page view controllers
│       ├── __init__.py
│       ├── home.py             # Hero, library metrics, genres, featured tracks
│       ├── discover.py         # Full-text search and multi-factor filtering
│       ├── recommendations.py  # Seed-track engine & personalized recommendations
│       ├── favorites.py        # Liked songs collection
│       ├── history.py          # Chronological listening timeline
│       ├── playlists.py        # Custom user playlists manager
│       ├── profile.py          # User activity stats & taste analytics
│       └── login.py            # Secure authentication & registration
│
├── backend/                    # Core business logic & data pipeline
│   ├── __init__.py
│   │
│   ├── data/                   # Data ingestion, validation & preprocessing
│   │   ├── __init__.py
│   │   ├── adapter.py          # Kaggle dataset column mapper and adapter
│   │   ├── validator.py        # Schema integrity and constraint checker
│   │   ├── loader.py           # CSV loading, caching, upload persistence
│   │   └── preprocessing.py    # Text cleaning, normalization, audio bounds
│   │
│   ├── recommendation/         # Machine learning recommendation engine
│   │   ├── __init__.py
│   │   ├── content_based.py    # TF-IDF vectorizer + Cosine Similarity model
│   │   ├── ranking.py          # Candidate deduplication, exclusion, ranking
│   │   └── engine.py           # Unified recommendation facade & serialization
│   │
│   ├── database/               # SQLite persistence layer
│   │   ├── __init__.py
│   │   ├── connection.py       # Thread-safe SQLite connection & schema initialization
│   │   ├── models.py           # Entity dataclasses
│   │   └── repository.py       # Parameterized SQL repository queries
│   │
│   ├── auth/                   # Authentication & security
│   │   ├── __init__.py
│   │   ├── password.py         # PBKDF2-HMAC-SHA256 password hashing
│   │   └── authentication.py   # Register, login, session validation
│   │
│   └── services/               # Application service orchestrators
│       ├── __init__.py
│       ├── music_service.py    # Catalog querying and filtering
│       ├── user_service.py     # User registration and profile analytics
│       ├── playlist_service.py # Playlist CRUD operations
│       └── history_service.py  # Interaction logging and favorites
│
├── data/                       # Data storage
│   ├── raw/
│   │   └── songs.csv           # Raw canonical music dataset
│   └── processed/
│       └── songs_processed.csv # Cleaned dataset with combined_features
│
├── models/                     # Serialized ML artifacts
│   └── content_recommender.pkl # Serialized TF-IDF vectorizer & feature matrices
│
├── database/                   # Database files
│   └── music.db                # SQLite database
│
├── tests/                      # Automated unit test suite
│   ├── test_data_loader.py     # Loader & CSV tests
│   ├── test_preprocessing.py   # Pipeline transformation tests
│   ├── test_database.py        # Database operations tests
│   ├── test_adapter.py         # Kaggle adapter tests
│   ├── test_auth.py            # Password hashing & auth tests
│   ├── test_recommendation.py  # ML recommendation & ranking tests
│   ├── test_services.py        # Service layer tests
│   └── test_ui_states.py       # Empty state & validation tests
│
├── .streamlit/
│   └── config.toml             # Streamlit server and theme configuration
│
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git exclusion rules
└── README.md                   # System documentation
```

---

## 4. Kaggle Dataset Integration

### Recommended Dataset
- **Dataset**: Spotify 114k Tracks Dataset (`maharshipandya/spotify-tracks-dataset`) or Spotify 1.2M+ Tracks.
- **Link**: [Spotify Tracks Dataset on Kaggle](https://www.kaggle.com/datasets/maharshipandya/spotify-tracks-dataset)

### Dataset Schema & Adapter
The `backend.data.adapter` module dynamically maps diverse Kaggle dataset columns to the canonical schema:

| Canonical Field | Kaggle Source Aliases | Description | Fallback Strategy |
|---|---|---|---|
| `song_id` | `track_id`, `id`, `spotify_id`, `uri` | Unique track identifier | Sequential identifier |
| `song_name` | `track_name`, `title`, `name` | Song title | Required |
| `artist` | `artists`, `artist_name`, `performer` | Artist / band name | Required (list strings cleaned) |
| `album` | `album_name`, `album`, `release` | Album title | `"Unknown"` |
| `genre` | `track_genre`, `genre`, `genres` | Music category/genre | `"Unknown"` |
| `language` | `language`, `lang`, `locale` | Language code / name | `"Unknown"` (no fabrication) |
| `year` | `year`, `release_year`, `release_date` | 4-digit release year | Extracted from date / nullable |
| Audio Features | `danceability`, `energy`, `valence`, `tempo`, etc. | Acoustic numeric features | Clamped to bounds / optional |

### Dataset Setup Instructions

#### Option A: Upload Through Web UI
1. Start the application: `streamlit run app.py`
2. Navigate to **⚙️ Settings / Dataset** or use the uploader on the **🏠 Home** page.
3. Upload your CSV file. The built-in adapter will automatically normalize columns and save it to `data/raw/songs.csv`.

#### Option B: Kaggle API CLI
If your Kaggle API key (`~/.kaggle/kaggle.json` or `KAGGLE_USERNAME` / `KAGGLE_KEY`) is configured:
```bash
kaggle datasets download -d maharshipandya/spotify-tracks-dataset -p data/raw --unzip
```
Rename the downloaded CSV to `data/raw/songs.csv`.

> **Note**: If Kaggle API credentials are not set up on the host machine, manual download from the Kaggle URL above is required.

---

## 5. Machine Learning Recommendation Algorithm

### 1. Feature Preprocessing
The `backend.data.preprocessing` pipeline creates a unified text representation:
$$\text{combined\_features} = \text{song\_name} \oplus \text{artist} \oplus \text{album} \oplus \text{genre} \oplus \text{language}$$

### 2. TF-IDF & Cosine Similarity
- Text features are tokenized using `TfidfVectorizer` (sublinear term frequency, unigrams & bigrams).
- Pairwise cosine similarity is computed between query feature vector $\vec{q}$ and library matrix $M$:
$$\text{Sim}_{\text{text}}(q, s) = \frac{\vec{q} \cdot \vec{s}}{\|\vec{q}\| \|\vec{s}\|}$$

### 3. Audio Feature Blending
When numeric audio features are present, audio vectors are normalized with `MinMaxScaler` and blended:
$$\text{Sim}_{\text{total}}(q, s) = 0.75 \times \text{Sim}_{\text{text}}(q, s) + 0.25 \times \text{Sim}_{\text{audio}}(q, s)$$

### 4. User Profile Personalization
When generating personalized recommendations for a user:
- Seed songs from user's favorites and recent listening history are retrieved.
- A user preference centroid vector $\vec{u}_{\text{centroid}} = \frac{1}{|S|} \sum_{s \in S} \vec{s}$ is calculated.
- Top candidate songs matching the centroid are ranked, strictly excluding tracks the user has already played or favorited.

---

## 6. Database Architecture (SQLite)

The SQLite database is initialized automatically at `database/music.db`.

### Schema Design
- **`users`**: `id`, `username`, `email`, `password_hash`, `created_at`
- **`songs`**: `id`, `song_id`, `song_name`, `artist`, `album`, `genre`, `language`, `year`
- **`listening_history`**: `id`, `user_id`, `song_id`, `action`, `played_at` (Foreign Key $\to$ `users.id`)
- **`likes`**: `id`, `user_id`, `song_id`, `created_at` (Unique constraint on `user_id, song_id`)
- **`dislikes`**: `id`, `user_id`, `song_id`, `created_at`
- **`playlists`**: `id`, `user_id`, `playlist_name`, `created_at`
- **`playlist_songs`**: `id`, `playlist_id`, `song_id`, `added_at`

---

## 7. Authentication & Security

- **Password Hashing**: Implements salted **PBKDF2-HMAC-SHA256** with 100,000 iterations and cryptographically random salts via `secrets.token_hex`.
- **Verification**: Constant-time verification using `hmac.compare_digest` to prevent timing attacks.
- **Session State**: User password hashes are sanitized before populating Streamlit session state.

---

## 8. Installation & Running Locally

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd "music recommendation system"
```

### Step 2: Set Up Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Run Application
```bash
python -m streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 9. Automated Testing

To run the complete automated unit test suite:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

All 40 unit tests cover:
- CSV Loading, Uploading, and Parser Resilience (`test_data_loader.py`)
- Kaggle Dataset Adaptation and Schema Mapping (`test_adapter.py`)
- Data Preprocessing, Normalization, and Audio Bounding (`test_preprocessing.py`)
- SQLite CRUD, Playlists, Likes, and History (`test_database.py`)
- Password Hashing, User Registration, and Auth (`test_auth.py`)
- Content-Based & Personalized Recommendation Engine (`test_recommendation.py`)
- High-level Business Services (`test_services.py`)
- UI Empty States and Validation Handling (`test_ui_states.py`)

---

## 10. Deployment Readiness

- **Streamlit Community Cloud**:
  - Entrypoint: `app.py`
  - Dependencies: `requirements.txt`
  - Configuration: `.streamlit/config.toml`
- **Docker / Cloud Run**:
  ```dockerfile
  FROM python:3.11-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY . .
  EXPOSE 8501
  CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
  ```

---

## 11. Troubleshooting

- **Dataset Not Found**:
  Navigate to **⚙️ Settings / Dataset** or **🏠 Home** and upload your CSV.
- **Cache Refreshing**:
  Click **Clear Cache & Reload Catalog** in **Settings** to re-index the catalog and re-fit recommendation models.
- **Missing Audio Features**:
  The system automatically detects which features exist; missing audio columns gracefully default to text-based similarity without raising errors.

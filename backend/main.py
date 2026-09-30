import sys
from pathlib import Path

# Ensure project root and backend dir are in sys.path for serverless execution
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
for p in [str(PROJECT_ROOT), str(BASE_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.auth import router as auth_router
from backend.api.favorites import router as favorites_router
from backend.api.history import router as history_router
from backend.api.playlists import router as playlists_router
from backend.api.recommendations import router as recommendations_router
from backend.api.songs import get_cached_df, router as songs_router
from backend.api.users import router as users_router
from backend.database.connection import init_db
from backend.recommendation.engine import get_or_train_recommender


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle management."""
    # Initialize database tables
    try:
        init_db()
    except Exception as e:
        print(f"[Startup Warning] Database initialization exception: {e}")

    # Warm up music dataset and recommendation model
    try:
        df = get_cached_df()
        if not df.empty:
            get_or_train_recommender(df=df)
    except Exception as e:
        print(f"[Startup Warning] ML Engine warmup exception: {e}")

    yield


app = FastAPI(
    title="TuneSphere Music Recommendation API",
    description="Full-stack AI music recommendation and catalog discovery backend.",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS configuration for development and single-origin deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
@app.get("/health")
def health_check():
    """Health check endpoint to verify backend connectivity and operational status."""
    return {"status": "ok", "app": "TuneSphere", "version": "2.0.0"}


# Mount all routers under /api namespace
app.include_router(auth_router, prefix="/api")
app.include_router(songs_router, prefix="/api")
app.include_router(recommendations_router, prefix="/api")
app.include_router(favorites_router, prefix="/api")
app.include_router(history_router, prefix="/api")
app.include_router(playlists_router, prefix="/api")
app.include_router(users_router, prefix="/api")


# Also mount directly under root to handle Vercel rewrites where /api is stripped
app.include_router(auth_router)
app.include_router(songs_router)
app.include_router(recommendations_router)
app.include_router(favorites_router)
app.include_router(history_router)
app.include_router(playlists_router)
app.include_router(users_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

"""History API router recording listening activity and timeline interactions."""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from backend.api.songs import get_cached_df
from backend.auth.jwt_utils import get_current_user, get_optional_user
from backend.services.history_service import (
    clear_listening_history,
    get_user_timeline_history,
    log_play_action,
)

router = APIRouter(prefix="/history", tags=["History"])


class HistoryLogRequest(BaseModel):
    song_id: str
    action: Optional[str] = "PLAY"


@router.get("")
def list_history(
    limit: int = Query(50, ge=1, le=100),
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Retrieves chronological listening timeline entries for the current user."""
    df = get_cached_df()
    user_id = current_user["id"] if current_user else 1
    history = get_user_timeline_history(user_id=user_id, limit=limit, df=df)
    return {"history": history, "total": len(history)}


@router.post("")
def record_listening(
    req: HistoryLogRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Records a playback or interaction event into the listening history log."""
    user_id = current_user["id"] if current_user else 1
    log_play_action(user_id=user_id, song_id=str(req.song_id), action=req.action or "PLAY")
    return {"status": "ok", "song_id": req.song_id, "action": req.action}


@router.delete("")
def clear_history(current_user: dict = Depends(get_current_user)):
    """Clears all historical listening records for the authenticated user."""
    user_id = current_user["id"]
    clear_listening_history(user_id=user_id)
    return {"status": "ok", "message": "Listening history cleared successfully."}

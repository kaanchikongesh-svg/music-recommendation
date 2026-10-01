"""Recommendation ranking, filtering, and metadata enrichment module."""

from typing import Any, Dict, List, Optional, Set, Tuple
import pandas as pd


def rank_and_enrich_recommendations(
    candidates: List[Tuple[int, float]],
    df: pd.DataFrame,
    query_song_id: Optional[str] = None,
    exclude_song_ids: Optional[Set[str]] = None,
    preferred_language: Optional[str] = None,
    language_mode: str = "same",
    n_recommendations: int = 10,
) -> List[Dict[str, Any]]:
    """Filters, deduplicates, and enriches candidate song indices into structured recommendation items."""
    if df is None or df.empty or not candidates:
        return []

    exclude_set = set(exclude_song_ids or set())
    if query_song_id:
        exclude_set.add(str(query_song_id))

    ranked_items: List[Dict[str, Any]] = []
    seen_track_keys: Set[Tuple[str, str]] = set()

    # If same language requested and preferred language is known, partition into primary and fallback candidates
    target_lang = preferred_language.lower().strip() if preferred_language and preferred_language.lower().strip() not in ("unknown", "none", "") else None

    filtered_candidates = []
    if target_lang and language_mode == "same" and "language" in df.columns:
        # Prioritize matching language
        same_lang_candidates = []
        other_candidates = []
        for idx, score in candidates:
            if 0 <= idx < len(df):
                c_lang = str(df.iloc[idx].get("language", "")).lower().strip()
                if c_lang == target_lang:
                    same_lang_candidates.append((idx, score))
                else:
                    other_candidates.append((idx, score))
        filtered_candidates = same_lang_candidates + other_candidates
    else:
        filtered_candidates = candidates

    for idx, score in filtered_candidates:
        if idx < 0 or idx >= len(df):
            continue

        row = df.iloc[idx]
        sid = str(row["song_id"])

        if sid in exclude_set:
            continue

        # Avoid exact duplicate song name + artist pairs
        track_key = (str(row["song_name"]).lower().strip(), str(row["artist"]).lower().strip())
        if track_key in seen_track_keys:
            continue
        seen_track_keys.add(track_key)

        album_val = row.get("album")
        album_str = str(album_val) if album_val is not None and not pd.isna(album_val) and str(album_val).lower() != "unknown" else None

        genre_val = row.get("genre")
        genre_str = str(genre_val) if genre_val is not None and not pd.isna(genre_val) and str(genre_val).lower() != "unknown" else None

        lang_val = row.get("language")
        lang_str = str(lang_val) if lang_val is not None and not pd.isna(lang_val) and str(lang_val).lower() != "unknown" else None

        year_val = row.get("year")
        year_int = None
        if year_val is not None and not pd.isna(year_val):
            try:
                year_int = int(year_val)
            except (ValueError, TypeError):
                pass

        # Compute authentic similarity reason
        reason_parts = []
        if query_song_id and query_song_id in df["song_id"].values:
            q_row = df[df["song_id"] == query_song_id].iloc[0]
            if str(q_row["artist"]).lower().strip() == str(row["artist"]).lower().strip():
                reason_parts.append("Same artist")
            elif any(part in str(row["artist"]).lower() for part in str(q_row["artist"]).lower().split() if len(part) > 3):
                reason_parts.append("Related artist")
            
            if q_row.get("album") and row.get("album") and str(q_row["album"]).lower().strip() == str(row["album"]).lower().strip():
                reason_parts.append("Same soundtrack")
        
        if not reason_parts:
            if score > 0.6:
                reason_parts.append("Similar lyrics & theme")
            elif score > 0.4:
                reason_parts.append("Shared vocabulary & style")
            else:
                reason_parts.append("Lexical vector match")

        sim_reason = " • ".join(reason_parts)

        item: Dict[str, Any] = {
            "song_id": sid,
            "song_name": str(row["song_name"]),
            "artist": str(row["artist"]),
            "album": album_str,
            "genre": genre_str,
            "language": lang_str,
            "year": year_int,
            "similarity_score": round(float(score), 4),
            "similarity_reason": sim_reason,
            "reason": sim_reason,
        }

        # Include optional audio features if valid numeric value present
        for feat in [
            "danceability",
            "energy",
            "tempo",
            "valence",
            "acousticness",
            "instrumentalness",
            "speechiness",
            "loudness",
            "popularity",
        ]:
            if feat in row and pd.notna(row[feat]):
                try:
                    val = float(row[feat])
                    if not (pd.isna(val) or val != val):
                        item[feat] = val
                except (ValueError, TypeError):
                    pass

        ranked_items.append(item)
        if len(ranked_items) >= n_recommendations:
            break

    return ranked_items

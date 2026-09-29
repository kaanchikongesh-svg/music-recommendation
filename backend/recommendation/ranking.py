"""Recommendation ranking, filtering, and metadata enrichment module."""

from typing import Any, Dict, List, Optional, Set, Tuple
import pandas as pd


def rank_and_enrich_recommendations(
    candidates: List[Tuple[int, float]],
    df: pd.DataFrame,
    query_song_id: Optional[str] = None,
    exclude_song_ids: Optional[Set[str]] = None,
    n_recommendations: int = 10,
) -> List[Dict[str, Any]]:
    """Filters, deduplicates, and enriches candidate song indices into structured recommendation items.

    Args:
        candidates: List of (row_index, similarity_score) tuples.
        df: Pandas DataFrame of song library.
        query_song_id: Optional query song ID to strictly exclude.
        exclude_song_ids: Set of song IDs to exclude (e.g., previously played or liked).
        n_recommendations: Maximum number of ranked recommendations to return.

    Returns:
        List of enriched song dictionaries with similarity scores and metadata.
    """
    if df is None or df.empty or not candidates:
        return []

    exclude_set = set(exclude_song_ids or set())
    if query_song_id:
        exclude_set.add(str(query_song_id))

    ranked_items: List[Dict[str, Any]] = []
    seen_track_keys: Set[Tuple[str, str]] = set()

    for idx, score in candidates:
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

        item = {
            "song_id": sid,
            "song_name": str(row["song_name"]),
            "artist": str(row["artist"]),
            "album": str(row.get("album", "Unknown")),
            "genre": str(row.get("genre", "Unknown")),
            "language": str(row.get("language", "Unknown")),
            "year": int(row["year"]) if pd.notna(row.get("year")) and str(row.get("year")).isdigit() else None,
            "similarity_score": round(float(score), 4),
        }

        # Include optional audio features if present in DataFrame
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
                    item[feat] = float(row[feat])
                except (ValueError, TypeError):
                    pass

        ranked_items.append(item)
        if len(ranked_items) >= n_recommendations:
            break

    return ranked_items

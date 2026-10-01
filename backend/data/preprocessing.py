"""Data preprocessing pipeline for text normalization, feature engineering, and data quality validation."""

from dataclasses import asdict, dataclass, field
import json
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

from backend.data.adapter import adapt_kaggle_dataset

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_PROCESSED_DATA_PATH = BASE_DIR / "data" / "processed" / "songs_processed.csv"

BOUNDED_AUDIO_FEATURES = [
    "danceability",
    "energy",
    "valence",
    "acousticness",
    "instrumentalness",
    "speechiness",
    "liveness",
]


@dataclass
class PreprocessingReport:
    """Detailed summary of data quality, cleaning steps, and row counts."""

    source_rows: int = 0
    original_rows: int = 0
    valid_rows: int = 0
    final_rows: int = 0
    invalid_rows: int = 0
    duplicate_rows: int = 0
    duplicates_removed: int = 0
    final_rows_imported: int = 0
    missing_lyrics: int = 0
    missing_artists: int = 0
    missing_artists_removed: int = 0
    missing_song_names: int = 0
    missing_song_names_removed: int = 0
    invalid_years_handled: int = 0
    invalid_audio_values_fixed: List[str] = field(default_factory=list)
    available_audio_features: List[str] = field(default_factory=list)
    missing_audio_features: List[str] = field(default_factory=list)
    unique_artists: int = 0
    unique_songs: int = 0
    features_engineered: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PreprocessingResult:
    """Result container supporting both attribute access and tuple unpacking."""

    is_success: bool = True
    df: Optional[pd.DataFrame] = None
    report: Optional[PreprocessingReport] = None
    errors: List[str] = field(default_factory=list)
    error_message: Optional[str] = None

    def __iter__(self):
        yield self.df if self.df is not None else pd.DataFrame()
        yield self.report if self.report is not None else PreprocessingReport()

    def __getitem__(self, index: int):
        items = (self.df if self.df is not None else pd.DataFrame(), self.report if self.report is not None else PreprocessingReport())
        return items[index]


def clean_text_field(text: Any) -> str:
    """Cleans a single text string by stripping and normalizing whitespace."""
    if text is None or pd.isna(text):
        return ""
    val = str(text).strip()
    val = re.sub(r"\s+", " ", val)
    return val


def clean_text(text: Any) -> str:
    return clean_text_field(text)


def normalize_text(text: Any) -> str:
    return clean_text_field(text).lower()


def clean_year_column(series: pd.Series) -> pd.Series:
    from backend.data.adapter import extract_year_from_value
    return series.apply(extract_year_from_value)


def validate_and_clean_audio_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    clean_df = df.copy()
    fixed_cols: List[str] = []
    
    for col in BOUNDED_AUDIO_FEATURES:
        if col in clean_df.columns:
            orig = pd.to_numeric(clean_df[col], errors="coerce")
            needs_fix = ((orig < 0.0) | (orig > 1.0)).any() or orig.isna().any()
            if needs_fix:
                fixed_cols.append(col)
            clean_df[col] = orig.clip(0.0, 1.0)
            
    if "tempo" in clean_df.columns:
        tempo_orig = pd.to_numeric(clean_df["tempo"], errors="coerce")
        if (tempo_orig <= 0).any() or tempo_orig.isna().any():
            if "tempo" not in fixed_cols:
                fixed_cols.append("tempo")
        # Replace non-positive tempo with fallback median or positive value
        clean_df["tempo"] = tempo_orig.apply(lambda v: 120.0 if pd.isna(v) or v <= 0 else float(v))
        
    return clean_df, fixed_cols


def clean_lyrics_for_feature(text: Any, max_words: int = 250) -> str:
    """Extracts and normalizes clean lyrical tokens for TF-IDF feature engineering."""
    if text is None or pd.isna(text):
        return ""
    val = str(text).replace("\r\n", " ").replace("\n", " ")
    val = re.sub(r"[^\w\s]", " ", val)
    val = re.sub(r"\s+", " ", val).strip().lower()
    words = val.split()
    if len(words) > max_words:
        words = words[:max_words]
    return " ".join(words)


def create_combined_features(row: pd.Series) -> str:
    """Builds a unified text feature string from song_name, artist, album, genre, language, and lyrics."""
    parts: List[str] = []

    for col in ["song_name", "artist", "album", "genre", "language"]:
        val = row.get(col, None)
        if val is not None and not pd.isna(val):
            cleaned = clean_text_field(val)
            if cleaned and cleaned.lower() not in ("unknown", "none", "nan"):
                parts.append(cleaned.lower())

    lyrics = row.get("lyrics", None)
    if lyrics is not None and not pd.isna(lyrics):
        lyrics_feat = clean_lyrics_for_feature(lyrics, max_words=200)
        if lyrics_feat:
            parts.append(lyrics_feat)

    return " ".join(parts)


def preprocess_dataset(
    df: pd.DataFrame,
    report_path: Optional[Union[str, Path]] = None,
    save_processed: bool = False,
    output_path: Optional[Union[str, Path]] = None,
    processed_path: Optional[Union[str, Path]] = None,
) -> PreprocessingResult:
    """Cleans, adapts, and feature-engineers a raw music DataFrame."""
    dest_path = output_path or processed_path

    if df is None or df.empty:
        rep_empty = PreprocessingReport(
            source_rows=0,
            original_rows=0,
            warnings=["Empty input DataFrame."],
        )
        return PreprocessingResult(
            is_success=False,
            df=None,
            report=rep_empty,
            errors=["Empty input DataFrame."],
            error_message="Empty input DataFrame.",
        )

    clean_working_df = df.copy()
    initial_len = len(clean_working_df)
    report = PreprocessingReport(
        source_rows=initial_len,
        original_rows=initial_len,
    )

    # 1. Adapt schema if needed
    adapted_df, adapt_rep = adapt_kaggle_dataset(clean_working_df)
    if not adapt_rep.is_adapted or adapted_df.empty:
        report.warnings.extend(adapt_rep.warnings)
        return PreprocessingResult(
            is_success=False,
            df=None,
            report=report,
            errors=adapt_rep.warnings,
            error_message=str(adapt_rep.warnings),
        )

    report.invalid_years_handled = adapt_rep.invalid_years_handled

    # Clean text values
    for col in ["song_name", "artist"]:
        if col in adapted_df.columns:
            adapted_df[col] = adapted_df[col].apply(clean_text_field)

    # 2. Track missing song_name and artist
    missing_song_mask = adapted_df["song_name"].fillna("").str.strip() == ""
    missing_artist_mask = adapted_df["artist"].fillna("").str.strip() == ""

    report.missing_song_names = int(missing_song_mask.sum())
    report.missing_song_names_removed = report.missing_song_names
    report.missing_artists = int(missing_artist_mask.sum())
    report.missing_artists_removed = report.missing_artists

    if "lyrics" in adapted_df.columns:
        report.missing_lyrics = int(
            adapted_df["lyrics"].isna().sum() + (adapted_df["lyrics"].fillna("").str.strip() == "").sum()
        )

    # Filter out missing required fields
    valid_mask = (~missing_song_mask) & (~missing_artist_mask)
    report.invalid_rows = int((~valid_mask).sum())
    clean_df = adapted_df[valid_mask].copy()

    # Clean year if present
    if "year" in clean_df.columns:
        if report.invalid_years_handled == 0:
            from backend.data.adapter import extract_year_from_value
            cleaned_years = clean_df["year"].apply(extract_year_from_value)
            invalid_years = int((clean_df["year"].notna() & cleaned_years.isna()).sum())
            report.invalid_years_handled = invalid_years
            clean_df["year"] = cleaned_years

    # Audio features cleaning
    audio_cols_present = [c for c in BOUNDED_AUDIO_FEATURES + ["tempo"] if c in clean_df.columns]
    report.available_audio_features = audio_cols_present
    report.missing_audio_features = [c for c in BOUNDED_AUDIO_FEATURES + ["tempo"] if c not in clean_df.columns]
    
    clean_df, fixed_audio = validate_and_clean_audio_features(clean_df)
    report.invalid_audio_values_fixed = fixed_audio

    # 4. Detect and remove duplicate records
    subset_cols = ["artist", "song_name"]
    if "source_link" in clean_df.columns and clean_df["source_link"].notna().any():
        subset_cols.append("source_link")
    elif "song_id" in clean_df.columns:
        subset_cols = ["song_id"]

    dupe_count = int(clean_df.duplicated(subset=subset_cols).sum())
    report.duplicate_rows = dupe_count
    report.duplicates_removed = dupe_count
    clean_df = clean_df.drop_duplicates(subset=subset_cols).reset_index(drop=True)

    report.valid_rows = len(clean_df)
    report.final_rows = len(clean_df)
    report.final_rows_imported = len(clean_df)
    report.unique_artists = int(clean_df["artist"].nunique()) if "artist" in clean_df.columns else 0
    report.unique_songs = int(clean_df["song_name"].nunique()) if "song_name" in clean_df.columns else 0

    # 5. Feature Engineering
    clean_df["combined_features"] = clean_df.apply(create_combined_features, axis=1)
    report.features_engineered = ["combined_features"]

    # 6. Save data quality report if requested
    if report_path:
        r_path = Path(report_path)
        r_path.parent.mkdir(parents=True, exist_ok=True)
        with open(r_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2)

    # 7. Save processed csv if requested
    if save_processed or dest_path:
        dest = Path(dest_path or DEFAULT_PROCESSED_DATA_PATH)
        dest.parent.mkdir(parents=True, exist_ok=True)
        clean_df.to_csv(dest, index=False)

    return PreprocessingResult(
        is_success=True,
        df=clean_df,
        report=report,
    )


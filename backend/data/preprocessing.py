"""Data preprocessing pipeline module for Music Recommendation System."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from backend.data.validator import (
    OPTIONAL_AUDIO_FEATURES,
    REQUIRED_COLUMNS,
    get_optional_features,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_PROCESSED_DATA_PATH = BASE_DIR / "data" / "processed" / "songs_processed.csv"

# Typical bounded audio feature columns [0.0, 1.0]
BOUNDED_AUDIO_FEATURES = [
    "danceability",
    "energy",
    "valence",
    "acousticness",
    "instrumentalness",
    "speechiness",
]


@dataclass
class PreprocessingReport:
    """Detailed summary of transformations applied during preprocessing."""

    original_rows: int = 0
    final_rows: int = 0
    duplicates_removed: int = 0
    missing_song_names_removed: int = 0
    missing_artists_removed: int = 0
    invalid_years_handled: int = 0
    available_audio_features: List[str] = field(default_factory=list)
    missing_audio_features: List[str] = field(default_factory=list)
    invalid_audio_values_fixed: Dict[str, int] = field(default_factory=dict)
    unique_genres: int = 0
    unique_artists: int = 0
    unique_languages: int = 0


@dataclass
class PreprocessingResult:
    """Encapsulates the outcome of dataset preprocessing."""

    is_success: bool
    df: Optional[pd.DataFrame] = None
    report: PreprocessingReport = field(default_factory=PreprocessingReport)
    errors: List[str] = field(default_factory=list)


def clean_text(text: Any) -> str:
    """Cleans a single text value by stripping whitespace and collapsing multiple spaces."""
    if text is None or pd.isna(text):
        return ""
    s = str(text).strip()
    return re.sub(r"\s+", " ", s)


def normalize_text(text: Any) -> str:
    """Normalizes text for matching and recommendation tokens by lowercasing."""
    return clean_text(text).lower()


def clean_year_column(series: pd.Series) -> Tuple[pd.Series, int]:
    """Cleans release year column, validating range and converting valid values to nullable integer."""
    current_year = datetime.now().year
    numeric_years = pd.to_numeric(series, errors="coerce")

    # Flag invalid years (non-numeric, < 1800, or > current_year + 5)
    invalid_mask = (
        numeric_years.isna()
        | (numeric_years < 1800)
        | (numeric_years > current_year + 5)
    )
    invalid_count = int(invalid_mask.sum())

    cleaned_years = numeric_years.copy()
    cleaned_years[invalid_mask] = np.nan

    return cleaned_years.astype("Int64"), invalid_count


def validate_and_clean_audio_features(
    df: pd.DataFrame, detected_features: List[str]
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Validates and cleans optional audio features without fabricating missing columns."""
    cleaned_df = df.copy()
    fixed_counts: Dict[str, int] = {}

    for feat in detected_features:
        if feat not in cleaned_df.columns:
            continue

        numeric_col = pd.to_numeric(cleaned_df[feat], errors="coerce")
        fixed = 0

        if feat in BOUNDED_AUDIO_FEATURES:
            out_of_bounds = (numeric_col < 0.0) | (numeric_col > 1.0)
            fixed += int(out_of_bounds.sum()) + int(numeric_col.isna().sum())
            median_val = numeric_col.median()
            fill_val = median_val if pd.notna(median_val) else 0.5
            cleaned_col = numeric_col.fillna(fill_val).clip(lower=0.0, upper=1.0)
        elif feat == "popularity":
            out_of_bounds = (numeric_col < 0) | (numeric_col > 100)
            fixed += int(out_of_bounds.sum()) + int(numeric_col.isna().sum())
            median_val = numeric_col.median()
            fill_val = median_val if pd.notna(median_val) else 50
            cleaned_col = numeric_col.fillna(fill_val).clip(lower=0, upper=100)
        elif feat == "tempo":
            invalid_tempo = (numeric_col <= 0) | numeric_col.isna()
            fixed += int(invalid_tempo.sum())
            median_val = numeric_col[numeric_col > 0].median()
            fill_val = median_val if pd.notna(median_val) else 120.0
            cleaned_col = numeric_col.mask(invalid_tempo, fill_val)
        else:
            invalid_num = numeric_col.isna()
            fixed += int(invalid_num.sum())
            median_val = numeric_col.median()
            fill_val = median_val if pd.notna(median_val) else 0.0
            cleaned_col = numeric_col.fillna(fill_val)

        cleaned_df[feat] = cleaned_col
        if fixed > 0:
            fixed_counts[feat] = fixed

    return cleaned_df, fixed_counts


def create_combined_features(df: pd.DataFrame) -> pd.Series:
    """Constructs a unified, normalized text feature combining metadata for TF-IDF."""
    song_names = df["song_name"].apply(normalize_text)
    artists = df["artist"].apply(normalize_text)
    albums = df["album"].apply(normalize_text)
    genres = df["genre"].apply(normalize_text)
    languages = df["language"].apply(normalize_text)

    combined = (
        song_names
        + " "
        + artists
        + " "
        + albums
        + " "
        + genres
        + " "
        + languages
    )
    return combined.apply(lambda s: re.sub(r"\s+", " ", s).strip())


def preprocess_dataset(
    df: Optional[pd.DataFrame],
    save_processed: bool = True,
    processed_path: Union[str, Path] = DEFAULT_PROCESSED_DATA_PATH,
) -> PreprocessingResult:
    """Executes the complete preprocessing pipeline on a raw songs DataFrame."""
    if df is None or df.empty:
        return PreprocessingResult(
            is_success=False,
            df=None,
            report=PreprocessingReport(),
            errors=["Input DataFrame is empty or None."],
        )

    # 1. Verify required columns exist
    missing_req = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_req:
        return PreprocessingResult(
            is_success=False,
            df=None,
            report=PreprocessingReport(original_rows=len(df)),
            errors=[
                f"Cannot preprocess dataset missing required columns: {', '.join(missing_req)}"
            ],
        )

    raw_df = df.copy()
    original_rows = len(raw_df)

    # Clean strings of required columns
    for col in ["song_id", "song_name", "artist", "album", "genre", "language"]:
        raw_df[col] = raw_df[col].apply(clean_text)

    # Handle critical missing values
    missing_names_mask = raw_df["song_name"] == ""
    missing_song_names_count = int(missing_names_mask.sum())
    cleaned_df = raw_df[~missing_names_mask].copy()

    missing_artists_mask = cleaned_df["artist"] == ""
    missing_artists_count = int(missing_artists_mask.sum())
    cleaned_df = cleaned_df[~missing_artists_mask].copy()

    missing_ids_mask = cleaned_df["song_id"] == ""
    cleaned_df = cleaned_df[~missing_ids_mask].copy()

    # Deduplicate records by song_id
    before_dedup = len(cleaned_df)
    cleaned_df = cleaned_df.drop_duplicates(subset=["song_id"], keep="first").copy()
    duplicates_removed = before_dedup - len(cleaned_df)

    # Impute missing non-critical metadata
    cleaned_df["album"] = cleaned_df["album"].replace("", "Unknown")
    cleaned_df["genre"] = cleaned_df["genre"].replace("", "Unknown")
    cleaned_df["language"] = cleaned_df["language"].replace("", "Unknown")

    # Clean release year column
    cleaned_df["year"], invalid_years_count = clean_year_column(cleaned_df["year"])

    # Clean audio features if present
    detected_features = get_optional_features(cleaned_df)
    missing_features = [f for f in OPTIONAL_AUDIO_FEATURES if f not in detected_features]
    cleaned_df, fixed_audio_counts = validate_and_clean_audio_features(
        cleaned_df, detected_features
    )

    # Create combined features for recommendation engine
    cleaned_df["combined_features"] = create_combined_features(cleaned_df)

    final_rows = len(cleaned_df)
    unique_genres = int(cleaned_df["genre"].nunique())
    unique_artists = int(cleaned_df["artist"].nunique())
    unique_languages = int(cleaned_df["language"].nunique())

    report = PreprocessingReport(
        original_rows=original_rows,
        final_rows=final_rows,
        duplicates_removed=duplicates_removed,
        missing_song_names_removed=missing_song_names_count,
        missing_artists_removed=missing_artists_count,
        invalid_years_handled=invalid_years_count,
        available_audio_features=detected_features,
        missing_audio_features=missing_features,
        invalid_audio_values_fixed=fixed_audio_counts,
        unique_genres=unique_genres,
        unique_artists=unique_artists,
        unique_languages=unique_languages,
    )

    # Save processed dataset to disk if requested
    if save_processed and final_rows > 0:
        target_path = Path(processed_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        cleaned_df.to_csv(target_path, index=False)

    return PreprocessingResult(
        is_success=True,
        df=cleaned_df,
        report=report,
        errors=[],
    )

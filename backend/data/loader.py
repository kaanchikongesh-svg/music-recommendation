"""Data loading, upload persistence, and catalog querying module."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import pandas as pd

from backend.data.adapter import adapt_kaggle_dataset
from backend.data.validator import (
    OPTIONAL_AUDIO_FEATURES,
    REQUIRED_COLUMNS,
    ValidationResult,
    get_optional_features,
    validate_dataset,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "songs.csv"


def load_dataset(file_path: Union[str, Path] = DEFAULT_RAW_DATA_PATH) -> ValidationResult:
    """Loads a CSV dataset from the specified file path and validates it.

    Args:
        file_path: Relative or absolute path to CSV file. Defaults to data/raw/songs.csv.

    Returns:
        ValidationResult with validation status, DataFrame, errors, warnings, and statistics.
    """
    path = Path(file_path)

    if not path.exists():
        return ValidationResult(
            is_valid=False,
            errors=[f"Dataset file not found at '{path}'."],
        )

    try:
        if path.stat().st_size == 0:
            return ValidationResult(
                is_valid=False,
                errors=[f"Dataset file '{path}' is completely empty (0 bytes)."],
            )
    except OSError as e:
        return ValidationResult(
            is_valid=False,
            errors=[f"Failed to check file size for '{path}': {str(e)}"],
        )

    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return ValidationResult(
            is_valid=False,
            errors=[f"CSV file '{path}' contains no data or headers."],
        )
    except pd.errors.ParserError as e:
        return ValidationResult(
            is_valid=False,
            errors=[f"CSV parsing error while reading '{path}': {str(e)}"],
        )
    except UnicodeDecodeError as e:
        return ValidationResult(
            is_valid=False,
            errors=[
                f"Encoding error while reading '{path}': {str(e)}. Please save the file with UTF-8 encoding."
            ],
        )
    except Exception as e:
        return ValidationResult(
            is_valid=False,
            errors=[f"Unexpected error while loading '{path}': {str(e)}"],
        )

    return validate_dataset(df)


def save_uploaded_dataset(
    uploaded_file: Any,
    target_path: Union[str, Path] = DEFAULT_RAW_DATA_PATH,
    auto_adapt: bool = True,
) -> ValidationResult:
    """Validates an uploaded file from Streamlit file_uploader and saves it to disk if valid.

    Args:
        uploaded_file: Streamlit UploadedFile or file-like object containing CSV bytes.
        target_path: Path where valid CSV will be saved. Defaults to data/raw/songs.csv.
        auto_adapt: Whether to run the Kaggle adapter if direct validation fails.

    Returns:
        ValidationResult from validation check.
    """
    if uploaded_file is None:
        return ValidationResult(is_valid=False, errors=["No file was uploaded."])

    try:
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file)
    except pd.errors.EmptyDataError:
        return ValidationResult(
            is_valid=False, errors=["Uploaded file contains no data or headers."]
        )
    except pd.errors.ParserError as e:
        return ValidationResult(
            is_valid=False, errors=[f"CSV parsing error in uploaded file: {str(e)}"]
        )
    except UnicodeDecodeError as e:
        return ValidationResult(
            is_valid=False,
            errors=[
                f"Encoding error in uploaded file: {str(e)}. Please use UTF-8 encoding."
            ],
        )
    except Exception as e:
        return ValidationResult(
            is_valid=False,
            errors=[f"Failed to read uploaded CSV: {str(e)}"],
        )

    result = validate_dataset(df)

    # If direct validation failed and auto_adapt is enabled, try adapter
    if not result.is_valid and auto_adapt:
        adapted_df, report = adapt_kaggle_dataset(df)
        if report.is_adapted:
            adapted_result = validate_dataset(adapted_df)
            if adapted_result.is_valid:
                result = adapted_result
                df = adapted_df

    # Save ONLY if dataset is valid
    if result.is_valid:
        path = Path(target_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        result.df = df

    return result


def get_dataset_statistics(df: Optional[pd.DataFrame]) -> Dict[str, Any]:
    """Calculates comprehensive summary statistics from a valid songs DataFrame."""
    if df is None or df.empty:
        return {
            "total_songs": 0,
            "total_artists": 0,
            "total_albums": 0,
            "total_genres": 0,
            "total_languages": 0,
            "genres_list": [],
            "artists_list": [],
            "languages_list": [],
            "years_range": (1900, datetime.now().year),
        }

    years = pd.to_numeric(df["year"], errors="coerce").dropna()
    min_year = int(years.min()) if not years.empty else 1900
    max_year = int(years.max()) if not years.empty else datetime.now().year

    genres_series = df["genre"].dropna().astype(str).str.strip()
    genres_list = sorted([g for g in genres_series.unique() if g and g.lower() != "unknown"])

    artists_series = df["artist"].dropna().astype(str).str.strip()
    artists_list = sorted([a for a in artists_series.unique() if a and a.lower() != "unknown"])

    languages_series = df["language"].dropna().astype(str).str.strip()
    languages_list = sorted([l for l in languages_series.unique() if l and l.lower() != "unknown"])

    return {
        "total_songs": len(df),
        "total_artists": int(df["artist"].dropna().nunique()) if "artist" in df.columns else 0,
        "total_albums": int(df["album"].dropna().nunique()) if "album" in df.columns else 0,
        "total_genres": len(genres_list),
        "total_languages": len(languages_list),
        "genres_list": genres_list,
        "artists_list": artists_list,
        "languages_list": languages_list,
        "years_range": (min_year, max_year),
    }


def filter_songs(
    df: Optional[pd.DataFrame],
    search_query: str = "",
    artist: str = "All",
    genre: str = "All",
    language: str = "All",
    year_range: Optional[Tuple[int, int]] = None,
) -> pd.DataFrame:
    """Filters songs dataframe according to search keywords and selected facet filters."""
    if df is None or df.empty:
        return pd.DataFrame()

    filtered = df.copy()

    # Search query in song_name, artist, album
    if search_query and search_query.strip():
        q = search_query.strip().lower()
        mask = (
            filtered["song_name"].astype(str).str.lower().str.contains(q, na=False)
            | filtered["artist"].astype(str).str.lower().str.contains(q, na=False)
            | filtered["album"].astype(str).str.lower().str.contains(q, na=False)
        )
        filtered = filtered[mask]

    # Artist filter
    if artist and artist != "All":
        filtered = filtered[filtered["artist"] == artist]

    # Genre filter
    if genre and genre != "All":
        filtered = filtered[filtered["genre"] == genre]

    # Language filter
    if language and language != "All":
        filtered = filtered[filtered["language"] == language]

    # Year range filter
    if year_range and len(year_range) == 2:
        year_num = pd.to_numeric(filtered["year"], errors="coerce")
        filtered = filtered[
            (year_num >= year_range[0]) & (year_num <= year_range[1])
        ]

    return filtered

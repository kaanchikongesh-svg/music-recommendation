"""Dataset validation module for checking schema, integrity, and data types."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import pandas as pd

# Mandatory columns required in canonical dataset
REQUIRED_COLUMNS: List[str] = [
    "song_id",
    "song_name",
    "artist",
    "album",
    "genre",
    "language",
    "year",
]

# Supported optional audio and popularity features
OPTIONAL_AUDIO_FEATURES: List[str] = [
    "danceability",
    "energy",
    "tempo",
    "valence",
    "acousticness",
    "instrumentalness",
    "speechiness",
    "loudness",
    "popularity",
]


@dataclass
class ValidationResult:
    """Encapsulates dataset validation status, dataframe reference, errors, and statistics."""

    is_valid: bool
    df: Optional[pd.DataFrame] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    missing_required_columns: List[str] = field(default_factory=list)
    detected_audio_features: List[str] = field(default_factory=list)
    total_songs: int = 0
    unique_artists: int = 0
    unique_albums: int = 0
    unique_genres: int = 0
    unique_languages: int = 0


def get_optional_features(df: Optional[pd.DataFrame]) -> List[str]:
    """Detect which supported optional audio feature columns are present in the DataFrame."""
    if df is None or df.empty:
        return []
    return [col for col in OPTIONAL_AUDIO_FEATURES if col in df.columns]


# Backwards compatibility alias
detect_audio_features = get_optional_features


def validate_dataset(df: Optional[pd.DataFrame]) -> ValidationResult:
    """Validates structure, required columns, non-null identifiers, and value ranges of a song dataset.

    Args:
        df: Pandas DataFrame to validate.

    Returns:
        ValidationResult containing validation status, diagnostics, and catalog statistics.
    """
    errors: List[str] = []
    warnings: List[str] = []

    if df is None:
        return ValidationResult(is_valid=False, errors=["Dataset DataFrame is None."])

    if df.empty:
        return ValidationResult(
            is_valid=False, errors=["Dataset is empty (0 rows found)."]
        )

    # 1. Check required columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        errors.append(
            f"Missing required columns: {', '.join(missing_cols)}. "
            f"Required columns are: {', '.join(REQUIRED_COLUMNS)}."
        )
        return ValidationResult(
            is_valid=False,
            df=df,
            errors=errors,
            missing_required_columns=missing_cols,
            detected_audio_features=get_optional_features(df),
            total_songs=len(df),
        )

    # 2. Detect optional audio features
    detected_features = get_optional_features(df)

    # 3. Check critical non-nulls (song_id, song_name, artist)
    null_song_ids = df["song_id"].isna() | (
        df["song_id"].astype(str).str.strip() == ""
    )
    if null_song_ids.any():
        count = int(null_song_ids.sum())
        errors.append(f"Found {count} row(s) with missing or empty 'song_id'.")

    null_song_names = df["song_name"].isna() | (
        df["song_name"].astype(str).str.strip() == ""
    )
    if null_song_names.any():
        count = int(null_song_names.sum())
        errors.append(f"Found {count} row(s) with missing or empty 'song_name'.")

    null_artists = df["artist"].isna() | (
        df["artist"].astype(str).str.strip() == ""
    )
    if null_artists.any():
        count = int(null_artists.sum())
        errors.append(f"Found {count} row(s) with missing or empty 'artist'.")

    # 4. Check duplicate song IDs
    duplicate_ids = df[df.duplicated(subset=["song_id"], keep=False)]
    if not duplicate_ids.empty:
        unique_dups = duplicate_ids["song_id"].nunique()
        warnings.append(
            f"Found {len(duplicate_ids)} duplicate row(s) sharing {unique_dups} unique 'song_id' value(s)."
        )

    # 5. Check 'year' column integrity
    current_year = datetime.now().year
    year_numeric = pd.to_numeric(df["year"], errors="coerce")
    invalid_year_mask = (
        year_numeric.isna()
        | (year_numeric < 1800)
        | (year_numeric > current_year + 5)
    )
    if invalid_year_mask.any():
        invalid_count = int(invalid_year_mask.sum())
        warnings.append(
            f"Found {invalid_count} row(s) with non-numeric or out-of-range 'year' values (valid range: 1800 - {current_year + 5})."
        )

    # 6. Check audio features numeric formats
    for feature in detected_features:
        non_numeric = pd.to_numeric(df[feature], errors="coerce").isna()
        if non_numeric.any():
            warnings.append(
                f"Audio feature column '{feature}' contains {int(non_numeric.sum())} non-numeric value(s)."
            )

    is_valid = len(errors) == 0

    unique_artists = int(df["artist"].dropna().nunique()) if "artist" in df.columns else 0
    unique_albums = int(df["album"].dropna().nunique()) if "album" in df.columns else 0
    unique_genres = int(df["genre"].dropna().nunique()) if "genre" in df.columns else 0
    unique_languages = int(df["language"].dropna().nunique()) if "language" in df.columns else 0

    return ValidationResult(
        is_valid=is_valid,
        df=df,
        errors=errors,
        warnings=warnings,
        missing_required_columns=missing_cols,
        detected_audio_features=detected_features,
        total_songs=len(df),
        unique_artists=unique_artists,
        unique_albums=unique_albums,
        unique_genres=unique_genres,
        unique_languages=unique_languages,
    )

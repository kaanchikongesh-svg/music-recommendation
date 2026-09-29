"""Data loading, validation, and querying module for Music Recommendation System.

Preserved for backwards-compatibility; delegates to backend.data.
"""

from backend.data.adapter import (
    AdaptationReport,
    COLUMN_ALIASES,
    adapt_kaggle_dataset,
    clean_artist_list_string,
    extract_year_from_value,
)
from backend.data.loader import (
    BASE_DIR,
    DEFAULT_RAW_DATA_PATH,
    filter_songs,
    get_dataset_statistics,
    load_dataset,
    save_uploaded_dataset,
)
from backend.data.validator import (
    OPTIONAL_AUDIO_FEATURES,
    REQUIRED_COLUMNS,
    ValidationResult,
    detect_audio_features,
    get_optional_features,
    validate_dataset,
)

__all__ = [
    "BASE_DIR",
    "DEFAULT_RAW_DATA_PATH",
    "REQUIRED_COLUMNS",
    "OPTIONAL_AUDIO_FEATURES",
    "ValidationResult",
    "AdaptationReport",
    "COLUMN_ALIASES",
    "load_dataset",
    "save_uploaded_dataset",
    "validate_dataset",
    "get_optional_features",
    "detect_audio_features",
    "get_dataset_statistics",
    "filter_songs",
    "adapt_kaggle_dataset",
    "clean_artist_list_string",
    "extract_year_from_value",
]

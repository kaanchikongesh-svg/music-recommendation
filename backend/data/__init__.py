"""Data layer package containing loaders, validators, Kaggle adapter, and preprocessing."""

from backend.data.adapter import (
    AdaptationReport,
    COLUMN_ALIASES,
    adapt_kaggle_dataset,
    clean_artist_list_string,
    extract_year_from_value,
)
from backend.data.loader import (
    DEFAULT_RAW_DATA_PATH,
    filter_songs,
    get_dataset_statistics,
    load_dataset,
    save_uploaded_dataset,
)
from backend.data.preprocessing import (
    DEFAULT_PROCESSED_DATA_PATH,
    PreprocessingReport,
    PreprocessingResult,
    clean_text,
    clean_year_column,
    create_combined_features,
    normalize_text,
    preprocess_dataset,
    validate_and_clean_audio_features,
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
    "DEFAULT_RAW_DATA_PATH",
    "DEFAULT_PROCESSED_DATA_PATH",
    "REQUIRED_COLUMNS",
    "OPTIONAL_AUDIO_FEATURES",
    "ValidationResult",
    "PreprocessingReport",
    "PreprocessingResult",
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
    "clean_text",
    "normalize_text",
    "clean_year_column",
    "validate_and_clean_audio_features",
    "create_combined_features",
    "preprocess_dataset",
]

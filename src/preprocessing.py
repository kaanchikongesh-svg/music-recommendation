"""Data preprocessing pipeline module for Music Recommendation System.

Preserved for backwards-compatibility; delegates to backend.data.preprocessing.
"""

from backend.data.preprocessing import (
    BOUNDED_AUDIO_FEATURES,
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

__all__ = [
    "DEFAULT_PROCESSED_DATA_PATH",
    "BOUNDED_AUDIO_FEATURES",
    "PreprocessingReport",
    "PreprocessingResult",
    "clean_text",
    "normalize_text",
    "clean_year_column",
    "validate_and_clean_audio_features",
    "create_combined_features",
    "preprocess_dataset",
]

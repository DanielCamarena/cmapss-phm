from __future__ import annotations

from .config import PredictiveSettings
from .data_loader import build_sequence_dataset, load_processed_split


def build_train_valid_windows(settings: PredictiveSettings, window_size: int):
    train_df = load_processed_split(settings, "train")
    valid_df = load_processed_split(settings, "valid")
    return (
        build_sequence_dataset(train_df, settings, window_size),
        build_sequence_dataset(valid_df, settings, window_size),
    )

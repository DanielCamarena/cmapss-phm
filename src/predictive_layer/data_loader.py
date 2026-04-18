from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .config import PredictiveSettings


@dataclass
class SequenceDataset:
    X: np.ndarray
    y: np.ndarray
    meta: pd.DataFrame


def load_processed_split(settings: PredictiveSettings, split_name: str) -> pd.DataFrame:
    df = pd.read_parquet(settings.root / "out" / "processed" / f"{split_name}_processed.parquet")
    df = df.sort_values(settings.group_columns + ["cycle"]).reset_index(drop=True)
    df["rul_capped"] = df[settings.target_column].clip(lower=0, upper=settings.target_cap)
    return df


def build_tabular_xy(df: pd.DataFrame, settings: PredictiveSettings) -> tuple[pd.DataFrame, np.ndarray, pd.DataFrame]:
    X = df[settings.features].copy()
    y = df["rul_capped"].to_numpy(dtype=np.float32)
    meta = df[settings.id_columns + [settings.target_column, "rul_capped"]].copy()
    return X, y, meta


def build_sequence_dataset(df: pd.DataFrame, settings: PredictiveSettings, window_size: int) -> SequenceDataset:
    sequences: list[np.ndarray] = []
    labels: list[float] = []
    meta_rows: list[dict] = []
    for (dataset_id, unit_id), unit_df in df.groupby(settings.group_columns, sort=False):
        unit_df = unit_df.sort_values("cycle")
        values = unit_df[settings.features].to_numpy(dtype=np.float32)
        targets = unit_df["rul_capped"].to_numpy(dtype=np.float32)
        cycles = unit_df["cycle"].to_numpy()
        raw_rul = unit_df[settings.target_column].to_numpy(dtype=np.float32)
        if len(unit_df) < window_size:
            continue
        for end_idx in range(window_size - 1, len(unit_df)):
            start_idx = end_idx - window_size + 1
            sequences.append(values[start_idx : end_idx + 1])
            labels.append(targets[end_idx])
            meta_rows.append(
                {
                    "dataset_id": dataset_id,
                    "unit_id": int(unit_id),
                    "cycle": int(cycles[end_idx]),
                    "rul": float(raw_rul[end_idx]),
                    "rul_capped": float(targets[end_idx]),
                    "window_size": window_size,
                }
            )
    return SequenceDataset(
        X=np.asarray(sequences, dtype=np.float32),
        y=np.asarray(labels, dtype=np.float32),
        meta=pd.DataFrame(meta_rows),
    )

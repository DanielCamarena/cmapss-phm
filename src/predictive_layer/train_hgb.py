from __future__ import annotations

import json
import time
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from .config import PredictiveSettings
from .data_loader import build_tabular_xy, load_processed_split
from .io_utils import write_json


def train_hgb(settings: PredictiveSettings) -> dict:
    train_df = load_processed_split(settings, "train")
    valid_df = load_processed_split(settings, "valid")
    X_train, y_train, _ = build_tabular_xy(train_df, settings)
    X_valid, y_valid, meta_valid = build_tabular_xy(valid_df, settings)

    model = HistGradientBoostingRegressor(**settings.hgb_params)
    start = time.perf_counter()
    model.fit(X_train, y_train)
    fit_seconds = time.perf_counter() - start

    preds = model.predict(X_valid)
    pred_df = meta_valid.copy()
    pred_df["model_name"] = "hgb"
    pred_df["y_pred"] = preds
    pred_df["target_policy"] = "rul_capped"
    pred_df.to_parquet(settings.out_dir / "02_valid_predictions_hgb.parquet", index=False)
    joblib.dump(model, settings.models_dir / "hgb_model.joblib")

    metadata = {
        "model_name": "hgb",
        "model_class": "HistGradientBoostingRegressor",
        "fit_seconds": fit_seconds,
        "train_rows": len(train_df),
        "valid_rows": len(valid_df),
        "features": settings.features,
        "target_cap": settings.target_cap,
        "params": settings.hgb_params,
    }
    write_json(settings.out_dir / "02_train_metadata_hgb.json", metadata)
    return metadata

from __future__ import annotations

import time

import joblib
from sklearn.ensemble import RandomForestRegressor

from .config import PredictiveSettings
from .data_loader import build_tabular_xy, load_processed_split
from .io_utils import write_json


def train_rf(settings: PredictiveSettings) -> dict:
    train_df = load_processed_split(settings, "train")
    valid_df = load_processed_split(settings, "valid")
    X_train, y_train, _ = build_tabular_xy(train_df, settings)
    X_valid, _, meta_valid = build_tabular_xy(valid_df, settings)

    model = RandomForestRegressor(**settings.rf_params)
    start = time.perf_counter()
    model.fit(X_train, y_train)
    fit_seconds = time.perf_counter() - start

    preds = model.predict(X_valid)
    pred_df = meta_valid.copy()
    pred_df["model_name"] = "rf"
    pred_df["y_pred"] = preds
    pred_df["target_policy"] = "rul_capped"
    pred_df.to_parquet(settings.out_dir / "02_valid_predictions_rf.parquet", index=False)
    joblib.dump(model, settings.models_dir / "rf_model.joblib")

    metadata = {
        "model_name": "rf",
        "model_class": "RandomForestRegressor",
        "fit_seconds": fit_seconds,
        "train_rows": len(train_df),
        "valid_rows": len(valid_df),
        "features": settings.features,
        "target_cap": settings.target_cap,
        "params": settings.rf_params,
    }
    write_json(settings.out_dir / "02_train_metadata_rf.json", metadata)
    return metadata

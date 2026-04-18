from __future__ import annotations

import json
from datetime import datetime, UTC
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from .config import load_settings


class ValidationError(Exception):
    pass


DATASETS = ["FD001", "FD002", "FD003", "FD004"]
META_COLUMNS = ["unit_id", "cycle"]
SETTING_COLUMNS = [f"op_setting_{i}" for i in range(1, 4)]
SENSOR_COLUMNS = [f"sensor_{i}" for i in range(1, 22)]
ALL_COLUMNS = META_COLUMNS + SETTING_COLUMNS + SENSOR_COLUMNS


def _load_split(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=r"\s+", header=None, engine="python")
    if df.shape[1] > len(ALL_COLUMNS):
        df = df.iloc[:, : len(ALL_COLUMNS)]
    df.columns = ALL_COLUMNS
    return df


def _add_train_rul(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    max_cycle = result.groupby("unit_id")["cycle"].transform("max")
    result["rul"] = max_cycle - result["cycle"]
    return result


def _split_train_valid(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_parts: list[pd.DataFrame] = []
    valid_parts: list[pd.DataFrame] = []
    for dataset_id, group in df.groupby("dataset_id"):
        unit_ids = sorted(group["unit_id"].unique())
        valid_count = max(1, int(round(0.2 * len(unit_ids))))
        valid_units = set(unit_ids[-valid_count:])
        train_parts.append(group[~group["unit_id"].isin(valid_units)].copy())
        valid_parts.append(group[group["unit_id"].isin(valid_units)].copy())
    return pd.concat(train_parts, ignore_index=True), pd.concat(valid_parts, ignore_index=True)


def _rebuild_training_scaler(settings) -> StandardScaler:
    train_frames: list[pd.DataFrame] = []
    for dataset_id in DATASETS:
        train_df = _load_split(settings.root / "data" / f"train_{dataset_id}.txt")
        train_df["dataset_id"] = dataset_id
        train_frames.append(_add_train_rul(train_df))
    train_all = pd.concat(train_frames, ignore_index=True)
    train_split, _ = _split_train_valid(train_all)
    scaler = StandardScaler()
    scaler.fit(train_split[settings.features])
    scaler_path = settings.root / "out" / "processed" / "standard_scaler.joblib"
    scaler_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, scaler_path)
    return scaler


def _load_or_rebuild_scaler(settings) -> StandardScaler:
    scaler_path = settings.root / "out" / "processed" / "standard_scaler.joblib"
    if scaler_path.exists():
        return joblib.load(scaler_path)
    return _rebuild_training_scaler(settings)


@lru_cache(maxsize=1)
def _load_runtime_assets():
    settings = load_settings()
    champion_record = json.loads((settings.out_dir / "champion_record.json").read_text(encoding="utf-8"))
    confidence_policy = json.loads((settings.out_dir / "05_confidence_band_policy.json").read_text(encoding="utf-8"))
    champion = champion_record["champion_model"]
    fallback = champion_record["fallback_model"]
    champion_model = joblib.load(settings.models_dir / f"{champion}_model.joblib") if champion in {"hgb", "rf"} else None
    fallback_model = joblib.load(settings.models_dir / f"{fallback}_model.joblib")
    scaler = _load_or_rebuild_scaler(settings)
    return settings, champion_record, confidence_policy, champion_model, fallback_model, scaler


def _coerce_features(payload: dict, features: list[str]) -> pd.DataFrame:
    values: list[float] = []
    op_settings = payload.get("op_settings", {})
    sensors = payload.get("sensors", {})
    for feature in features:
        if feature.startswith("op_setting_"):
            if feature not in op_settings:
                raise ValidationError(f"missing {feature}")
            values.append(float(op_settings[feature]))
        else:
            if feature not in sensors:
                raise ValidationError(f"missing {feature}")
            values.append(float(sensors[feature]))
    return pd.DataFrame([values], columns=features, dtype=np.float32)


def _prepare_model_input(payload: dict, features: list[str], scaler: StandardScaler) -> pd.DataFrame:
    raw = _coerce_features(payload, features)
    transformed = scaler.transform(raw[features])
    return pd.DataFrame(transformed, columns=features, dtype=np.float32)


def predict_rul(payload: dict) -> dict:
    settings, champion_record, confidence_policy, champion_model, fallback_model, scaler = _load_runtime_assets()
    try:
        for required in ["dataset_id", "unit_id", "cycle"]:
            if required not in payload:
                raise ValidationError(f"missing {required}")
        X = _prepare_model_input(payload, settings.features, scaler)
        service_status = "ok"
        model_name = champion_record["champion_model"]
        model = champion_model
        if model is None:
            service_status = "fallback"
            model_name = champion_record["fallback_model"]
            model = fallback_model
        y_pred = float(model.predict(X)[0])
        band = confidence_policy["quantiles"]["p80_abs_error"]
        response = {
            "rul_pred": round(max(0.0, y_pred), 3),
            "confidence_band": {
                "lower": round(max(0.0, y_pred - band), 3),
                "upper": round(max(0.0, y_pred + band), 3),
                "method": confidence_policy["method"],
            },
            "target_policy": {"name": "rul_capped", "cap": settings.target_cap},
            "model_version": f"predictive-layer-v1/{model_name}",
            "service_status": service_status,
            "trace": {
                "dataset_id": payload["dataset_id"],
                "feature_schema_version": "v1",
                "preprocessing_version": "plan1-baseline-v1",
                "scaler_artifact": "out/processed/standard_scaler.joblib",
                "fallback_model": champion_record["fallback_model"],
            },
            "timestamp": datetime.now(UTC).isoformat(),
        }
        return response
    except ValidationError as exc:
        return {
            "rul_pred": None,
            "confidence_band": None,
            "model_version": None,
            "service_status": "error_validacion",
            "error": str(exc),
            "timestamp": datetime.now(UTC).isoformat(),
        }

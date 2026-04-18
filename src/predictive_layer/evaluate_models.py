from __future__ import annotations

import json
import math
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

from .config import PredictiveSettings
from .data_loader import load_processed_split


def rul_band(value: float) -> str:
    if value <= 20:
        return "late_life"
    if value <= 60:
        return "mid_life"
    return "early_life"


def load_prediction_frames(settings: PredictiveSettings) -> dict[str, pd.DataFrame]:
    return {
        "hgb": pd.read_parquet(settings.out_dir / "02_valid_predictions_hgb.parquet"),
        "rf": pd.read_parquet(settings.out_dir / "02_valid_predictions_rf.parquet"),
        "lstm": pd.read_parquet(settings.out_dir / "03_valid_predictions_lstm.parquet"),
        "gru": pd.read_parquet(settings.out_dir / "03_valid_predictions_gru_or_tcn.parquet"),
    }


def measure_latency(settings: PredictiveSettings) -> pd.DataFrame:
    valid_df = load_processed_split(settings, "valid")
    sample_tabular = valid_df[settings.features].head(512)
    rows: list[dict] = []

    for name in ["hgb", "rf"]:
        model = joblib.load(settings.models_dir / f"{name}_model.joblib")
        start = time.perf_counter()
        _ = model.predict(sample_tabular)
        seconds = time.perf_counter() - start
        rows.append({"model_name": name, "samples": len(sample_tabular), "seconds": seconds, "ms_per_sample": seconds * 1000 / len(sample_tabular)})

    for path in [settings.out_dir / "03_train_metadata_lstm.json", settings.out_dir / "03_train_metadata_gru_or_tcn.json"]:
        metadata = json.loads(path.read_text(encoding="utf-8"))
        rows.append(
            {
                "model_name": metadata["model_name"],
                "samples": metadata["valid_windows"],
                "seconds": metadata["inference_seconds_valid"],
                "ms_per_sample": metadata["ms_per_sample_valid"],
            }
        )
    return pd.DataFrame(rows)


def evaluate_models(settings: PredictiveSettings) -> dict:
    prediction_frames = load_prediction_frames(settings)
    global_rows: list[dict] = []
    by_dataset_rows: list[dict] = []
    by_band_rows: list[dict] = []
    stability: dict[str, float] = {}

    for model_name, frame in prediction_frames.items():
        rmse = math.sqrt(mean_squared_error(frame["rul_capped"], frame["y_pred"]))
        mae = mean_absolute_error(frame["rul_capped"], frame["y_pred"])
        global_rows.append({"model_name": model_name, "rmse": rmse, "mae": mae, "rows": len(frame)})

        dataset_scores: list[float] = []
        for dataset_id, group in frame.groupby("dataset_id"):
            ds_rmse = math.sqrt(mean_squared_error(group["rul_capped"], group["y_pred"]))
            ds_mae = mean_absolute_error(group["rul_capped"], group["y_pred"])
            dataset_scores.append(ds_rmse)
            by_dataset_rows.append({"model_name": model_name, "dataset_id": dataset_id, "rmse": ds_rmse, "mae": ds_mae, "rows": len(group)})

        frame = frame.copy()
        frame["rul_band"] = frame["rul_capped"].map(rul_band)
        for band, group in frame.groupby("rul_band"):
            by_band_rows.append(
                {
                    "model_name": model_name,
                    "rul_band": band,
                    "rmse": math.sqrt(mean_squared_error(group["rul_capped"], group["y_pred"])),
                    "mae": mean_absolute_error(group["rul_capped"], group["y_pred"]),
                    "rows": len(group),
                }
            )
        stability[model_name] = max(dataset_scores) - min(dataset_scores)

    global_df = pd.DataFrame(global_rows).sort_values("rmse").reset_index(drop=True)
    by_dataset_df = pd.DataFrame(by_dataset_rows).sort_values(["model_name", "dataset_id"]).reset_index(drop=True)
    by_band_df = pd.DataFrame(by_band_rows).sort_values(["model_name", "rul_band"]).reset_index(drop=True)
    latency_df = measure_latency(settings)

    best_tabular = global_df[global_df["model_name"].isin(["hgb", "rf"])].sort_values("rmse").iloc[0]
    best_overall = global_df.iloc[0]
    improvement = (best_tabular["rmse"] - best_overall["rmse"]) / best_tabular["rmse"] if best_tabular["rmse"] else 0.0
    champion_name = str(best_tabular["model_name"])
    champion_reason = "Best stable baseline selected for integration readiness."

    if best_overall["model_name"] != best_tabular["model_name"]:
        if improvement >= 0.05:
            champion_name = str(best_overall["model_name"])
            champion_reason = f"Selected for exceeding the 5% RMSE improvement rule over the best tabular baseline ({improvement:.1%})."
        elif stability[str(best_overall["model_name"])] < stability[str(best_tabular["model_name"])]:
            champion_name = str(best_overall["model_name"])
            champion_reason = "Selected for better per-subset stability despite not clearing the 5% global RMSE threshold."

    sorted_tabular = global_df[global_df["model_name"].isin(["hgb", "rf"])].sort_values("rmse").reset_index(drop=True)
    fallback_name = str(sorted_tabular.iloc[min(1, len(sorted_tabular) - 1)]["model_name"])
    if champion_name not in {"hgb", "rf"}:
        fallback_name = str(best_tabular["model_name"])
    champion_record = {
        "champion_model": champion_name,
        "fallback_model": fallback_name,
        "best_tabular_model": str(best_tabular["model_name"]),
        "best_overall_model": str(best_overall["model_name"]),
        "best_tabular_rmse": float(best_tabular["rmse"]),
        "best_overall_rmse": float(best_overall["rmse"]),
        "relative_improvement_vs_tabular": float(improvement),
        "stability_spread_rmse": stability,
        "selection_reason": champion_reason,
    }

    global_df.to_csv(settings.out_dir / "04_metrics_global_by_model.csv", index=False)
    by_dataset_df.to_csv(settings.out_dir / "04_metrics_by_dataset_by_model.csv", index=False)
    by_band_df.to_csv(settings.out_dir / "04_error_by_rul_band_by_model.csv", index=False)
    latency_df.to_csv(settings.out_dir / "04_latency_by_model.csv", index=False)
    (settings.out_dir / "04_champion_decision_record.md").write_text(
        "\n".join(
            [
                "# Champion Decision Record",
                "",
                f"- Champion: `{champion_name}`",
                f"- Fallback: `{champion_record['fallback_model']}`",
                f"- Best tabular RMSE: {champion_record['best_tabular_rmse']:.4f}",
                f"- Best overall RMSE: {champion_record['best_overall_rmse']:.4f}",
                f"- Relative improvement vs best tabular: {champion_record['relative_improvement_vs_tabular']:.2%}",
                f"- Selection reason: {champion_reason}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (settings.out_dir / "champion_record.json").write_text(json.dumps(champion_record, indent=2), encoding="utf-8")
    return champion_record

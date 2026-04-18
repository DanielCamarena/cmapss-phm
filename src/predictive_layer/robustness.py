from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd

from .config import PredictiveSettings
from .data_loader import load_processed_split


def run_robustness(settings: PredictiveSettings, champion_record: dict) -> None:
    valid_df = load_processed_split(settings, "valid")
    champion_name = champion_record["champion_model"]
    fallback_name = champion_record["fallback_model"]
    results: list[dict] = []

    for model_name in {champion_name, fallback_name}:
        if model_name not in {"hgb", "rf"}:
            continue
        model = joblib.load(settings.models_dir / f"{model_name}_model.joblib")
        base_X = valid_df[settings.features].copy()
        y = valid_df["rul_capped"].to_numpy()
        for scenario, transformed in [
            ("clean", base_X),
            ("noise_0p05", base_X + np.random.default_rng(42).normal(0, 0.05, size=base_X.shape)),
            ("mask_sensor_2", base_X.assign(sensor_2=0.0 if "sensor_2" in base_X.columns else base_X.iloc[:, 0])),
        ]:
            pred = model.predict(transformed)
            rmse = float(np.sqrt(np.mean((y - pred) ** 2)))
            results.append({"model_name": model_name, "scenario": scenario, "rmse": rmse})
    complexity_map = valid_df[["dataset_id"]].copy()
    complexity_map["complexity"] = complexity_map["dataset_id"].map(lambda v: "simple" if v in {"FD001", "FD003"} else "complex")
    complexity_summary = complexity_map["complexity"].value_counts().to_dict()
    pd.DataFrame(results).to_csv(settings.out_dir / "05_robustness_results.csv", index=False)
    (settings.out_dir / "05_fallback_policy.txt").write_text(
        "\n".join(
            [
                "Fallback policy",
                "",
                f"Primary champion: {champion_name}",
                f"Fallback model: {fallback_name}",
                "- Use the fallback when the champion artifact is unavailable, when a sequence champion lacks sufficient history, or when validation fails for required champion inputs.",
                "- Preserve `service_status=fallback` and include the original failure reason in the response audit trace.",
                f"- Validation split composition by complexity: {complexity_summary}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

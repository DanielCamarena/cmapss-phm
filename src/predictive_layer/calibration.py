from __future__ import annotations

import json

import pandas as pd

from .config import PredictiveSettings


def build_calibration(settings: PredictiveSettings, champion_record: dict) -> dict:
    champion_name = champion_record["champion_model"]
    frame_map = {
        "hgb": pd.read_parquet(settings.out_dir / "02_valid_predictions_hgb.parquet"),
        "rf": pd.read_parquet(settings.out_dir / "02_valid_predictions_rf.parquet"),
        "lstm": pd.read_parquet(settings.out_dir / "03_valid_predictions_lstm.parquet"),
        "gru": pd.read_parquet(settings.out_dir / "03_valid_predictions_gru_or_tcn.parquet"),
    }
    frame = frame_map[champion_name].copy()
    abs_err = (frame["rul_capped"] - frame["y_pred"]).abs()
    policy = {
        "champion_model": champion_name,
        "method": "empirical_abs_error_quantiles",
        "quantiles": {
            "p50_abs_error": float(abs_err.quantile(0.5)),
            "p80_abs_error": float(abs_err.quantile(0.8)),
            "p90_abs_error": float(abs_err.quantile(0.9)),
        },
        "default_interval": "p80_abs_error",
    }
    (settings.out_dir / "05_confidence_band_policy.json").write_text(json.dumps(policy, indent=2), encoding="utf-8")
    (settings.out_dir / "05_calibration_report.md").write_text(
        "\n".join(
            [
                "# Calibration Report",
                "",
                f"- Champion model: `{champion_name}`",
                "- Confidence bands are derived from empirical absolute residual quantiles on the validation split.",
                f"- Median absolute error proxy: {policy['quantiles']['p50_abs_error']:.3f}",
                f"- P80 absolute error proxy: {policy['quantiles']['p80_abs_error']:.3f}",
                f"- P90 absolute error proxy: {policy['quantiles']['p90_abs_error']:.3f}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return policy

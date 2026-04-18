from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class PredictiveSettings:
    root: Path
    out_dir: Path
    models_dir: Path
    features: list[str]
    removed_features: list[str]
    target_cap: int
    target_column: str
    id_columns: list[str]
    group_columns: list[str]
    window_sizes: list[int]
    hgb_params: dict
    rf_params: dict
    lstm_params: dict
    gru_params: dict


def load_settings() -> PredictiveSettings:
    root = Path(__file__).resolve().parents[2]
    preprocessing = json.loads((root / "out" / "eda" / "05_preprocessing_config.json").read_text(encoding="utf-8"))
    return PredictiveSettings(
        root=root,
        out_dir=root / "out" / "predictive_layer",
        models_dir=root / "out" / "predictive_layer" / "models",
        features=preprocessing["selected_features"],
        removed_features=preprocessing["removed_low_variance_features"],
        target_cap=int(preprocessing["target_default_policy"]["default_cap"]),
        target_column=preprocessing["target_column"],
        id_columns=["dataset_id", "unit_id", "cycle"],
        group_columns=["dataset_id", "unit_id"],
        window_sizes=preprocessing["window_policy"]["recommended_window_lengths"],
        hgb_params={"learning_rate": 0.08, "max_depth": 6, "max_iter": 250, "min_samples_leaf": 40, "random_state": 42},
        rf_params={"n_estimators": 160, "max_depth": 18, "min_samples_leaf": 4, "n_jobs": -1, "random_state": 42},
        lstm_params={"hidden_size": 32, "epochs": 4, "batch_size": 128, "lr": 0.0015, "window_size": preprocessing["window_policy"]["recommended_window_lengths"][0]},
        gru_params={"hidden_size": 32, "epochs": 4, "batch_size": 128, "lr": 0.0015, "window_size": preprocessing["window_policy"]["recommended_window_lengths"][1]},
    )


def settings_as_dict(settings: PredictiveSettings) -> dict:
    data = asdict(settings)
    for key in ["root", "out_dir", "models_dir"]:
        data[key] = str(data[key])
    return data

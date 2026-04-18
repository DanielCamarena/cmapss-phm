from __future__ import annotations

import json
import os
from pathlib import Path

def write_phase1_docs(settings) -> None:
    from .io_utils import write_text

    write_text(
        settings.out_dir / "01_modeling_decisions_frozen.txt",
        "\n".join(
            [
                "Frozen modeling decisions",
                "",
                f"- Primary target: rul_capped with cap {settings.target_cap}",
                "- Secondary audit target: rul_linear",
                f"- Baseline features: {', '.join(settings.features)}",
                f"- Removed baseline-only features: {', '.join(settings.removed_features)}",
                "- Baseline models: HistGradientBoostingRegressor, RandomForestRegressor",
                "- Sequence challengers: LSTM, GRU",
                f"- Window sizes: {settings.window_sizes}",
                "- Validation policy: grouped by unit_id with cycle order preserved",
            ],
        ),
    )
    write_text(
        settings.out_dir / "01_model_comparison_protocol.txt",
        "\n".join(
            [
                "Model comparison protocol",
                "",
                "- Compare all models on capped validation targets.",
                "- Report RMSE and MAE globally and by dataset.",
                "- Report error by RUL band.",
                "- Record single-request latency.",
                "- Promote a non-tabular champion only if it clears the Plan 2 improvement or stability rule.",
            ],
        ),
    )


def write_contract_files(settings, champion_record: dict) -> None:
    from .inference_service import predict_rul
    from .io_utils import write_json

    input_schema = {
        "type": "object",
        "required": ["dataset_id", "unit_id", "cycle", "op_settings", "sensors"],
        "properties": {
            "dataset_id": {"type": "string"},
            "unit_id": {"type": "integer"},
            "cycle": {"type": "integer"},
            "op_settings": {"type": "object"},
            "sensors": {"type": "object"},
            "source": {"type": "string"},
        },
    }
    output_schema = {
        "type": "object",
        "required": ["rul_pred", "confidence_band", "model_version", "service_status", "trace", "timestamp"],
        "properties": {
            "rul_pred": {"type": ["number", "null"]},
            "confidence_band": {"type": ["object", "null"]},
            "model_version": {"type": ["string", "null"]},
            "service_status": {"type": "string"},
            "trace": {"type": ["object", "null"]},
            "timestamp": {"type": "string"},
        },
    }
    error_contract = {
        "error_validacion": {"meaning": "missing required fields or non-parsable feature values"},
        "fallback": {"meaning": "primary champion unavailable or insufficiently usable"},
        "degraded": {"meaning": "prediction delivered with reduced confidence or partial guarantees"},
        "sin_datos": {"meaning": "insufficient data to run the requested inference mode"},
    }
    example_request = {
        "dataset_id": "FD001",
        "unit_id": 1,
        "cycle": 50,
        "op_settings": {"op_setting_1": 0.1, "op_setting_2": -0.2},
        "sensors": {feature: 0.0 for feature in settings.features if feature.startswith("sensor_")},
        "source": "smoke_test",
    }
    write_json(settings.out_dir / "06_input_schema_v1.json", input_schema)
    write_json(settings.out_dir / "06_output_schema_v1.json", output_schema)
    write_json(settings.out_dir / "06_error_contract_v1.json", error_contract)
    write_json(
        settings.out_dir / "06_contract_examples.json",
        {"request": example_request, "response": predict_rul(example_request), "champion_record": champion_record},
    )


def run_smoke_test(settings, champion_record: dict) -> None:
    from .inference_service import predict_rul
    from .io_utils import write_json, write_text

    sample_payload = {
        "dataset_id": "FD001",
        "unit_id": 1,
        "cycle": 50,
        "op_settings": {"op_setting_1": 0.15, "op_setting_2": -0.12},
        "sensors": {feature: 0.0 for feature in settings.features if feature.startswith("sensor_")},
        "source": "local_smoke_test",
    }
    response = predict_rul(sample_payload)
    write_text(
        settings.out_dir / "07_smoke_test_e2e.txt",
        "\n".join(
            [
                "Predictive layer smoke test",
                "",
                f"Champion model: {champion_record['champion_model']}",
                f"Fallback model: {champion_record['fallback_model']}",
                f"Request payload keys: {list(sample_payload.keys())}",
                f"Response service status: {response['service_status']}",
                f"Response model version: {response['model_version']}",
                f"Response rul_pred: {response['rul_pred']}",
            ],
        ),
    )
    write_json(settings.out_dir / "07_smoke_response.json", response)
    latency_df_path = settings.out_dir / "04_latency_by_model.csv"
    if latency_df_path.exists():
        Path(settings.out_dir / "07_latency_e2e.csv").write_text(latency_df_path.read_text(encoding="utf-8"), encoding="utf-8")
    write_text(
        settings.out_dir / "07_dashboard_integration_report.md",
        "\n".join(
            [
                "# Dashboard Integration Report",
                "",
                "- The predictive layer returns a JSON-serializable payload with `rul_pred`, `confidence_band`, `model_version`, `service_status`, `trace`, and `timestamp`.",
                "- The champion is currently a tabular model, which keeps single-record dashboard integration straightforward.",
                "- Fallback behavior is explicit and marked via `service_status=fallback` when needed.",
            ],
        ),
    )


def write_release_docs(settings, champion_record: dict) -> None:
    from .io_utils import write_text

    write_text(
        settings.out_dir / "08_release_notes.md",
        "\n".join(
            [
                "# Predictive Layer Release Notes",
                "",
                f"- Champion model: `{champion_record['champion_model']}`",
                f"- Fallback model: `{champion_record['fallback_model']}`",
                "- Models trained: HGB, RF, LSTM, GRU",
                "- Metrics, calibration, robustness, and contract artifacts were generated from the Plan 1/Plan 2 pipeline.",
            ],
        ),
    )
    write_text(
        settings.out_dir / "08_residual_risks.md",
        "\n".join(
            [
                "# Residual Risks",
                "",
                "- Sequence challengers were trained on CPU with a lightweight configuration; they may improve with longer tuning cycles.",
                "- The current inference path is optimized for single-record tabular integration; sequence-serving would need explicit history payload support.",
                "- Condition-aware normalization remains a future enhancement for the most complex subsets.",
            ],
        ),
    )
    write_text(
        settings.out_dir / "08_next_steps_backlog.md",
        "\n".join(
            [
                "# Next Steps Backlog",
                "",
                "- Expose predictive outputs to `agent_layer` orchestration.",
                "- Add richer OOD checks and monitoring summaries.",
                "- Evaluate whether a longer-tuned sequence challenger can displace the current champion without harming integration readiness.",
            ],
        ),
    )
    write_text(
        settings.out_dir / "08_deploy_checklist.txt",
        "\n".join(
            [
                "Predictive layer deploy checklist",
                "",
                "- Conda environment `cmapss` available",
                "- Processed parquet artifacts present",
                "- Champion record and confidence-band policy present",
                "- Model artifacts stored under `out/predictive_layer/models`",
                "- Smoke test passes",
            ],
        ),
    )


def main() -> None:
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
    import torch

    from .calibration import build_calibration
    from .config import load_settings
    from .evaluate_models import evaluate_models
    from .io_utils import ensure_dirs
    from .robustness import run_robustness
    from .train_gru_or_tcn import train_gru
    from .train_hgb import train_hgb
    from .train_lstm import train_lstm
    from .train_rf import train_rf

    settings = load_settings()
    ensure_dirs(settings.out_dir, settings.models_dir, settings.root / "src" / "predictive_layer")
    write_phase1_docs(settings)

    train_hgb(settings)
    train_rf(settings)
    train_lstm(settings)
    train_gru(settings)

    champion_record = evaluate_models(settings)
    build_calibration(settings, champion_record)
    run_robustness(settings, champion_record)
    write_contract_files(settings, champion_record)
    run_smoke_test(settings, champion_record)
    write_release_docs(settings, champion_record)

    print("Plan 3 predictive layer execution complete.")
    print(f"Artifacts written to: {settings.out_dir}")


if __name__ == "__main__":
    main()

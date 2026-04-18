from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path

import pandas as pd

from src.agent_layer.config import load_settings as load_agent_settings
from src.agent_layer.orchestrator import orchestrate_prediction, run_scenario
from src.agent_layer.recommender import build_recommendation
from src.agent_layer.risk_engine import compute_risk
from src.agent_layer.tools import call_predictive_layer
from src.predictive_layer.config import load_settings as load_predictive_settings


ROOT = Path(__file__).resolve().parents[2]
RAW_SETTING_KEYS = [f"op_setting_{idx}" for idx in range(1, 4)]
RAW_SENSOR_KEYS = [f"sensor_{idx}" for idx in range(1, 22)]
RAW_REQUIRED_COLUMNS = ["dataset_id", "unit_id", "cycle", *RAW_SETTING_KEYS, *RAW_SENSOR_KEYS]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _build_raw_payload_from_sample() -> dict:
    sample = pd.read_csv(ROOT / "data" / "sample_input.csv").iloc[0].to_dict()
    return {
        "dataset_id": str(sample["dataset_id"]),
        "unit_id": int(sample["unit_id"]),
        "cycle": int(sample["cycle"]),
        "op_settings": {key: float(sample[key]) for key in RAW_SETTING_KEYS},
        "sensors": {key: float(sample[key]) for key in RAW_SENSOR_KEYS},
        "source": "dashboard.sample_input",
    }


def get_default_payload() -> dict:
    return deepcopy(_build_raw_payload_from_sample())


def load_configured_analysis_dataset() -> pd.DataFrame | None:
    configured_path = os.getenv("CMAPSS_DASHBOARD_DATASET_PATH")
    candidate_paths = [Path(configured_path)] if configured_path else [ROOT / "data" / "dashboard_dataset.csv"]
    for candidate in candidate_paths:
        if not candidate.exists():
            continue
        df = pd.read_csv(candidate)
        ok, _ = validate_uploaded_dataframe(df)
        if ok:
            return df[RAW_REQUIRED_COLUMNS].copy().reset_index(drop=True)
    return None


def validate_uploaded_dataframe(df: pd.DataFrame) -> tuple[bool, list[str]]:
    missing = [column for column in RAW_REQUIRED_COLUMNS if column not in df.columns]
    return len(missing) == 0, missing


def build_payload_from_row(row: pd.Series, source: str = "dashboard.upload") -> dict:
    return {
        "dataset_id": str(row["dataset_id"]),
        "unit_id": int(row["unit_id"]),
        "cycle": int(row["cycle"]),
        "op_settings": {key: float(row[key]) for key in RAW_SETTING_KEYS},
        "sensors": {key: float(row[key]) for key in RAW_SENSOR_KEYS},
        "source": source,
    }


def run_decision_flow(payload: dict) -> dict:
    return orchestrate_prediction(payload)


def run_scenario_flow(payload: dict, intent_text: str) -> dict:
    return run_scenario(payload, intent_text)


def load_model_comparison() -> pd.DataFrame:
    metrics = pd.read_csv(ROOT / "out" / "predictive_layer" / "04_metrics_global_by_model.csv")
    latency = pd.read_csv(ROOT / "out" / "predictive_layer" / "04_latency_by_model.csv")
    champion = load_json(ROOT / "out" / "predictive_layer" / "champion_record.json")
    metrics = metrics.merge(latency[["model_name", "ms_per_sample"]], on="model_name", how="left")
    metrics["stability_score"] = metrics["model_name"].map(champion["stability_spread_rmse"])
    metrics["model_type"] = metrics["model_name"].map(
        {"rf": "Tabular", "hgb": "Tabular", "lstm": "Sequence", "gru": "Sequence"}
    )
    metrics["highlight"] = metrics["model_name"].map(
        lambda name: "Champion" if name == champion["champion_model"] else ("Best raw RMSE" if name == champion["best_overall_model"] else "")
    )
    return metrics


def load_agent_audit_tail(limit: int = 5) -> list[dict]:
    path = ROOT / "out" / "agent_layer" / "audit_log.jsonl"
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    lines = [line for line in lines if line.strip()]
    return [json.loads(line) for line in lines[-limit:]][::-1]


def load_contract_snapshot() -> dict:
    return {
        "predictive_schema": load_json(ROOT / "out" / "predictive_layer" / "06_output_schema_v1.json"),
        "agent_input_schema": load_json(ROOT / "out" / "agent_layer" / "01_input_contract_v1.json"),
        "agent_output_schema": load_json(ROOT / "out" / "agent_layer" / "01_output_contract_v1.json"),
    }


def load_predictive_feature_list() -> list[str]:
    return load_predictive_settings().features


def _score_payload_for_analysis(payload: dict) -> dict:
    agent_settings = load_agent_settings()
    predictive = call_predictive_layer(payload)
    risk = compute_risk(
        predictive.get("rul_pred"),
        predictive.get("confidence_band"),
        predictive.get("service_status", "degraded"),
        agent_settings.risk_thresholds,
    )
    recommendation = build_recommendation(risk["risk_level"], predictive.get("service_status", "degraded"))
    return {
        "rul_pred": predictive.get("rul_pred"),
        "confidence_band": predictive.get("confidence_band"),
        "target_policy": predictive.get("target_policy"),
        "risk_level": risk["risk_level"],
        "risk_score": risk["risk_score"],
        "recommendation_text": recommendation["recommendation_text"],
        "recommendation_priority": recommendation["recommendation_priority"],
        "recommendation_alternatives": recommendation["recommendation_alternatives"],
        "rationale": risk["rationale"],
        "safety_notes": recommendation["safety_notes"],
        "model_version": predictive.get("model_version"),
        "service_status": predictive.get("service_status", "degraded"),
        "trace": predictive.get("trace"),
        "timestamp": predictive.get("timestamp"),
    }


def run_selected_unit_history(uploaded_df: pd.DataFrame, dataset_id: str, unit_id: int) -> pd.DataFrame:
    unit_df = uploaded_df[
        (uploaded_df["dataset_id"].astype(str) == str(dataset_id))
        & (uploaded_df["unit_id"].astype(int) == int(unit_id))
    ].sort_values("cycle")
    records: list[dict] = []
    for row in unit_df.to_dict("records"):
        payload = build_payload_from_row(pd.Series(row), source="dashboard.analysis.unit_history")
        scored = _score_payload_for_analysis(payload)
        records.append(
            {
                "dataset_id": str(row["dataset_id"]),
                "unit_id": int(row["unit_id"]),
                "cycle": int(row["cycle"]),
                "rul_pred": scored["rul_pred"],
                "risk_level": scored["risk_level"],
                "risk_score": scored["risk_score"],
                "recommendation_priority": scored["recommendation_priority"],
                "service_status": scored["service_status"],
                "confidence_lower": None if not scored["confidence_band"] else scored["confidence_band"]["lower"],
                "confidence_upper": None if not scored["confidence_band"] else scored["confidence_band"]["upper"],
            }
        )
    return pd.DataFrame(records)


def run_fleet_snapshot(uploaded_df: pd.DataFrame, dataset_id: str) -> pd.DataFrame:
    dataset_df = uploaded_df[uploaded_df["dataset_id"].astype(str) == str(dataset_id)].copy()
    if dataset_df.empty:
        return pd.DataFrame()
    snapshot_df = (
        dataset_df.sort_values(["unit_id", "cycle"])
        .groupby(["dataset_id", "unit_id"], as_index=False)
        .tail(1)
        .sort_values(["dataset_id", "unit_id"])
    )
    records: list[dict] = []
    for row in snapshot_df.to_dict("records"):
        payload = build_payload_from_row(pd.Series(row), source="dashboard.analysis.fleet_snapshot")
        scored = _score_payload_for_analysis(payload)
        records.append(
            {
                "dataset_id": str(row["dataset_id"]),
                "unit_id": int(row["unit_id"]),
                "last_cycle": int(row["cycle"]),
                "rul_pred": scored["rul_pred"],
                "risk_level": scored["risk_level"],
                "risk_score": scored["risk_score"],
                "recommendation_priority": scored["recommendation_priority"],
                "service_status": scored["service_status"],
                "model_version": scored["model_version"],
            }
        )
    return pd.DataFrame(records)

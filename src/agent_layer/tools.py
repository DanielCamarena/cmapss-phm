from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from src.predictive_layer.config import load_settings as load_predictive_settings
from src.predictive_layer.inference_service import predict_rul


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def append_jsonl(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")


def _trim_payload_for_predictive_model(payload: dict) -> dict:
    predictive_settings = load_predictive_settings()
    feature_set = set(predictive_settings.features)
    trimmed = {
        "dataset_id": payload["dataset_id"],
        "unit_id": payload["unit_id"],
        "cycle": payload["cycle"],
        "source": payload.get("source", "agent_layer"),
        "op_settings": {},
        "sensors": {},
    }
    for key, value in payload.get("op_settings", {}).items():
        if key in feature_set:
            trimmed["op_settings"][key] = value
    for key, value in payload.get("sensors", {}).items():
        if key in feature_set:
            trimmed["sensors"][key] = value
    if "operator_note" in payload:
        trimmed["operator_note"] = payload["operator_note"]
    if "request_context" in payload:
        trimmed["request_context"] = payload["request_context"]
    return trimmed


def call_predictive_layer(payload: dict) -> dict:
    return predict_rul(_trim_payload_for_predictive_model(payload))

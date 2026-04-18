from __future__ import annotations

import re
import json
import uuid

from .config import load_settings
from .recommender import build_recommendation
from .risk_engine import compute_risk
from .scenario_interpreter import compare_baseline_vs_scenario, generate_interpretation, optionally_enrich_explanation
from .scenario_rules import (
    DEFAULT_SCENARIO_PROMPT,
    build_scenario_payload,
    parse_intent_deterministically,
    validate_scenario,
)
from .llm_client import llm_available, parse_scenario_intent
from .tools import append_jsonl, call_predictive_layer, utc_now


def _validate_payload(payload: dict) -> tuple[bool, str | None]:
    for required in ["dataset_id", "unit_id", "cycle", "op_settings", "sensors"]:
        if required not in payload:
            return False, f"missing {required}"
    return True, None


def orchestrate_prediction(payload: dict) -> dict:
    settings = load_settings()
    ok, reason = _validate_payload(payload)
    if not ok:
        response = {
            "rul_pred": None,
            "confidence_band": None,
            "risk_level": "unknown",
            "risk_score": None,
            "recommendation_text": "Request validation failed before prediction.",
            "recommendation_priority": "P1",
            "recommendation_alternatives": ["Correct the request payload and retry."],
            "rationale": reason,
            "audit_record_id": str(uuid.uuid4()),
            "service_status": "error_validacion",
            "timestamp": utc_now(),
        }
        append_jsonl(settings.out_dir / "audit_log.jsonl", {"type": "decision", "payload": payload, "response": response})
        return response

    predictive = call_predictive_layer(payload)
    risk = compute_risk(
        predictive.get("rul_pred"),
        predictive.get("confidence_band"),
        predictive.get("service_status", "degraded"),
        settings.risk_thresholds,
    )
    recommendation = build_recommendation(risk["risk_level"], predictive.get("service_status", "degraded"))
    audit_record_id = str(uuid.uuid4())
    response = {
        "rul_pred": predictive.get("rul_pred"),
        "confidence_band": predictive.get("confidence_band"),
        "risk_level": risk["risk_level"],
        "risk_score": risk["risk_score"],
        "recommendation_text": recommendation["recommendation_text"],
        "recommendation_priority": recommendation["recommendation_priority"],
        "recommendation_alternatives": recommendation["recommendation_alternatives"],
        "rationale": risk["rationale"],
        "safety_notes": recommendation["safety_notes"],
        "model_version": predictive.get("model_version"),
        "trace": predictive.get("trace"),
        "audit_record_id": audit_record_id,
        "service_status": predictive.get("service_status", "degraded"),
        "timestamp": utc_now(),
    }
    append_jsonl(
        settings.out_dir / "audit_log.jsonl",
        {"type": "decision", "audit_record_id": audit_record_id, "request": payload, "predictive": predictive, "response": response},
    )
    return response


def parse_intent(intent_text: str, model_name: str) -> tuple[list[dict], str, str | None, list[str]]:
    normalized = re.sub(r"\s+", " ", (intent_text or "").strip())
    parse_errors: list[str] = []
    if not normalized:
        return [], "rules_only", None, ["Scenario input is empty. Provide instructions like `cycle +25; sensor_11 -0.1`."]

    deterministic_changes, deterministic_errors = parse_intent_deterministically(normalized)
    if not deterministic_errors and deterministic_changes:
        return deterministic_changes, "deterministic", None, []

    if llm_available():
        llm_changes, used_model = parse_scenario_intent(normalized, model_name)
        if llm_changes:
            return llm_changes, "llm-assisted", used_model, []

    if deterministic_errors:
        parse_errors.extend(deterministic_errors)
    return deterministic_changes, "deterministic", None, parse_errors


def _invalid_scenario_response(payload: dict, intent_text: str, errors: list[str], parsing_mode: str, llm_model_used: str | None) -> dict:
    settings = load_settings()
    baseline = orchestrate_prediction(payload)
    assistant_mode = "llm_enabled" if llm_model_used else "rules_only"
    response = {
        "input_text": intent_text,
        "parsed_changes": {"changes": []},
        "proposed_payload": payload,
        "change_summary": [],
        "assumptions": ["No scenario changes were applied because the request could not be parsed or validated."],
        "safety_notes": [
            "Scenario execution is blocked until parsing and validation errors are resolved.",
            "Prediction, risk scoring, and comparison remain deterministic once a valid scenario is supplied.",
        ],
        "comparison": {
            "baseline_rul": baseline.get("rul_pred"),
            "scenario_rul": None,
            "delta_rul": None,
            "baseline_risk_score": baseline.get("risk_score"),
            "scenario_risk_score": None,
            "delta_risk_score": None,
            "baseline_risk_level": baseline.get("risk_level"),
            "scenario_risk_level": "unknown",
        },
        "comparison_interpretation": "Scenario request could not be executed because parsing or validation failed.",
        "operator_guidance": "Review the validation messages, correct the scenario instructions, and retry.",
        "assistant_mode": assistant_mode,
        "parsing_mode": parsing_mode,
        "llm_used": bool(llm_model_used),
        "llm_model_used": llm_model_used,
        "service_status": "error_validacion",
        "validation_errors": errors,
        "baseline": baseline,
        "scenario": None,
        "timestamp": utc_now(),
    }
    append_jsonl(settings.out_dir / "audit_log.jsonl", {"type": "scenario_invalid", "request": payload, "response": response})
    return response


def run_baseline_prediction(payload: dict) -> dict:
    return orchestrate_prediction(payload)


def run_scenario_prediction(payload: dict) -> dict:
    return orchestrate_prediction(payload)


def run_scenario(payload: dict, intent_text: str | None = None) -> dict:
    settings = load_settings()
    scenario_text = (intent_text or "").strip() or DEFAULT_SCENARIO_PROMPT
    structured_changes, parsing_mode, llm_model_used, parse_errors = parse_intent(scenario_text, settings.llm_model or "gemini-2.5-flash")
    if parse_errors:
        return _invalid_scenario_response(payload, scenario_text, parse_errors, parsing_mode, llm_model_used)

    valid, validation_errors = validate_scenario(payload, structured_changes)
    if not valid:
        return _invalid_scenario_response(payload, scenario_text, validation_errors, parsing_mode, llm_model_used)

    proposed_payload, change_summary, assumptions, safety_notes = build_scenario_payload(payload, structured_changes)
    baseline = run_baseline_prediction(payload)
    scenario_prediction = run_scenario_prediction(proposed_payload)
    comparison = compare_baseline_vs_scenario(baseline, scenario_prediction)
    interpretation = generate_interpretation(change_summary, comparison)
    assistant_mode = "llm_enabled" if llm_model_used else "rules_only"
    if llm_available():
        interpretation, explanation_model_used = optionally_enrich_explanation(interpretation, settings.llm_model or "gemini-2.5-flash")
        if explanation_model_used:
            llm_model_used = explanation_model_used
            assistant_mode = "llm_enabled"
    response = {
        "input_text": scenario_text,
        "parsed_changes": {"changes": structured_changes},
        "proposed_payload": proposed_payload,
        "structured_changes": structured_changes,
        "change_summary": change_summary,
        "assumptions": assumptions,
        "safety_notes": safety_notes,
        "comparison": comparison,
        **interpretation,
        "validation_errors": [],
        "assistant_mode": assistant_mode,
        "parsing_mode": parsing_mode,
        "llm_used": bool(llm_model_used),
        "llm_model_used": llm_model_used,
        "baseline": baseline,
        "scenario": scenario_prediction,
        "service_status": scenario_prediction.get("service_status", "degraded"),
        "timestamp": utc_now(),
    }
    append_jsonl(settings.out_dir / "audit_log.jsonl", {"type": "scenario", "request": payload, "response": response})
    return response

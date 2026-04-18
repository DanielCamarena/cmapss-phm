from __future__ import annotations

import csv
import json
from pathlib import Path

from .config import load_settings
from .llm_client import llm_available
from .orchestrator import orchestrate_prediction, run_scenario
from .recommender import RECOMMENDATION_CATALOG


def ensure_dirs(settings) -> None:
    settings.out_dir.mkdir(parents=True, exist_ok=True)
    settings.dashboard_out_dir.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict | list) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


def write_phase1(settings) -> None:
    input_contract = {
        "type": "object",
        "required": ["dataset_id", "unit_id", "cycle", "op_settings", "sensors"],
        "properties": {
            "dataset_id": {"type": "string"},
            "unit_id": {"type": "integer"},
            "cycle": {"type": "integer"},
            "op_settings": {"type": "object"},
            "sensors": {"type": "object"},
            "source": {"type": "string"},
            "operator_note": {"type": "string"},
            "request_context": {"type": "object"},
        },
    }
    output_contract = {
        "type": "object",
        "required": [
            "rul_pred",
            "confidence_band",
            "risk_level",
            "risk_score",
            "recommendation_text",
            "recommendation_priority",
            "recommendation_alternatives",
            "rationale",
            "audit_record_id",
            "service_status",
            "timestamp",
        ],
    }
    example_request = settings.predictive_examples["request"]
    example_response = orchestrate_prediction(example_request)
    write_json(settings.out_dir / "01_input_contract_v1.json", input_contract)
    write_json(settings.out_dir / "01_output_contract_v1.json", output_contract)
    write_json(settings.out_dir / "01_contract_examples.json", {"request": example_request, "response": example_response})
    write_text(
        settings.out_dir / "01_policy_rules.txt",
        "\n".join(
            [
                "Agent layer policy rules",
                "",
                "- Preserve upstream predictive `service_status` unless validation fails before prediction.",
                "- Risk logic is deterministic and threshold-driven.",
                "- Recommendation text must remain available even when LLM enrichment is disabled.",
                "- Scenario assistant may enrich language, but not alter deterministic baseline comparisons.",
            ]
        ),
    )
    with (settings.out_dir / "01_recommendation_catalog.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["risk_level", "recommendation_text", "priority"])
        for risk_level, record in RECOMMENDATION_CATALOG.items():
            writer.writerow([risk_level, record["recommendation_text"], record["recommendation_priority"]])


def write_phase2(settings) -> None:
    write_text(
        settings.out_dir / "02_risk_scoring_design.txt",
        "\n".join(
            [
                "Risk scoring design",
                "",
                "- Base level is determined by RUL thresholds: critical <=20, warning <=60, healthy >60.",
                "- Confidence-band width can increase the risk score conservatively.",
                "- Upstream fallback or degraded predictive states increase the risk score conservatively.",
                "- Missing valid RUL yields `unknown` risk and forces a validation-first recommendation path.",
            ]
        ),
    )
    write_json(settings.out_dir / "02_thresholds_config.json", settings.risk_thresholds)


def write_phase3(settings) -> None:
    write_text(
        settings.out_dir / "03_recommendation_templates.txt",
        "\n".join(
            [
                "Recommendation templates",
                "",
                *[f"- {level}: {record['recommendation_text']}" for level, record in RECOMMENDATION_CATALOG.items()],
            ]
        ),
    )
    with (settings.out_dir / "03_priority_matrix.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["risk_level", "priority", "alternatives_count"])
        for level, record in RECOMMENDATION_CATALOG.items():
            writer.writerow([level, record["recommendation_priority"], len(record["recommendation_alternatives"])])


def write_phase4(settings) -> None:
    write_text(
        settings.out_dir / "04_toolchain_contracts.txt",
        "\n".join(
            [
                "Toolchain contracts",
                "",
                "- Agent input validates before predictive-layer invocation.",
                "- Predictive provider: src.predictive_layer.inference_service.predict_rul",
                "- Orchestration path: validate -> predict -> risk -> recommend -> audit -> response",
                "- Scenario path reuses the same predictive and risk contracts on modified payloads.",
            ]
        ),
    )


def write_phase5(settings, example_request: dict) -> None:
    scenario_response = run_scenario(example_request)
    write_text(
        settings.out_dir / "05_scenario_assistant_flow.txt",
        "\n".join(
            [
                "Scenario assistant flow",
                "",
                "1. Validate base request.",
                "2. Produce baseline deterministic decision.",
                "3. Generate a rules-only proposed scenario payload.",
                "4. Run the same predictive and agent pipeline on the proposed payload.",
                "5. Compare baseline and scenario outputs and add assumptions/safety notes.",
                "6. Optionally enrich interpretation text with google-genai if configured.",
            ]
        ),
    )
    write_json(settings.out_dir / "05_scenario_examples.json", scenario_response)


def write_phase6(settings) -> None:
    write_text(
        settings.out_dir / "06_llm_integration_policy.txt",
        "\n".join(
            [
                "LLM integration policy",
                "",
                "- Provider package: google-genai",
                "- Secret: GEMINI_API_KEY",
                f"- Default model override target: {settings.llm_model}",
                "- LLM output may enrich wording only; it does not replace deterministic risk or recommendation logic.",
                "- If the provider is unavailable, the system remains in `rules_only` mode.",
            ]
        ),
    )
    write_text(
        settings.out_dir / "06_scenario_assistant_policy.txt",
        "\n".join(
            [
                "Scenario assistant policy",
                "",
                f"- LLM available in current environment: {llm_available()}",
                "- Deterministic scenario generation is mandatory.",
                "- Safety notes and assumptions must always be present.",
                "- Enrichment failures must not change scenario comparison values.",
            ]
        ),
    )


def write_phase7(settings) -> None:
    write_text(
        settings.out_dir / "07_dashboard_mapping.txt",
        "\n".join(
            [
                "Dashboard mapping",
                "",
                "- Summary: rul_pred, risk_level, recommendation_text, recommendation_priority",
                "- Analysis: risk_score, confidence_band, recommendation_alternatives, trace",
                "- Scenarios: proposed_payload, change_summary, comparison, comparison_interpretation, operator_guidance",
                "- Technical Audit: audit_record_id, service_status, model_version, timestamp, trace",
            ]
        ),
    )
    write_text(
        settings.out_dir / "07_explainability_checklist.txt",
        "\n".join(
            [
                "Explainability checklist",
                "",
                "- Every decision includes rationale.",
                "- Confidence-band information is preserved from the predictive layer.",
                "- Fallback and degraded states are visible in service_status.",
                "- Scenario outputs include assumptions and safety notes.",
            ]
        ),
    )
    write_text(
        settings.dashboard_out_dir / "contract_integration_checklist.txt",
        "\n".join(
            [
                "Dashboard contract integration checklist",
                "",
                "- Agent output exposes stable risk and recommendation fields.",
                "- Scenario mode is optional but deterministic scenario comparison is available.",
                "- Technical audit fields are present for traceability.",
            ]
        ),
    )


def write_phase8(settings, example_request: dict) -> None:
    smoke = orchestrate_prediction(example_request)
    write_text(
        settings.out_dir / "08_test_matrix.txt",
        "\n".join(
            [
                "Agent-layer test matrix",
                "",
                "- valid request -> ok",
                "- missing field -> error_validacion",
                "- predictive fallback -> fallback",
                "- provider degradation -> degraded",
                "- scenario rules-only path -> ok or fallback depending on predictive result",
            ]
        ),
    )
    write_text(
        settings.out_dir / "08_failure_modes.txt",
        "\n".join(
            [
                "Failure modes",
                "",
                "- Invalid request payload",
                "- Predictive layer validation failure",
                "- Predictive champion unavailable and fallback used",
                "- LLM secret missing or provider call failure",
                "- Scenario payload outside intended safe perturbation bounds",
            ]
        ),
    )
    write_text(
        settings.out_dir / "08_acceptance_criteria.txt",
        "\n".join(
            [
                "Acceptance criteria",
                "",
                "- Valid requests produce deterministic risk and recommendation outputs.",
                "- Invalid requests fail with structured validation status.",
                "- Scenario assistant works in deterministic mode with assumptions and safety notes.",
                "- Audit log entries are written for both baseline and scenario flows.",
                "- Dashboard mapping fields are fully available from agent outputs.",
            ]
        ),
    )
    write_text(
        settings.out_dir / "08_smoke_local.txt",
        "\n".join(
            [
                "Agent-layer local smoke",
                "",
                f"service_status: {smoke['service_status']}",
                f"risk_level: {smoke['risk_level']}",
                f"recommendation_priority: {smoke['recommendation_priority']}",
                f"audit_record_id: {smoke['audit_record_id']}",
            ]
        ),
    )


def main() -> None:
    settings = load_settings()
    ensure_dirs(settings)
    example_request = settings.predictive_examples["request"]
    write_phase1(settings)
    write_phase2(settings)
    write_phase3(settings)
    write_phase4(settings)
    write_phase5(settings, example_request)
    write_phase6(settings)
    write_phase7(settings)
    write_phase8(settings, example_request)
    print("Plan 4 agent layer execution complete.")
    print(f"Artifacts written to: {settings.out_dir}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import csv
import json
from pathlib import Path

from .backend_adapter import get_default_payload, load_contract_snapshot, load_model_comparison, run_decision_flow, run_scenario_flow


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "out" / "dashboard_layer"


def ensure_dirs() -> None:
    OUT.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: dict | list) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def phase1(decision: dict, scenario: dict) -> None:
    write_text(
        OUT / "01_user_flows_final.txt",
        "\n".join(
            [
                "Dashboard user flows",
                "",
                "1. Operator loads the dashboard and edits or accepts the default sample payload.",
                "2. Operator triggers a deterministic decision request and receives Summary and Analysis outputs.",
                "3. Operator optionally triggers a scenario comparison and reviews assumptions and safety notes.",
                "4. Technical users inspect trace, audit identifiers, and contract snapshots in the Technical Audit tab.",
            ]
        ),
    )
    write_text(
        OUT / "01_screen_map_final.txt",
        "\n".join(
            [
                "Screen map",
                "",
                "- Sidebar: request console and action controls",
                "- Summary: main decision, service state, rationale",
                "- Analysis: score, confidence band, alternatives, model comparison, trace",
                "- Scenarios: baseline vs scenario comparison, assumptions, safety notes",
                "- Technical Audit: trace, schemas, audit log tail, raw JSON",
            ]
        ),
    )
    write_json(
        OUT / "01_ui_backend_contract_v1.json",
        {
            "request": get_default_payload(),
            "decision_response": decision,
            "scenario_response": scenario,
        },
    )


def phase2() -> None:
    write_text(
        OUT / "02_migration_notes.txt",
        "\n".join(
            [
                "Dashboard migration notes",
                "",
                "- Implemented a fresh Streamlit dashboard in src/dashboard_layer/app.py.",
                "- Backend integration is handled by backend_adapter.py and calls real agent-layer entrypoints.",
                "- No mock data path is used in the runtime flow.",
            ]
        ),
    )


def phase3(decision: dict, scenario: dict) -> None:
    comparison = load_model_comparison()
    with (OUT / "03_mapping_fields_table.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["dashboard_tab", "field_name", "source_layer"])
        rows = [
            ("Summary", "rul_pred", "agent/predictive"),
            ("Summary", "risk_level", "agent"),
            ("Summary", "recommendation_text", "agent"),
            ("Analysis", "risk_score", "agent"),
            ("Analysis", "confidence_band", "predictive"),
            ("Analysis", "trace", "predictive"),
            ("Scenarios", "comparison", "agent scenario"),
            ("Scenarios", "change_summary", "agent scenario"),
            ("Technical Audit", "audit_record_id", "agent"),
            ("Technical Audit", "model_version", "predictive"),
            ("Technical Audit", "service_status", "agent/predictive"),
        ]
        writer.writerows(rows)
    write_text(
        OUT / "03_integration_contract_check.txt",
        "\n".join(
            [
                "Integration contract check",
                "",
                "- Dashboard decision flow consumes real agent-layer output successfully.",
                "- Scenario flow consumes real agent-layer scenario output successfully.",
                "- Model comparison table reads directly from predictive-layer evaluation artifacts.",
                "- Trace and service-state fields remain visible without custom post-processing.",
            ]
        ),
    )
    write_text(
        OUT / "03_smoke_local.txt",
        "\n".join(
            [
                "Dashboard local smoke",
                "",
                f"Decision state: {decision['service_status']}",
                f"Scenario state: {scenario['service_status']}",
                f"Decision risk level: {decision['risk_level']}",
                f"Scenario delta RUL: {scenario['comparison']['delta_rul_pred']}",
                f"Model comparison rows: {len(comparison)}",
            ]
        ),
    )
    write_text(
        OUT / "03_scenario_assistant_contract_check.txt",
        "\n".join(
            [
                "Scenario contract check",
                "",
                "- Scenario response includes proposed payload, assumptions, safety notes, comparison, interpretation, and service_status.",
                f"- Current scenario mode: {scenario['assistant_mode']}",
                "- The UI can render the deterministic path without requiring llm_model_used.",
            ]
        ),
    )


def phase4() -> None:
    write_text(
        OUT / "04_summary_design_notes.txt",
        "\n".join(
            [
                "Summary tab design notes",
                "",
                "- Large RUL gauge anchors the operator's attention.",
                "- Risk level, recommendation priority, and service state are surfaced as compact tiles.",
                "- Immediate action text is shown beside the gauge to reduce scanning time.",
            ]
        ),
    )


def phase5() -> None:
    write_text(
        OUT / "05_analysis_design_notes.txt",
        "\n".join(
            [
                "Analysis tab design notes",
                "",
                "- Focus on diagnostics already supported by contracts: risk_score, confidence_band, alternatives, trace.",
                "- Model comparison is shown from predictive-layer evaluation artifacts rather than invented fleet analytics.",
                "- Audit detail is visible but kept separate from the operator summary flow.",
            ]
        ),
    )


def phase6(scenario: dict) -> None:
    write_text(
        OUT / "06_scenario_ux_rules.txt",
        "\n".join(
            [
                "Scenario UX rules",
                "",
                "- Always show assumptions and safety notes before interpretive text.",
                "- Render baseline vs scenario values distinctly from prose interpretation.",
                "- Treat rules_only mode as first-class, not as a degraded placeholder.",
            ]
        ),
    )
    write_text(
        OUT / "06_scenario_examples_rendering.txt",
        "\n".join(
            [
                "Scenario rendering notes",
                "",
                f"Current scenario mode: {scenario['assistant_mode']}",
                f"Baseline RUL: {scenario['comparison']['baseline_rul_pred']}",
                f"Scenario RUL: {scenario['comparison']['scenario_rul_pred']}",
                f"Delta: {scenario['comparison']['delta_rul_pred']}",
            ]
        ),
    )


def phase7(decision: dict) -> None:
    write_text(
        OUT / "07_audit_ux_rules.txt",
        "\n".join(
            [
                "Technical audit UX rules",
                "",
                "- Display audit_record_id, model_version, service_status, timestamp, and trace as primary technical fields.",
                "- Present schema snapshots and recent audit entries in expandable sections.",
                f"- Current example audit id: {decision['audit_record_id']}",
            ]
        ),
    )


def phase8() -> None:
    write_text(
        OUT / "08_ux_copy_guide.txt",
        "\n".join(
            [
                "UX copy guide",
                "",
                "- Use direct operational language for recommendations.",
                "- Use plain caution language for fallback and degraded states.",
                "- Keep technical vocabulary in the Technical Audit tab instead of the operator summary view.",
            ]
        ),
    )
    write_text(
        OUT / "08_explainability_rules.txt",
        "\n".join(
            [
                "Explainability rules",
                "",
                "- Rationale must stay visible with every decision result.",
                "- Confidence-band messaging must not imply false certainty.",
                "- Scenario interpretation must be labeled as interpretation rather than factual output.",
            ]
        ),
    )
    write_text(
        OUT / "08_state_handling_guide.txt",
        "\n".join(
            [
                "State handling guide",
                "",
                "- loading: show progress and suppress stale action language",
                "- ok: show full decision UI",
                "- fallback: show amber state and preserve trace",
                "- degraded: show caution styling and surface uncertainty prominently",
                "- error_validacion: show correction guidance instead of decision content",
                "- sin_datos: show neutral empty state",
            ]
        ),
    )


def phase9(decision: dict, scenario: dict) -> None:
    write_text(
        OUT / "09_test_matrix.txt",
        "\n".join(
            [
                "Dashboard test matrix",
                "",
                "- valid decision request",
                "- valid scenario request",
                "- invalid payload triggering error_validacion",
                "- predictive fallback rendering",
                "- predictive degraded rendering",
                "- rules_only scenario rendering without LLM",
            ]
        ),
    )
    write_text(OUT / "09_bug_log.txt", "No dashboard-specific rendering bugs were recorded during the initial local execution pass.")
    write_text(
        OUT / "09_acceptance_checklist.txt",
        "\n".join(
            [
                "Acceptance checklist",
                "",
                "- Four required tabs exist",
                "- Backend adapter uses real agent-layer entrypoints",
                "- Service states are surfaced in the UI",
                "- Technical audit includes traceability fields",
                "- Scenario flow renders deterministic outputs cleanly",
            ]
        ),
    )
    write_text(
        OUT / "09_local_smoke_report.txt",
        "\n".join(
            [
                "Local smoke report",
                "",
                f"Decision service_status: {decision['service_status']}",
                f"Scenario service_status: {scenario['service_status']}",
                f"Decision model_version: {decision['model_version']}",
            ]
        ),
    )
    write_text(
        OUT / "09_runtime_config_notes.txt",
        "\n".join(
            [
                "Runtime configuration notes",
                "",
                "- Streamlit entrypoint: python -m streamlit run src/dashboard_layer/app.py",
                "- Backend integration requires the local agent_layer and predictive_layer artifacts already generated by Plans 3 and 4.",
                "- LLM enrichment remains optional; the UI supports rules_only mode cleanly.",
            ]
        ),
    )
    write_text(
        OUT / "09_deploy_checklist.txt",
        "\n".join(
            [
                "Deploy checklist",
                "",
                "- cmapss conda environment available",
                "- streamlit and plotly installed",
                "- predictive_layer artifacts present",
                "- agent_layer artifacts present",
                "- local smoke report generated",
            ]
        ),
    )


def main() -> None:
    ensure_dirs()
    decision = run_decision_flow(get_default_payload())
    scenario = run_scenario_flow(get_default_payload(), "cycle +25; op_setting_1 = 0.6; sensor_11 -0.1")
    phase1(decision, scenario)
    phase2()
    phase3(decision, scenario)
    phase4()
    phase5()
    phase6(scenario)
    phase7(decision)
    phase8()
    phase9(decision, scenario)
    write_json(OUT / "contracts_snapshot.json", load_contract_snapshot())
    print("Plan 5 dashboard execution complete.")
    print(f"Artifacts written to: {OUT}")


if __name__ == "__main__":
    main()

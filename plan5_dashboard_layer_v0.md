# Plan 5 - Final Dashboard Layer
Plan ID: `plan5_dashboard_layer`  
Layer: `dashboard_layer` (Layer 3 / capa3)  
Version: `v1.0`  
Status: `active`  
Depends on: `plan3_predictive_layer`, `plan4_agent_layer`  
Last updated: `2026-04-17`

## Goal
Deliver the final product dashboard in `src/dashboard_layer` integrated with contracts from `predictive_layer` and `agent_layer`.

## Scope
- Final UX for PHM operation.
- Contract-based integration.
- Robust status/error handling.
- Local deployment readiness.

## Required Structure
- `src/dashboard_layer/app.py`
- `src/dashboard_layer/components.py`
- `src/dashboard_layer/backend_adapter.py`
- `src/dashboard_layer/contracts/`
- `src/dashboard_layer/assets/`
- `out/dashboard_layer/`

## Final UI Structure (aligned with implementation)
- `Summary`
- `Analysis`
- `Scenarios`
- `Technical Audit`

## Core Inputs and Outputs
### UI Input
- `dataset_id`, `unit_id`, `cycle`, `op_settings[3]`, `sensors[21]`, `source`

### Agent-layer output consumed by dashboard
- `rul_pred`, `confidence_band`
- `risk_level`, `risk_score`
- `recommendation_text`, `recommendation_priority`, `recommendation_alternatives`
- `rationale`, `audit_record_id`, `service_status`, `timestamp`
- `history` (optional), `dashboard_note` (optional)

### Scenario output consumed by dashboard
- `proposed_payload`, `change_summary`, `assumptions`, `safety_notes`
- `comparison` and deltas
- `comparison_interpretation`, `operator_guidance`
- `assistant_mode`, `llm_model_used` (optional), `service_status`

## Mandatory App States
- `sin_datos`
- `loading`
- `ok`
- `error_validacion`
- `degraded`

## Phase 1 - Product Definition and UI Contract Freeze
### Deliverables
- `out/dashboard_layer/01_user_flows_final.txt`
- `out/dashboard_layer/01_screen_map_final.txt`
- `out/dashboard_layer/01_ui_backend_contract_v1.json`

## Phase 2 - Final Code Migration and Structure
### Tasks
1. Ensure dashboard runs from `src/dashboard_layer/app.py`.
2. Ensure adapter path uses `agent_layer.orchestrate_prediction`.
3. Remove runtime dependence on legacy mock paths.

### Deliverables
- `out/dashboard_layer/02_migration_notes.txt`

## Phase 3 - Integration with Layers 1 and 2
### Deliverables
- `out/dashboard_layer/03_integration_contract_check.txt`
- `out/dashboard_layer/03_mapping_fields_table.csv`
- `out/dashboard_layer/03_smoke_local.txt`
- `out/dashboard_layer/03_scenario_assistant_contract_check.txt`

## Phase 4 - UX and Explainability
### Tasks
1. `Summary`: KPI + immediate action + quick trend.
2. `Analysis`: fleet stats, unit history, top-risk ranking, model comparisons.
3. `Scenarios`: prompt, diff, interpretation, baseline vs scenario.
4. `Technical Audit`: traceability, model metadata, technical JSON.

### Deliverables
- `out/dashboard_layer/04_ux_copy_guide.txt`
- `out/dashboard_layer/04_explainability_rules.txt`
- `out/dashboard_layer/04_scenario_ux_rules.txt`

## Phase 5 - QA and Regression
### Deliverables
- `out/dashboard_layer/05_test_matrix.txt`
- `out/dashboard_layer/05_bug_log.txt`
- `out/dashboard_layer/05_acceptance_checklist.txt`
- `out/dashboard_layer/05_scenario_test_report.txt`

## Phase 6 - Local Operation Readiness
### Tasks
1. Validate local entrypoint and dependency setup.
2. Validate local secret handling (`GEMINI_API_KEY`, optional `GEMINI_MODEL`).
3. Validate degraded behavior when agent/LLM is unavailable.

### Deliverables
- `out/dashboard_layer/06_deploy_checklist.txt`
- `out/dashboard_layer/06_local_smoke_report.txt`
- `out/dashboard_layer/06_runtime_config_notes.txt`

## Success Criteria
- Final dashboard is stable in local environment.
- End-to-end flow uses real contracts from Layer 1 and Layer 2.
- Scenario workflow is safe, explainable, and traceable.

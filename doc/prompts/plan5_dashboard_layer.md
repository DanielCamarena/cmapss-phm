# Plan 5 - Dashboard Layer Implementation
Plan ID: `plan5_dashboard_layer`  
Layer: `dashboard_layer` (Layer 3)  
Version: `v1.0`  
Status: `active`  
Depends on: `plan3_predictive_layer`, `plan4_agent_layer`  
Last updated: `2026-04-17`  
Detailed source: `prompt.md`

## Goal
Implement the final dashboard in `src/dashboard_layer` using the real contracts already exposed by `predictive_layer` and `agent_layer`, with clear service-state handling, scenario support, and traceable technical audit views.

## Scope
- UI location: `src/dashboard_layer/*`
- Integration inputs: `out/predictive_layer/*`, `out/agent_layer/*`, `out/dashboard_layer/*`
- Final tabs: `Summary`, `Analysis`, `Scenarios`, `Technical Audit`
- Main responsibilities: contract-based integration, dashboard orchestration, service-state UX, explainability, and local operation readiness

## Preconditions
1. Activate environment: `conda activate cmapss`
2. Confirm Plan 3 and Plan 4 smoke artifacts exist and pass.
3. Confirm the current integration checklist exists in `out/dashboard_layer/contract_integration_checklist.txt`.
4. Ensure `src/dashboard_layer` exists or is created before implementation begins.

## Frozen Upstream Contracts
- Predictive-layer output provides: `rul_pred`, `confidence_band`, `target_policy`, `model_version`, `service_status`, `trace`, `timestamp`
- Agent-layer output provides: predictive fields plus `risk_level`, `risk_score`, `recommendation_text`, `recommendation_priority`, `recommendation_alternatives`, `rationale`, `audit_record_id`, `service_status`, `timestamp`
- Scenario output provides: `proposed_payload`, `change_summary`, `assumptions`, `safety_notes`, `comparison`, `comparison_interpretation`, `operator_guidance`, `assistant_mode`, `llm_model_used`, `service_status`
- Service states already in use: `ok`, `fallback`, `degraded`, `error_validacion`, `sin_datos`

## Required Structure
- `src/dashboard_layer/app.py`
- `src/dashboard_layer/components.py`
- `src/dashboard_layer/backend_adapter.py`
- `src/dashboard_layer/contracts/`
- `src/dashboard_layer/assets/`
- `out/dashboard_layer/`

## Final UI Structure
- `Summary`
- `Analysis`
- `Scenarios`
- `Technical Audit`

## Core Inputs and Outputs
### UI Input
- `dataset_id`, `unit_id`, `cycle`
- `op_settings`
- `sensors`
- optional `source`, `operator_note`, `request_context`

### Agent-layer output consumed by dashboard
- `rul_pred`, `confidence_band`
- `risk_level`, `risk_score`
- `recommendation_text`, `recommendation_priority`, `recommendation_alternatives`
- `rationale`, `audit_record_id`, `service_status`, `timestamp`
- `model_version`, `trace`, `safety_notes`

### Scenario output consumed by dashboard
- `proposed_payload`, `change_summary`, `assumptions`, `safety_notes`
- `comparison`
- `comparison_interpretation`, `operator_guidance`
- `assistant_mode`, `llm_model_used`, `service_status`, `timestamp`

## Mandatory App States
- `sin_datos`
- `loading`
- `ok`
- `fallback`
- `degraded`
- `error_validacion`

## Phase 1 - Product Definition and Contract Freeze
### Tasks
1. Freeze the UI-to-agent request contract and the dashboard-consumed response contract.
2. Define the state model for `loading`, `ok`, `fallback`, `degraded`, `error_validacion`, and `sin_datos`.
3. Map each upstream field to a dashboard location and visibility rule.
4. Define the minimum viable end-to-end user flow for a single-unit decision request.

### Deliverables
- `out/dashboard_layer/01_user_flows_final.txt`
- `out/dashboard_layer/01_screen_map_final.txt`
- `out/dashboard_layer/01_ui_backend_contract_v1.json`

### Exit Criteria
- The dashboard contract is explicit enough for implementation without guessing field names.
- Every service state has a UI behavior definition.
- The minimum end-to-end flow is frozen before component implementation begins.

## Phase 2 - Code Skeleton and Runtime Structure
### Tasks
1. Create the dashboard package structure in `src/dashboard_layer`.
2. Implement the local entrypoint in `src/dashboard_layer/app.py`.
3. Create a backend adapter that calls the agent-layer orchestration entrypoints instead of any mock service.
4. Define reusable UI components and asset organization.

### Deliverables
- `src/dashboard_layer/app.py`
- `src/dashboard_layer/components.py`
- `src/dashboard_layer/backend_adapter.py`
- `src/dashboard_layer/contracts/`
- `src/dashboard_layer/assets/`
- `out/dashboard_layer/02_migration_notes.txt`

### Exit Criteria
- The dashboard can start from the intended entrypoint.
- The runtime path uses real layer integration rather than placeholder data.
- Component boundaries are clear enough to support iteration without UI regression.

## Phase 3 - Integration with Predictive and Agent Layers
### Tasks
1. Wire dashboard requests to `agent_layer.orchestrate_prediction`.
2. Wire scenario requests to `agent_layer.run_scenario`.
3. Preserve predictive and agent traceability fields all the way to the UI.
4. Validate that the dashboard can consume fallback and degraded outputs without breaking layout logic.

### Deliverables
- `out/dashboard_layer/03_integration_contract_check.txt`
- `out/dashboard_layer/03_mapping_fields_table.csv`
- `out/dashboard_layer/03_smoke_local.txt`
- `out/dashboard_layer/03_scenario_assistant_contract_check.txt`

### Exit Criteria
- End-to-end dashboard integration uses the real Plan 3 and Plan 4 contracts.
- Scenario responses are consumable without custom post-hoc patching.
- A local smoke flow succeeds for at least one valid request.

## Phase 4 - Summary Tab
### Tasks
1. Implement the `Summary` tab for the main operational decision.
2. Display `rul_pred`, `risk_level`, `recommendation_text`, and `recommendation_priority` prominently.
3. Show a compact service-state banner that makes `ok`, `fallback`, and `degraded` easy to distinguish.
4. Surface minimal rationale without overwhelming the operator.

### Deliverables
- `out/dashboard_layer/04_summary_design_notes.txt`

### Exit Criteria
- The Summary tab communicates the core decision in one screen.
- Service-state communication is visible and unambiguous.
- The tab remains useful even when the response is not fully `ok`.

## Phase 5 - Analysis Tab
### Tasks
1. Implement the `Analysis` tab for deeper inspection.
2. Surface `risk_score`, `confidence_band`, `recommendation_alternatives`, and trace information.
3. Show comparison or history placeholders only if they are truly backed by current contracts.
4. Make uncertainty and fallback conditions clearly visible.

### Deliverables
- `out/dashboard_layer/05_analysis_design_notes.txt`

### Exit Criteria
- The Analysis tab adds diagnostic value beyond the Summary tab.
- Uncertainty and traceability are easy to inspect.
- No unsupported pseudo-analytics are introduced.

## Phase 6 - Scenarios Tab
### Tasks
1. Implement the `Scenarios` tab around the deterministic scenario assistant.
2. Show the scenario payload delta, assumptions, safety notes, and baseline-vs-scenario comparison.
3. If LLM enrichment is unavailable, present the deterministic interpretation cleanly rather than exposing missing-provider noise.
4. Distinguish clearly between factual output values and interpretation text.

### Deliverables
- `out/dashboard_layer/06_scenario_ux_rules.txt`
- `out/dashboard_layer/06_scenario_examples_rendering.txt`

### Exit Criteria
- Scenario comparison is readable and safe in `rules_only` mode.
- The UI remains coherent whether or not `llm_enabled` is active.
- Assumptions and safety notes are impossible to miss.

## Phase 7 - Technical Audit Tab
### Tasks
1. Implement the `Technical Audit` tab for traceability and debugging.
2. Display `audit_record_id`, `service_status`, `model_version`, `timestamp`, and `trace`.
3. Provide access to structured JSON or serialized payload views for technical users.
4. Make it easy to understand when a response came from fallback behavior.

### Deliverables
- `out/dashboard_layer/07_audit_ux_rules.txt`

### Exit Criteria
- Technical users can trace a dashboard result back to upstream layer outputs.
- Fallback and degraded runs are identifiable without reading logs directly.
- The audit tab supports debugging without cluttering the operator-facing tabs.

## Phase 8 - UX Copy, Explainability, and State Handling
### Tasks
1. Define the final copy rules for operator-facing language across all tabs.
2. Define how confidence, rationale, and recommendation urgency should be phrased.
3. Define empty, invalid, loading, degraded, and fallback state layouts.
4. Ensure the dashboard never hides important uncertainty or service-state information.

### Deliverables
- `out/dashboard_layer/08_ux_copy_guide.txt`
- `out/dashboard_layer/08_explainability_rules.txt`
- `out/dashboard_layer/08_state_handling_guide.txt`

### Exit Criteria
- Operator-facing language is consistent and explainable.
- Every mandatory app state has a final display strategy.
- Uncertainty and fallback behavior remain visible rather than softened away.

## Phase 9 - QA, Regression, and Local Readiness
### Tasks
1. Define the dashboard test matrix for valid, invalid, fallback, degraded, and scenario cases.
2. Record any rendering bugs or contract mismatches discovered during integration.
3. Validate local dependency setup and runtime configuration.
4. Validate local behavior when `GEMINI_API_KEY` is absent.

### Deliverables
- `out/dashboard_layer/09_test_matrix.txt`
- `out/dashboard_layer/09_bug_log.txt`
- `out/dashboard_layer/09_acceptance_checklist.txt`
- `out/dashboard_layer/09_local_smoke_report.txt`
- `out/dashboard_layer/09_runtime_config_notes.txt`
- `out/dashboard_layer/09_deploy_checklist.txt`

### Exit Criteria
- Local dashboard operation is documented and repeatable.
- The app has acceptance criteria tied to the real upstream contracts.
- The dashboard is ready for final implementation handoff or demo usage.

## Success Criteria
- The final dashboard uses real contracts from `predictive_layer` and `agent_layer`.
- The four target tabs are implemented around actual available data, not placeholders.
- Service states, uncertainty, and traceability remain visible and understandable throughout the UI.

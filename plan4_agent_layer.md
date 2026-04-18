# Plan 4 - Agent Layer Implementation
Plan ID: `plan4_agent_layer`  
Layer: `agent_layer` (Layer 2)  
Version: `v1.0`  
Status: `active`  
Depends on: `plan3_predictive_layer`  
Last updated: `2026-04-17`  
Detailed source: `prompt.md`

## Goal
Implement a contract-first `agent_layer` that converts predictive-layer RUL outputs into risk decisions, maintenance recommendations, and scenario-analysis responses, while preserving deterministic fallback behavior and auditability.

## Scope
- Inputs: `out/predictive_layer/*`, `out/research/*`, `out/eda/*`
- Code outputs: `src/agent_layer/*`
- Artifact outputs: `out/agent_layer/*`
- Main responsibilities: risk logic, recommendation engine, orchestration, scenario assistant, contract governance, and dashboard-facing decision payloads

## Preconditions
1. Activate environment: `conda activate cmapss`
2. Confirm Predictive Layer v1 artifacts exist, especially output schema, fallback policy, champion record, and smoke outputs.
3. Confirm service states are frozen as `ok`, `degraded`, `fallback`, `error_validacion`, `sin_datos`.
4. Ensure `src/agent_layer` and `out/agent_layer` exist or are created before implementation starts.

## Frozen Upstream Inputs
- Predictive-layer response includes: `rul_pred`, `confidence_band`, `target_policy`, `model_version`, `service_status`, `trace`, `timestamp`
- Current champion model: `rf`
- Predictive fallback model: `hgb`
- Predictive fallback behavior is already defined and must be preserved rather than replaced
- Target policy reaching upper layers remains `rul_capped` with cap `125`

## Core Contracts
### Contract A - Agent input from dashboard or caller
- `dataset_id`, `unit_id`, `cycle`
- `op_settings` with the required operating-condition fields
- `sensors` with the predictive-layer-required sensor fields
- optional `source`, `operator_note`, `request_context`

### Contract B - Predictive output consumed by agent_layer
- `rul_pred`, `confidence_band`, `model_version`, `service_status`, `trace`, `timestamp`

### Contract C - Agent decision output to dashboard_layer
- predictive fields passed through with traceability
- `risk_level`, `risk_score`
- `recommendation_text`, `recommendation_priority`, `recommendation_alternatives`
- `rationale`
- `audit_record_id`, `service_status`, `timestamp`

### Contract D - Scenario assistant output
- `proposed_payload`, `change_summary`, `assumptions`, `safety_notes`
- `comparison`, `comparison_interpretation`, `operator_guidance`
- `assistant_mode` (`rules_only|llm_enabled`)
- `llm_model_used` (optional), `service_status`

## Phase 1 - Contracts and Governance Freeze
### Tasks
1. Translate the upstream predictive-layer schema into an agent-layer input adapter contract.
2. Finalize the dashboard-facing output schema for decisions and recommendations.
3. Freeze policy rules for service-state propagation, audit fields, and recommendation safety boundaries.
4. Define a recommendation catalog that maps risk states to deterministic actions.

### Deliverables
- `out/agent_layer/01_input_contract_v1.json`
- `out/agent_layer/01_output_contract_v1.json`
- `out/agent_layer/01_contract_examples.json`
- `out/agent_layer/01_policy_rules.txt`
- `out/agent_layer/01_recommendation_catalog.csv`

### Exit Criteria
- Input and output schemas are explicit enough for implementation and dashboard integration.
- Service-state propagation rules are frozen and traceable to Predictive Layer v1.
- Deterministic recommendation rules exist before any LLM enrichment is added.

## Phase 2 - Risk Engine
### Tasks
1. Implement deterministic risk scoring driven primarily by `rul_pred`, confidence band width, and upstream service state.
2. Freeze threshold logic:
3. `critical` if `rul_pred <= 20`
4. `warning` if `20 < rul_pred <= 60`
5. `healthy` if `rul_pred > 60`
6. Define how degraded or fallback upstream states adjust confidence in the risk decision.
7. Emit human-readable rationale alongside numeric scores.

### Deliverables
- `src/agent_layer/risk_engine.py`
- `out/agent_layer/02_risk_scoring_design.txt`
- `out/agent_layer/02_thresholds_config.json`

### Exit Criteria
- Risk scoring is deterministic and reproducible.
- Thresholds and rationale rules are explicit and externally inspectable.
- The engine handles upstream `fallback` and `degraded` states without breaking the output contract.

## Phase 3 - Recommendation Engine
### Tasks
1. Implement deterministic recommendation selection from the risk score and risk level.
2. Define recommendation priority levels and alternative actions.
3. Add safety notes when upstream uncertainty or degraded service states are present.
4. Ensure recommendations remain explainable and do not depend on LLM availability.

### Deliverables
- `src/agent_layer/recommender.py`
- `out/agent_layer/03_recommendation_templates.txt`
- `out/agent_layer/03_priority_matrix.csv`

### Exit Criteria
- Every risk level maps to at least one stable primary recommendation.
- Recommendation outputs remain available in offline or provider-unavailable mode.
- The rationale for each recommendation path is documented and testable.

## Phase 4 - Orchestration and Audit Trail
### Tasks
1. Build the main pipeline: validate -> predictive call -> risk -> recommend -> audit -> response.
2. Keep the primary predictive provider as `src.predictive_layer.inference_service.predict_rul`.
3. Preserve upstream `service_status` while allowing the agent layer to add its own degraded notes.
4. Generate an append-only audit record for each decision.
5. Define helper utilities for tool calls, validation, and error wrapping.

### Deliverables
- `src/agent_layer/tools.py`
- `src/agent_layer/orchestrator.py`
- `out/agent_layer/04_toolchain_contracts.txt`
- `out/agent_layer/audit_log.jsonl`

### Exit Criteria
- One entrypoint can produce a full decision payload from a valid request.
- Audit records include enough information to reconstruct how a recommendation was produced.
- The orchestration path remains usable even if later scenario/LLM features are unavailable.

## Phase 5 - Scenario Assistant with Deterministic Fallback
### Tasks
1. Define the scenario assistant request and response contract.
2. Implement rules-only scenario generation that can perturb operating conditions or sensor assumptions safely.
3. Compare baseline versus scenario outputs using deterministic predictive and risk pipelines.
4. Produce clear change summaries, assumptions, and safety notes even without an LLM.

### Deliverables
- `src/agent_layer/scenario_rules.py`
- `src/agent_layer/scenario_interpreter.py`
- `out/agent_layer/05_scenario_assistant_flow.txt`
- `out/agent_layer/05_scenario_examples.json`

### Exit Criteria
- Scenario comparison works without any external model provider.
- Every scenario response includes explicit assumptions and safety notes.
- Scenario outputs reuse the same predictive and risk contracts as the baseline path.

## Phase 6 - Optional LLM Enrichment
### Tasks
1. Integrate `google-genai` for scenario interpretation and natural-language explanation enrichment.
2. Keep `GEMINI_API_KEY` as the primary secret and `GEMINI_MODEL` as an optional override.
3. Ensure LLM enrichment is additive and never required for core recommendations.
4. Guarantee automatic fallback to deterministic behavior when the provider is unavailable or the request is unsafe.

### Deliverables
- `src/agent_layer/llm_client.py`
- `out/agent_layer/06_llm_integration_policy.txt`
- `out/agent_layer/06_scenario_assistant_policy.txt`

### Exit Criteria
- The LLM path can be disabled without breaking any primary agent-layer feature.
- Deterministic outputs remain the source of truth for risk and recommendation logic.
- Provider failures are mapped cleanly into agent-layer service states.

## Phase 7 - Dashboard Mapping and Explainability
### Tasks
1. Map the agent-layer output to the target dashboard tabs: `Summary`, `Analysis`, `Scenarios`, `Technical Audit`.
2. Define what fields must appear in the dashboard for traceability and trust.
3. Document how `ok`, `degraded`, `fallback`, `error_validacion`, and `sin_datos` should appear to the user.
4. Freeze explainability rules for rationale, confidence communication, and scenario comparison text.

### Deliverables
- `out/agent_layer/07_dashboard_mapping.txt`
- `out/agent_layer/07_explainability_checklist.txt`
- `out/dashboard_layer/contract_integration_checklist.txt`

### Exit Criteria
- Dashboard integration fields are explicit and tab-aware.
- Explainability requirements are documented before UI implementation begins.
- Service-state behavior is defined consistently across prediction, agent, and scenario outputs.

## Phase 8 - Validation and Hardening
### Tasks
1. Define the agent-layer test matrix for valid, degraded, fallback, and invalid-input cases.
2. Record expected failure modes for predictive-provider errors, scenario misuse, and missing secrets.
3. Define acceptance criteria for risk stability, recommendation availability, audit completeness, and scenario safety.
4. Run a local end-to-end smoke path using the predictive-layer champion service.

### Deliverables
- `out/agent_layer/08_test_matrix.txt`
- `out/agent_layer/08_failure_modes.txt`
- `out/agent_layer/08_acceptance_criteria.txt`
- `out/agent_layer/08_smoke_local.txt`

### Exit Criteria
- Agent-layer behavior is documented for both normal and degraded conditions.
- Acceptance criteria are concrete enough to decide readiness for Plan 5 integration.
- The local smoke path proves contract compatibility with the predictive layer.

## Success Criteria
- The agent layer delivers stable, traceable risk and recommendation outputs from predictive-layer inputs.
- Scenario assistance works in deterministic mode and optionally in LLM-enriched mode without breaking core behavior.
- Layer 2 remains decoupled from UI internals and ready for dashboard integration under explicit contracts.

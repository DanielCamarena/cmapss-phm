# Plan 4 - Agent Layer (Risk, Recommendations, Scenario Assistant)
Plan ID: `plan4_agent_layer`  
Layer: `agent_layer` (Layer 2 / capa2)  
Version: `v1.0`  
Status: `active`  
Depends on: `plan3_predictive_layer`  
Last updated: `2026-04-17`

## Goal
Implement a contract-first decision layer that converts RUL predictions into risk and recommendations, and supports LLM-assisted what-if scenarios with deterministic fallback.

## Architecture Alignment
- Layer 1: `predictive_layer`
- Layer 2: `agent_layer`
- Layer 3: `dashboard_layer`

## Core Contracts
### Contract A: Dashboard input to Agent Layer
- `dataset_id`, `unit_id`, `cycle`, `op_settings[3]`, `sensors[21]`, `source`

### Contract B: Predictive output to Agent Layer
- `rul_pred`, `confidence_band`, `model_version`, `timestamp`, `service_status`

### Contract C: Agent decision output to Dashboard
- `rul_pred`, `confidence_band`
- `risk_level`, `risk_score`
- `recommendation_text`, `recommendation_priority`, `recommendation_alternatives`
- `rationale`, `audit_record_id`, `service_status`, `timestamp`

### Contract D: Scenario assistant output
- `proposed_payload`, `change_summary`, `assumptions`, `safety_notes`
- `comparison_interpretation`, `operator_guidance`
- `assistant_mode` (`rules_only|llm_enabled`)
- `llm_model_used` (optional), `service_status`

## Phase 1 - Contracts and Governance
### Deliverables
- `out/agent_layer/01_input_contract_v1.json`
- `out/agent_layer/01_output_contract_v1.json`
- `out/agent_layer/01_contract_examples.json`
- `out/agent_layer/01_policy_rules.txt`
- `out/agent_layer/01_recommendation_catalog.csv`

## Phase 2 - Risk Engine
### Tasks
1. Implement composite risk score and rationale.
2. Enforce hard-stop thresholds:
3. `critical` if `rul_pred <= 20`
4. `warning` if `20 < rul_pred <= 60`
5. `healthy` if `rul_pred > 60`

### Deliverables
- `src/agent_layer/risk_engine.py`
- `out/agent_layer/02_risk_scoring_design.txt`
- `out/agent_layer/02_thresholds_config.json`

## Phase 3 - Orchestration and Tool Use
### Tasks
1. Build pipeline: validate -> predictive read -> score -> recommend -> audit.
2. Keep primary provider as `predictive_layer.inference_service.predict_rul`.
3. Keep degraded behavior without breaking dashboard.

### Deliverables
- `src/agent_layer/tools.py`
- `src/agent_layer/orchestrator.py`
- `out/agent_layer/03_toolchain_contracts.txt`
- `out/agent_layer/audit_log.jsonl`

## Phase 4 - Recommendation Logic
### Deliverables
- `src/agent_layer/recommender.py`
- `out/agent_layer/04_recommendation_templates.txt`
- `out/agent_layer/04_priority_matrix.csv`

## Phase 5 - Dashboard Integration Mapping
### Tasks
1. Map output to final tabs:
2. `Summary`, `Analysis`, `Scenarios`, `Technical Audit`
3. Validate states: `ok`, `degraded`, `fallback`, `error_validacion`, `sin_datos`.

### Deliverables
- `out/agent_layer/05_dashboard_mapping.txt`
- `out/agent_layer/05_explainability_checklist.txt`
- `out/dashboard_layer/contract_integration_checklist.txt`
- `out/agent_layer/05_scenario_assistant_flow.txt`

## Phase 6 - LLM Integration (Official SDK)
### Tasks
1. Use `google-genai` SDK for scenario and interpretation enrichment.
2. Keep `GEMINI_API_KEY` as main secret, `GEMINI_MODEL` optional override.
3. Preserve deterministic fallback when provider is unavailable.

### Deliverables
- `src/agent_layer/llm_client.py`
- `src/agent_layer/scenario_interpreter.py`
- `out/agent_layer/06_llm_integration_policy.txt`
- `out/agent_layer/06_scenario_assistant_policy.txt`

## Phase 7 - Validation and Hardening
### Deliverables
- `out/agent_layer/07_test_matrix.txt`
- `out/agent_layer/07_failure_modes.txt`
- `out/agent_layer/07_acceptance_criteria.txt`

## Success Criteria
- Stable risk/recommendation decisions with traceability.
- Scenario assistant works in both LLM and fallback modes.
- Layer 2 remains decoupled from UI internals and is contract-compatible.

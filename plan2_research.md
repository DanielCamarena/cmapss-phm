# Plan 2 - Research and Predictive Method Framing
Plan ID: `plan2_research`  
Layer: `predictive_layer` (Layer 1)  
Version: `v1.0`  
Status: `active`  
Depends on: `plan1_eda`  
Last updated: `2026-04-17`  
Detailed source: `prompt.md`

## Goal
Transform the available CMAPSS references, benchmark documentation, and Plan 1 EDA outputs into an implementation-ready predictive RUL methodology for the application.

## Scope
- Sources: `doc/NASA_CMAPSS.pdf`, `doc/Damage Propagation Modeling.pdf`, `doc/Ramasso2014.pdf`, `data/readme.txt`
- EDA inputs: `out/eda/*`, `out/processed/*`, `fig/eda/*`
- Outputs: `out/research/*`
- Main outcome: a justified modeling strategy, explicit inference contract, and evaluation protocol for Plan 3

## Preconditions
1. Activate environment: `conda activate cmapss`
2. Ensure output folder exists: `out/research`
3. Confirm Plan 1 artifacts are available, especially target, preprocessing, and risk notes.
4. Keep research conclusions traceable to either a source document or an EDA artifact.

## Phase 1 - Structured Source Review
### Tasks
1. Review NASA CMAPSS benchmark documentation and extract simulator assumptions, fault setup, operating-condition structure, and variable interpretation.
2. Review the damage propagation reference and extract degradation assumptions, simulation limitations, and implications for predictive modeling.
3. Review the Ramasso survey/reference and extract RUL methodology patterns, evaluation practices, and common benchmark pitfalls.
4. Cross-check the literature against `data/readme.txt` and Plan 1 findings.
5. Write source notes in a comparable template so later decisions can cite evidence consistently.

### Deliverables
- `out/research/01_ficha_nasa_cmapss.txt`
- `out/research/01_ficha_damage_propagation.txt`
- `out/research/01_ficha_ramasso2014.txt`
- `out/research/01_cross_source_notes.txt`

### Exit Criteria
- Each source has a structured note with assumptions, limits, and modeling implications.
- Key differences between benchmark setup and real-world deployment expectations are documented.
- At least one research note explicitly connects literature claims to Plan 1 EDA observations.

## Phase 2 - Problem Framing and Method Synthesis
### Tasks
1. Define the predictive task precisely: unit-level RUL estimation from multivariate time series under varying operating conditions.
2. Compare candidate model families: tabular baselines, sequence models, and optional hybrid approaches.
3. Define minimum required inputs and optional enriched inputs for the predictive layer.
4. Reconcile target alternatives from Plan 1, including `rul_linear` and `rul_capped`.
5. Record trade-offs in interpretability, training cost, inference latency, and expected robustness.

### Deliverables
- `out/research/02_problem_definition.txt`
- `out/research/02_model_matrix.csv`
- `out/research/02_metodologia_propuesta.txt`
- `out/research/02_target_policy_decision.txt`

### Exit Criteria
- At least one primary and one secondary model family are selected for Plan 3.
- Target policy is justified with both literature and Plan 1 evidence.
- The proposed approach is specific enough to guide implementation without reopening the modeling scope.

## Phase 3 - Predictive Layer Contract Design
### Tasks
1. Specify the inference input contract, including required fields, accepted schema, and validation expectations.
2. Specify the inference output contract, including RUL prediction, confidence representation, metadata, and service status.
3. Define the internal pipeline stages: validate, preprocess, infer, calibrate or postprocess, and trace.
4. Define out-of-distribution handling, missing-input behavior, and degraded-service behavior.
5. Define model versioning and traceability fields that upper layers will need later.

### Deliverables
- `out/research/03_api_contract_rul_layer.txt`
- `out/research/03_inference_pipeline.txt`
- `out/research/03_output_payload_example.json`
- `out/research/03_error_policy.txt`

### Exit Criteria
- Input and output contracts are explicit enough for an implementation handoff.
- Error and degraded-mode behavior are defined for predictable downstream integration.
- Traceability fields are sufficient for dashboard audit and agent-layer use.

## Phase 4 - Evaluation Protocol and Acceptance Rules
### Tasks
1. Define the primary and secondary metrics for model comparison, including `RMSE`, `MAE`, subset stability, and optional PHM-specific score.
2. Define leakage-safe validation rules consistent with Plan 1 preprocessing and split strategy.
3. Define comparison slices by dataset, operating-condition complexity, and RUL band.
4. Define robustness tests for noise, partial missing inputs, and condition drift.
5. Define quantitative acceptance thresholds for promoting a model to champion status.

### Deliverables
- `out/research/04_eval_protocol.txt`
- `out/research/04_metric_definitions.txt`
- `out/research/04_robustness_test_plan.txt`
- `out/research/04_acceptance_criteria.txt`

### Exit Criteria
- The evaluation protocol supports fair comparison across all candidate models.
- Validation rules are demonstrably leakage-safe and aligned with Plan 1 outputs.
- Acceptance criteria are strict enough to support a real champion-selection decision in Plan 3.

## Phase 5 - Implementation Backlog for Plan 3
### Tasks
1. Translate the methodology into an ordered implementation backlog for `predictive_layer`.
2. Separate must-have deliverables from optional enhancements.
3. Identify training artifacts, metadata outputs, and contract files Plan 3 must produce.
4. Define the minimum smoke-test path needed before agent-layer integration.
5. Define release increments such as MVP, V1, and hardening follow-up work.

### Deliverables
- `out/research/05_integration_backlog.txt`
- `out/research/05_release_plan.txt`
- `out/research/05_plan3_handoff_checklist.txt`

### Exit Criteria
- Plan 3 implementation can start from an ordered backlog rather than open-ended research notes.
- MVP versus optional work is clearly separated.
- Integration dependencies with the agent and dashboard layers are visible early.

## Phase 6 - Research Closure and Risk Register
### Tasks
1. Consolidate the main technical decisions and unresolved questions.
2. Record key risks, assumptions, and recommended mitigations.
3. Summarize why the chosen methodology is appropriate for this project and benchmark.
4. Produce a short master handoff note that connects Plan 1 findings to Plan 3 work.

### Deliverables
- `out/research/06_master_plan_rul_layer.txt`
- `out/research/06_risks_mitigations.txt`
- `out/research/06_open_questions.txt`

### Exit Criteria
- The research phase ends with a concrete modeling direction, not just collected notes.
- Risks and unresolved items are bounded well enough to avoid blocking Plan 3.
- The final handoff is understandable without rereading every source document.

## Success Criteria
- The predictive methodology is literature-backed, benchmark-aware, and implementation-ready.
- Input/output contracts, evaluation rules, and model-selection logic are explicit.
- Plan 3 can proceed with minimal ambiguity about targets, candidate models, and validation strategy.

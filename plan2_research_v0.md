# Plan 2 - Research and Method Framing
Plan ID: `plan2_research`  
Layer: `predictive_layer` (Layer 1 / capa1)  
Version: `v1.0`  
Status: `active`  
Depends on: `plan1_eda`  
Last updated: `2026-04-17`

## Goal
Transform C-MAPSS documentation and literature into an implementable and testable RUL methodology for the app.

## Inputs
- `doc/NASA_CMAPSS.pdf`
- `doc/Damage Propagation Modeling.pdf`
- `doc/Ramasso2014.pdf`
- `data/readme.txt`
- `out/eda/*`

## Outputs
- Candidate-model strategy and rationale.
- Predictive-layer functional specification.
- Evaluation protocol and staged integration roadmap.

## Preconditions
1. Activate environment: `conda activate cmapss`
2. Ensure folder exists: `out/research`

## Phase 1 - Structured Technical Reading
### Tasks
1. Extract simulator assumptions and variable interpretation.
2. Extract degradation modeling assumptions and limits.
3. Extract PHM/RUL methodology from references.
4. Build comparable notes per source.

### Deliverables
- `out/research/01_ficha_nasa_cmapss.txt`
- `out/research/01_ficha_damage_propagation.txt`
- `out/research/01_ficha_ramasso2014.txt`

## Phase 2 - Method Synthesis
### Tasks
1. Build candidate model matrix (tabular, sequence, hybrid optional).
2. Define minimum and optional inputs.
3. Define target policy (`rul_linear`, `rul_capped`).
4. Define model-selection trade-offs.

### Deliverables
- `out/research/02_model_matrix.csv`
- `out/research/02_metodologia_propuesta.txt`

## Phase 3 - Predictive Layer Design
### Tasks
1. Specify input/output contract for inference.
2. Specify internal pipeline (validate, preprocess, infer, postprocess).
3. Define error handling and out-of-distribution policy.
4. Define model versioning and prediction traceability.

### Deliverables
- `out/research/03_api_contract_rul_layer.txt`
- `out/research/03_inference_pipeline.txt`
- `out/research/03_error_policy.txt`

## Phase 4 - Evaluation Protocol
### Tasks
1. Define metrics (RMSE, MAE, subset stability, optional PHM score).
2. Define leakage-safe validation.
3. Define robustness tests (noise, OOD, operating conditions).
4. Define acceptance thresholds.

### Deliverables
- `out/research/04_eval_protocol.txt`
- `out/research/04_acceptance_criteria.txt`

## Phase 5 - Staged Integration Plan
### Tasks
1. MVP: single-case inference + dashboard display.
2. V1: batch scoring and basic monitoring.
3. V2: recalibration loops and proactive recommendations.

### Deliverables
- `out/research/05_integration_backlog.txt`
- `out/research/05_release_plan.txt`

## Phase 6 - Research Closure
### Tasks
1. Consolidate technical decisions.
2. Order implementation tasks by priority and effort.
3. Document risks and mitigations.

### Deliverables
- `out/research/06_master_plan_rul_layer.txt`
- `out/research/06_risks_mitigations.txt`

## Success Criteria
- Methodology is literature-backed and implementation-ready.
- Predictive-layer contract and evaluation protocol are explicit.
- Clear handoff to Plan 3 development.

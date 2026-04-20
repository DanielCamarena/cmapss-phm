# Plan 3 - Predictive Layer Implementation
Plan ID: `plan3_predictive_layer`  
Layer: `predictive_layer` (Layer 1)  
Version: `v1.0`  
Status: `active`  
Depends on: `plan1_eda`, `plan2_research`  
Last updated: `2026-04-17`  
Detailed source: `prompt.md`

## Goal
Implement a production-internal predictive layer that trains multiple RUL models, selects a champion with explicit evidence, exposes a stable inference contract, and is ready for integration with upper layers.

## Scope
- Inputs: `out/eda/*`, `out/processed/*.parquet`, `fig/eda/*`, `out/research/*`
- Code outputs: `src/predictive_layer/*`
- Artifact outputs: `out/predictive_layer/*`
- Main responsibilities: multi-model training, evaluation, calibration, champion selection, inference service, and integration smoke readiness

## Preconditions
1. Activate environment: `conda activate cmapss`
2. Confirm Plan 1 processed artifacts exist: `out/processed/train_processed.parquet`, `valid_processed.parquet`, `test_processed.parquet`
3. Confirm Plan 2 methodology artifacts exist, especially target policy, acceptance criteria, and handoff checklist.
4. Ensure `src/predictive_layer` and `out/predictive_layer` exist or are created before implementation begins.

## Frozen Inputs from Plan 2
- Primary target: `rul_capped` with cap `125`
- Secondary audit target: `rul_linear`
- Baseline feature set: Plan 1 selected features
- Baseline models: `HistGradientBoostingRegressor`, `RandomForestRegressor`
- Sequence challengers: `LSTM`, `GRU` or `TCN`
- Validation rule: grouped by `unit_id`, preserving cycle order
- Mandatory reporting: global metrics, per-subset metrics, traceable output payload, and service status

## Phase 1 - Implementation Freeze and Project Skeleton
### Tasks
1. Freeze the modeling contract from Plans 1 and 2 into a machine-readable implementation note.
2. Create the `predictive_layer` folder structure for training, evaluation, calibration, and inference code.
3. Define shared utilities for loading processed artifacts, tracking model metadata, and writing results.
4. Define one configuration entrypoint for feature policy, target policy, and model settings.

### Deliverables
- `src/predictive_layer/__init__.py`
- `src/predictive_layer/config.py`
- `src/predictive_layer/data_loader.py`
- `src/predictive_layer/io_utils.py`
- `out/predictive_layer/01_modeling_decisions_frozen.txt`
- `out/predictive_layer/01_model_comparison_protocol.txt`

### Exit Criteria
- The predictive layer has a stable code skeleton with reusable utilities.
- Frozen decisions match Plan 2 without re-opening target or split policy debates.
- All later scripts can import one shared configuration surface.

## Phase 2 - Tabular Baselines
### Tasks
1. Implement row-level training flow for `HistGradientBoostingRegressor`.
2. Implement row-level training flow for `RandomForestRegressor`.
3. Save fitted model artifacts, training metadata, and validation predictions.
4. Record feature usage, target policy, runtime, and metric outputs for each baseline.

### Deliverables
- `src/predictive_layer/train_hgb.py`
- `src/predictive_layer/train_rf.py`
- `out/predictive_layer/models/hgb_model.joblib`
- `out/predictive_layer/models/rf_model.joblib`
- `out/predictive_layer/02_train_metadata_hgb.json`
- `out/predictive_layer/02_train_metadata_rf.json`
- `out/predictive_layer/02_valid_predictions_hgb.parquet`
- `out/predictive_layer/02_valid_predictions_rf.parquet`

### Exit Criteria
- Both tabular baselines train successfully on the Plan 1 artifacts.
- Validation predictions are written in a comparable format.
- At least one baseline satisfies the minimum Plan 2 baseline-acceptance rule.

## Phase 3 - Sequence Challengers
### Tasks
1. Implement sequence-window generation using the documented 30-step and 50-step policies.
2. Implement `LSTM` training on windowed trajectories.
3. Implement one secondary sequence architecture: `GRU` or `TCN`.
4. Save model artifacts, training metadata, and validation predictions in the same evaluation format used by the baselines.
5. Record any environment dependency added for sequence training.

### Deliverables
- `src/predictive_layer/windowing.py`
- `src/predictive_layer/train_lstm.py`
- `src/predictive_layer/train_gru_or_tcn.py`
- `out/predictive_layer/models/lstm_model.*`
- `out/predictive_layer/models/gru_or_tcn_model.*`
- `out/predictive_layer/03_train_metadata_lstm.json`
- `out/predictive_layer/03_train_metadata_gru_or_tcn.json`
- `out/predictive_layer/03_valid_predictions_lstm.parquet`
- `out/predictive_layer/03_valid_predictions_gru_or_tcn.parquet`

### Exit Criteria
- Window generation is deterministic and traceable.
- At least one sequence challenger trains successfully and produces comparable validation outputs.
- Sequence experiments are reproducible from documented configuration files.

## Phase 4 - Comparative Evaluation and Champion Selection
### Tasks
1. Evaluate all trained models with `RMSE`, `MAE`, and per-subset metrics.
2. Report error by RUL band and compare simple versus complex subsets.
3. Measure single-request inference latency for each candidate.
4. Apply Plan 2 champion-promotion rules, including the 5% global-improvement or stability-based waiver logic.
5. Record the champion, accepted challengers, and rejected candidates with reasons.

### Deliverables
- `src/predictive_layer/evaluate_models.py`
- `out/predictive_layer/04_metrics_global_by_model.csv`
- `out/predictive_layer/04_metrics_by_dataset_by_model.csv`
- `out/predictive_layer/04_error_by_rul_band_by_model.csv`
- `out/predictive_layer/04_latency_by_model.csv`
- `out/predictive_layer/04_champion_decision_record.md`

### Exit Criteria
- Every trained candidate is evaluated under one consistent protocol.
- A champion is selected or the blocking reason is documented explicitly.
- The decision record explains quality, latency, and subset-stability trade-offs.

## Phase 5 - Calibration, Robustness, and Fallback Policy
### Tasks
1. Build a confidence-band policy for the champion model.
2. Run robustness checks for noise, partial missing input, and subset complexity.
3. Test whether the champion degrades safely on difficult subsets and OOD-like conditions.
4. Define deterministic fallback behavior to the best stable baseline.

### Deliverables
- `src/predictive_layer/calibration.py`
- `src/predictive_layer/robustness.py`
- `out/predictive_layer/05_calibration_report.md`
- `out/predictive_layer/05_confidence_band_policy.json`
- `out/predictive_layer/05_robustness_results.csv`
- `out/predictive_layer/05_fallback_policy.txt`

### Exit Criteria
- Confidence bands are defined and testable.
- Robustness results are available for at least the scenarios mandated in Plan 2.
- Fallback behavior is explicit enough for use by upper layers.

## Phase 6 - Inference Contract v1
### Tasks
1. Convert the Plan 2 contract draft into finalized machine-readable schemas.
2. Define the request schema expected by `predictive_layer`.
3. Define the response schema with `rul_pred`, `confidence_band`, `model_version`, `service_status`, and trace metadata.
4. Define structured error payloads and example request/response pairs.

### Deliverables
- `out/predictive_layer/06_input_schema_v1.json`
- `out/predictive_layer/06_output_schema_v1.json`
- `out/predictive_layer/06_error_contract_v1.json`
- `out/predictive_layer/06_contract_examples.json`

### Exit Criteria
- Schemas are explicit enough for agent-layer and dashboard integration.
- Output contract includes service states and traceability metadata.
- Error payloads cover validation failure, degraded mode, fallback mode, and no-data cases.

## Phase 7 - Champion Inference Service and Integration Readiness
### Tasks
1. Implement the champion inference entrypoint using the finalized contract.
2. Implement preprocessing reuse so live inference matches training assumptions.
3. Integrate confidence-band and fallback logic into the service response.
4. Run local smoke tests from processed input to structured prediction output.
5. Validate that the service can be consumed by later layers without UI-specific coupling.

### Deliverables
- `src/predictive_layer/inference_service.py`
- `src/predictive_layer/predict.py`
- `out/predictive_layer/07_smoke_test_e2e.txt`
- `out/predictive_layer/07_latency_e2e.csv`
- `out/predictive_layer/07_dashboard_integration_report.md`

### Exit Criteria
- One local entrypoint produces a valid structured prediction response.
- Smoke tests pass from input payload to final response shape.
- The predictive layer is integration-ready and decoupled from dashboard internals.

## Phase 8 - Release Package and Residual Risks
### Tasks
1. Publish release notes for the predictive layer.
2. Publish residual risks, unresolved technical debt, and future improvements.
3. Publish the next-step backlog for Plans 4 and 5 dependencies.
4. Publish a deployment or local-operation checklist for reproducible use.

### Deliverables
- `out/predictive_layer/08_release_notes.md`
- `out/predictive_layer/08_residual_risks.md`
- `out/predictive_layer/08_next_steps_backlog.md`
- `out/predictive_layer/08_deploy_checklist.txt`

### Exit Criteria
- The predictive layer can be handed off with clear operational expectations.
- Residual technical risks are documented rather than hidden.
- Upper-layer integration work can start from a stable predictive contract.

## Success Criteria
- A champion model is selected with quantitative evidence and explicit trade-off documentation.
- The predictive layer exposes a stable, traceable inference contract with fallback behavior.
- The implementation is ready for agent-layer and dashboard integration under local demo conditions.

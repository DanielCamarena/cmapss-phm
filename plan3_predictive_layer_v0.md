# Plan 3 - Predictive Layer Consolidation
Plan ID: `plan3_predictive_layer`  
Layer: `predictive_layer` (Layer 1 / capa1)  
Version: `v1.0`  
Status: `active`  
Depends on: `plan1_eda`, `plan2_research`  
Last updated: `2026-04-17`

## Goal
Deliver a production-internal predictive layer with multi-model training, champion selection, stable inference contract, and integration readiness.

## Required Inputs
- `out/eda/*`, `fig/eda/*`
- `out/processed/train_processed.parquet`
- `out/processed/valid_processed.parquet`
- `out/processed/test_processed.parquet`
- `out/research/*`

## Phase 1 - Freeze Modeling Decisions
### Tasks
1. Confirm targets (`rul_capped` primary, `rul_linear` secondary).
2. Confirm feature policy and temporal windows.
3. Confirm anti-leakage split strategy.
4. Define model-comparison protocol.

### Deliverables
- `out/predictive_layer/01_modeling_decisions_frozen.txt`
- `out/predictive_layer/01_model_comparison_protocol.txt`

## Phase 2 - Train Candidate Models
### Tasks
1. Train tabular baselines (`RF`, `GB`).
2. Train sequence models (`LSTM`, `GRU` or `TCN`).
3. Version artifacts and training metadata.
4. Save validation predictions per model.

### Deliverables
- `src/predictive_layer/train_rf.py`
- `src/predictive_layer/train_gb.py`
- `src/predictive_layer/train_lstm.py`
- `src/predictive_layer/train_tcn_or_gru.py`
- `out/predictive_layer/models/*`
- `out/predictive_layer/02_train_metadata_<model>.json`
- `out/predictive_layer/02_valid_predictions_<model>.parquet`

## Phase 3 - Comparative Evaluation and Champion
### Tasks
1. Evaluate global and per-subset metrics.
2. Evaluate error by RUL bands.
3. Measure inference latency.
4. Select champion and challengers.
5. Record decision and trade-offs.

### Deliverables
- `out/predictive_layer/03_metrics_global_by_model.csv`
- `out/predictive_layer/03_metrics_by_dataset_by_model.csv`
- `out/predictive_layer/03_error_by_rul_band_by_model.csv`
- `out/predictive_layer/03_latency_by_model.csv`
- `out/predictive_layer/03_champion_decision_record.md`

## Phase 4 - Calibration and Robustness
### Tasks
1. Build confidence-band policy.
2. Evaluate robustness to noise and partial missing inputs.
3. Evaluate subset/condition drift behavior.
4. Define fallback behavior.

### Deliverables
- `out/predictive_layer/04_calibration_report.md`
- `out/predictive_layer/04_confidence_band_policy.json`
- `out/predictive_layer/04_robustness_results.csv`
- `out/predictive_layer/04_fallback_policy.txt`

## Phase 5 - Inference Contract v1
### Tasks
1. Finalize input schema.
2. Finalize output schema.
3. Finalize error contract and examples.

### Deliverables
- `out/predictive_layer/05_input_schema_v1.json`
- `out/predictive_layer/05_output_schema_v1.json`
- `out/predictive_layer/05_error_contract_v1.json`
- `out/predictive_layer/05_contract_examples.json`

## Phase 6 - Inference Service and Integration
### Tasks
1. Implement champion inference service.
2. Validate consumption by `agent_layer`.
3. Run local end-to-end smoke test.

### Deliverables
- `src/predictive_layer/inference_service.py`
- `out/predictive_layer/06_smoke_test_e2e.txt`
- `out/predictive_layer/06_latency_e2e.csv`
- `out/predictive_layer/06_dashboard_integration_report.md`

## Phase 7 - Release Package
### Tasks
1. Publish release notes.
2. Publish residual risks and mitigations.
3. Publish backlog and deployment checklist.

### Deliverables
- `out/predictive_layer/07_release_notes.md`
- `out/predictive_layer/07_residual_risks.md`
- `out/predictive_layer/07_next_steps_backlog.md`
- `out/predictive_layer/07_deploy_checklist.txt`

## Success Criteria
- Champion selected with quantitative evidence.
- Stable inference contract consumed by upper layers.
- Predictive layer ready for integration and demo operations.

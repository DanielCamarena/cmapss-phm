# Methodology

## 1. Dataset and problem definition

The project uses the NASA C-MAPSS turbofan benchmark, a standard predictive-maintenance dataset composed of multivariate run-to-failure trajectories. Each row corresponds to one cycle of engine operation and contains operational settings and sensor measurements. The predictive task is Remaining Useful Life (RUL) estimation.

The implemented system targets four benchmark subsets:
- `FD001`
- `FD002`
- `FD003`
- `FD004`

These subsets differ in operating-condition complexity and fault-mode structure, which makes them useful both for model comparison and system robustness analysis.

## 2. Preprocessing and feature selection

Preprocessing is implemented in [src/eda/run_plan1_eda.py](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/eda/run_plan1_eda.py:1>) and frozen in [out/eda/05_preprocessing_config.json](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/eda/05_preprocessing_config.json:1>).

Key decisions:
- low-variance features are removed before model training
- `StandardScaler` is fitted on the training split only
- processed train/validation/test splits are exported to parquet
- the target is preserved as raw `rul` and operationalized as capped `rul_capped`

Selected predictive features:
- `op_setting_1`
- `op_setting_2`
- `sensor_2`
- `sensor_3`
- `sensor_4`
- `sensor_7`
- `sensor_8`
- `sensor_9`
- `sensor_11`
- `sensor_12`
- `sensor_13`
- `sensor_14`
- `sensor_15`
- `sensor_17`
- `sensor_20`
- `sensor_21`

Removed low-variance features include:
- `op_setting_3`
- `sensor_1`
- `sensor_5`
- `sensor_6`
- `sensor_10`
- `sensor_16`
- `sensor_18`
- `sensor_19`

## 3. Target definition

The baseline target policy is capped RUL, documented in [out/eda/04_target_definition.txt](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/eda/04_target_definition.txt:1>).

Implemented policy:
- target column: `rul`
- operational learning target: `rul_capped`
- cap value: `125`

This design preserves raw RUL for audit and analysis while using capped RUL to stabilize training and downstream decision behavior.

## 4. Candidate predictive models

The predictive layer implements four candidate models:
- `rf`: RandomForestRegressor
- `hgb`: HistGradientBoostingRegressor
- `lstm`
- `gru`

The candidate set intentionally mixes:
- strong tabular baselines
- sequence challengers suited to temporal degradation modeling

The rationale is documented in [out/research/02_model_matrix.csv](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/research/02_model_matrix.csv:1>) and implemented in:
- [src/predictive_layer/train_rf.py](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/predictive_layer/train_rf.py:1>)
- [src/predictive_layer/train_hgb.py](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/predictive_layer/train_hgb.py:1>)
- [src/predictive_layer/train_lstm.py](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/predictive_layer/train_lstm.py:1>)
- [src/predictive_layer/train_gru_or_tcn.py](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/predictive_layer/train_gru_or_tcn.py:1>)

## 5. Champion selection and calibration

Model evaluation is produced in [src/predictive_layer/evaluate_models.py](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/predictive_layer/evaluate_models.py:1>) and frozen in:
- [out/predictive_layer/04_metrics_global_by_model.csv](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/predictive_layer/04_metrics_global_by_model.csv:1>)
- [out/predictive_layer/04_metrics_by_dataset_by_model.csv](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/predictive_layer/04_metrics_by_dataset_by_model.csv:1>)
- [out/predictive_layer/04_latency_by_model.csv](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/predictive_layer/04_latency_by_model.csv:1>)
- [out/predictive_layer/champion_record.json](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/predictive_layer/champion_record.json:1>)

Current outcome:
- `gru` achieves the best raw RMSE
- `rf` is selected as champion
- `hgb` is retained as deterministic fallback

The promotion rule favors stable, integration-ready performance rather than raw RMSE alone. This is critical because the final application is not only a benchmark model comparison, but a deployable PHM decision system.

Uncertainty is added through an empirical absolute-error calibration policy implemented in [src/predictive_layer/calibration.py](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/predictive_layer/calibration.py:1>) and surfaced at runtime through [src/predictive_layer/inference_service.py](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/predictive_layer/inference_service.py:1>).

## 6. Deterministic risk and recommendation logic

The agent layer transforms predictive outputs into operator-facing risk and action signals.

Key components:
- [src/agent_layer/risk_engine.py](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/agent_layer/risk_engine.py:1>)
- [src/agent_layer/recommender.py](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/agent_layer/recommender.py:1>)

Risk is computed deterministically from:
- predicted RUL
- confidence-band width
- predictive service status

Outputs include:
- `risk_level`
- `risk_score`
- `recommendation_text`
- recommendation urgency / alternatives

This design makes the decision layer auditable and stable across runs.

## 7. Scenario methodology

Scenario execution is implemented as a deterministic comparison pipeline in:
- [src/agent_layer/orchestrator.py](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/agent_layer/orchestrator.py:1>)
- [src/agent_layer/scenario_rules.py](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/agent_layer/scenario_rules.py:1>)
- [src/agent_layer/scenario_interpreter.py](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/agent_layer/scenario_interpreter.py:1>)

The implemented stages are:
1. parse intent
2. validate scenario changes
3. build scenario payload
4. run baseline prediction
5. run scenario prediction
6. compare baseline vs scenario
7. generate interpretation

The LLM is non-central:
- it may help parse natural-language scenario intent
- it may improve wording of the scenario explanation
- it never controls prediction, risk computation, validation, or comparison values

## 8. Dashboard-driven scientific artifact

The dashboard is not only a demo layer. It operationalizes the manuscript’s scientific narrative by exposing:
- decision outputs (`Summary`)
- interpretability and uncertainty (`Analysis`)
- controlled what-if comparison (`Scenarios`)
- traceability and contracts (`Technical Audit`)

This makes the application suitable as both:
- an engineering artifact
- a research demonstration of trustworthy PHM system integration

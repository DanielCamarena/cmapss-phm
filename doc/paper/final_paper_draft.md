# Traceable Predictive Maintenance for NASA C-MAPSS: An End-to-End PHM System with Calibrated RUL Prediction, Deterministic Risk Logic, and Interactive Scenario Analysis

## Abstract

This paper presents an end-to-end predictive maintenance application built on the NASA C-MAPSS benchmark. The system combines a multi-model predictive layer for Remaining Useful Life (RUL) estimation, a deterministic agent layer for risk scoring and maintenance recommendations, and a dashboard layer for decision presentation, scenario analysis, and technical auditability. Candidate models include Random Forest, HistGradientBoosting, LSTM, and GRU. Although GRU achieved the best raw RMSE, the deployed champion is Random Forest because it offered the best balance of stability, deployment readiness, and deterministic fallback support. The application augments point predictions with calibrated confidence bands, converts them into traceable risk and recommendation outputs, and exposes the full workflow through an interactive dashboard with `Summary`, `Analysis`, `Scenarios`, and `Technical Audit` views. The paper reports predictive performance, uncertainty behavior, scenario-comparison evidence, failure cases, and engineering constraints related to latency, safety, reliability, and reproducibility. The result is both a scientific study on C-MAPSS PHM and an implemented AI system that supports auditable human interaction.

## 1. Introduction

Remaining Useful Life estimation is a central task in prognostics and health management because it translates sensor and operational telemetry into actionable maintenance decisions. However, benchmark-oriented research often stops at model evaluation and does not fully address how a predictive component becomes part of a usable PHM application. Real maintenance systems require more than a point estimate: they need uncertainty handling, decision logic, scenario analysis, explainability, and traceability.

This project addresses that gap by implementing a three-layer PHM application around NASA C-MAPSS. The first layer performs RUL prediction using multiple candidate models. The second layer converts predictive output into deterministic risk and recommendation signals and supports what-if scenario analysis. The third layer exposes the system through an interactive dashboard that connects operator-facing summaries, technical analysis, scenario comparison, and audit trails.

The main contributions are:
- a calibrated and benchmarked predictive layer with champion selection grounded in both accuracy and deployment constraints
- a deterministic agent layer that keeps risk, recommendations, and scenario execution auditable
- a dashboard that operationalizes the scientific narrative through decision, explanation, and traceability tabs
- a reproducible artifact package linking data, code, models, contracts, and runtime configuration

## 2. Related Work

The literature around C-MAPSS has primarily emphasized prediction performance, especially through machine-learning and deep-learning models for RUL estimation. Sequence models such as LSTM and GRU are frequently motivated by the temporal nature of degradation, while tree-based models remain strong tabular baselines. At the same time, PHM decision-support systems must confront issues that pure benchmark studies often leave implicit: uncertainty communication, actionability, interpretability, fallback behavior, and traceability.

This work positions itself between these two traditions. It uses C-MAPSS as the predictive benchmark foundation, but extends the contribution into an implemented PHM application. The dashboard, scenario pipeline, and audit trail are therefore not auxiliary materials; they are part of the research contribution because they show how model outputs become controlled maintenance-support decisions.

## 3. Methodology

### 3.1 Dataset and preprocessing

The system uses the four standard NASA C-MAPSS subsets (`FD001`-`FD004`). Preprocessing is implemented in `src/eda/run_plan1_eda.py` and frozen in `out/eda/05_preprocessing_config.json`. Low-variance features are removed, the training split is standardized with `StandardScaler`, and processed train/validation/test artifacts are exported as parquet files.

The selected predictive feature set is:
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

The operational learning target is capped RUL with cap `125`, while raw RUL is preserved for audit and analysis.

### 3.2 Predictive models

Four candidate models were implemented:
- `rf`
- `hgb`
- `lstm`
- `gru`

The tabular models use the processed selected-feature matrix directly. The sequence models use sliding windows built from the same selected features. Evaluation compares global and per-dataset RMSE / MAE as well as latency and stability spread across datasets.

### 3.3 Champion selection and uncertainty

The best raw RMSE was achieved by `gru`, but the final champion is `rf`. The final champion record reports:
- champion: `rf`
- fallback: `hgb`
- best overall raw RMSE: `gru`

The selection rule favors stable, integration-ready behavior rather than raw error alone. Predictions are accompanied by calibrated confidence bands derived from an empirical absolute-error policy.

### 3.4 Deterministic risk and recommendations

The agent layer computes `risk_level` and `risk_score` from:
- predicted RUL
- confidence-band width
- predictive service status

The same layer maps these values to maintenance recommendations and urgency. This keeps the decision layer deterministic and auditable.

### 3.5 Scenario methodology

Scenario execution follows an explicit deterministic pipeline:
1. parse intent
2. validate scenario
3. build scenario payload
4. run baseline prediction
5. run scenario prediction
6. compare baseline and scenario
7. generate interpretation

The LLM is optional and non-central. If available, it may help interpret natural-language scenario input or improve wording, but prediction, validation, risk, and comparison remain deterministic.

## 4. System Architecture

The project is implemented as a layered stack:

### Predictive Layer
This layer loads the selected feature schema, applies the stored scaler, runs the champion model, attaches a confidence band, and returns trace metadata.

### Agent Layer
This layer validates requests, trims payloads to the predictive feature subset, computes deterministic risk and recommendation outputs, executes scenario comparisons, and writes audit logs.

### Dashboard Layer
This layer provides manual and CSV-driven request input, surfaces decision outputs, supports analysis and scenarios, and exposes contracts and traceability in a technical audit tab.

The system communicates through explicit contracts frozen in generated artifacts. Service states such as `ok`, `fallback`, `degraded`, `error_validacion`, and `sin_datos` are propagated through the stack and surfaced in the UI.

## 5. Experiments

The experiments evaluate both scientific and engineering behavior.

### Predictive evaluation
Candidate models are compared on:
- global RMSE / MAE
- per-dataset RMSE / MAE
- latency
- stability spread

### Calibration and uncertainty
The confidence-band policy is evaluated to justify uncertainty visualization and conservative risk adjustments.

### Scenario analysis
Scenario experiments verify:
- deterministic execution
- baseline vs scenario comparison
- interpretability of low-impact and higher-impact changes

### Failure cases and reliability
The experiments also document:
- validation failures
- fallback behavior
- degraded states
- dashboard smoke results and contract integrity

## 6. Results

Global predictive metrics show:

| model | RMSE | MAE |
|---|---:|---:|
| `gru` | 17.42 | 13.19 |
| `rf` | 18.31 | 13.26 |
| `hgb` | 18.43 | 13.33 |
| `lstm` | 20.01 | 14.99 |

Despite the best raw RMSE belonging to `gru`, the final deployed champion is `rf`. This is a central result of the project: the final application prioritizes stable deployment behavior and fallback readiness over benchmark-only optimization.

Scenario analysis demonstrates that:
- the system can produce structured baseline-vs-scenario comparisons
- deterministic what-if execution is auditable
- some requested changes have very low effect because the deployed model uses only a selected feature subset and exhibits low local sensitivity for some features

Dashboard screenshots provide evidence that the system presents:
- decision outputs in `Summary`
- explanation and uncertainty in `Analysis`
- deterministic what-if comparison in `Scenarios`
- traceability in `Technical Audit`

## 7. Discussion

The choice of `rf` over `gru` illustrates the main engineering lesson of this work: the best benchmark model is not always the best deployed system model. A PHM application must balance accuracy, stability, latency, fallback behavior, and interpretability.

The project also shows that scenario analysis should not be interpreted only through domain intuition. If a requested change targets non-feature fields or locally insensitive features, the model response may be negligible. This is not necessarily a pipeline error; it may be a direct consequence of the deployed champion and feature-selection policy.

Cost and reliability considerations are explicitly addressed by keeping the LLM optional and non-central. The agent layer remains deterministic even without external model access. Safety and trust are further supported by validation rules, protected identifiers, service-state handling, and audit logs.

Limitations remain. The deployed champion is a single-row tabular model, the uncertainty policy is relatively simple, and scenario grammars remain constrained compared with full maintenance simulators. These limitations nevertheless provide useful opportunities for future work.

## 8. Conclusion

This paper presented a complete PHM application for NASA C-MAPSS that combines predictive modeling, deterministic decision support, scenario comparison, and dashboard-based explainability. The system demonstrates how benchmark-grade predictive methods can be embedded into a reproducible and auditable engineering artifact.

The main scientific result is a stable deployed predictive layer with calibrated uncertainty and documented champion selection. The main engineering result is the integration of prediction, risk logic, scenarios, and traceability into a coherent user-facing PHM system.

Future work should extend local explainability, scenario realism, and deployment-oriented experimentation while preserving the non-central role of optional LLM components.

# Experiments

## 1. Experimental goals

The evaluation is designed to answer four questions:

1. Which predictive model provides the best balance of performance and deployment readiness?
2. Is the predictive output sufficiently calibrated to support downstream deterministic risk logic?
3. Does the agent layer produce stable, interpretable, and auditable decision outputs?
4. Does the dashboard preserve decision, explanation, scenario, and audit information without contract drift?

## 2. Predictive evaluation protocol

The predictive experiments compare four models:
- `rf`
- `hgb`
- `lstm`
- `gru`

Primary metrics:
- RMSE
- MAE

Secondary engineering metrics:
- stability spread across CMAPSS subsets
- latency per sample

Primary artifacts:
- [out/predictive_layer/04_metrics_global_by_model.csv](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/predictive_layer/04_metrics_global_by_model.csv:1>)
- [out/predictive_layer/04_metrics_by_dataset_by_model.csv](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/predictive_layer/04_metrics_by_dataset_by_model.csv:1>)
- [out/predictive_layer/04_latency_by_model.csv](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/predictive_layer/04_latency_by_model.csv:1>)
- [out/predictive_layer/champion_record.json](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/predictive_layer/champion_record.json:1>)

## 3. Champion-selection validation

Champion selection is validated not only by raw RMSE but also by:
- stability across datasets
- integration readiness
- deterministic fallback availability

This is essential because the target system is an application, not only a benchmark leaderboard.

The selection rationale is documented in:
- [out/predictive_layer/04_champion_decision_record.md](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/predictive_layer/04_champion_decision_record.md:1>)

## 4. Calibration and uncertainty evaluation

The system attaches confidence bands to each RUL prediction using an empirical absolute-error policy.

Calibration evidence is drawn from:
- [out/predictive_layer/05_calibration_report.md](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/predictive_layer/05_calibration_report.md:1>)
- [out/predictive_layer/05_confidence_band_policy.json](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/predictive_layer/05_confidence_band_policy.json:1>)

The paper will use this evidence to justify:
- uncertainty visualization in the dashboard
- use of interval width inside deterministic risk scoring

## 5. Scenario evaluation

Scenario evaluation focuses on:
- deterministic what-if execution
- structured comparison between baseline and scenario outputs
- interpretation behavior under both low-impact and meaningful-impact perturbations

Evidence sources:
- [out/agent_layer/05_scenario_examples.json](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/agent_layer/05_scenario_examples.json:1>)
- [data/test_input.csv](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/data/test_input.csv:1>)
- [data/test_input_reference.md](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/data/test_input_reference.md:1>)

The paper should explicitly include:
- a low-impact scenario case
- at least one stronger perturbation case
- explanation of why some scenario changes have almost no effect

## 6. Failure-case evaluation

The application should be evaluated not only on successful paths but also on controlled failure or degraded paths.

Failure-related evidence includes:
- validation errors in scenario parsing
- service-state transitions
- fallback behavior in predictive serving
- audit-log traces of failed requests

Primary sources:
- [out/agent_layer/08_failure_modes.txt](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/agent_layer/08_failure_modes.txt:1>)
- [out/agent_layer/08_test_matrix.txt](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/agent_layer/08_test_matrix.txt:1>)
- [out/dashboard_layer/09_test_matrix.txt](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/dashboard_layer/09_test_matrix.txt:1>)

## 7. Dashboard and interaction validation

The dashboard should be evaluated as a scientific artifact, not only as a UI shell.

Validation targets:
- Summary communicates the decision layer
- Analysis exposes explanation and uncertainty
- Scenarios supports deterministic comparison
- Technical Audit exposes traceability

Evidence:
- [out/dashboard_layer/09_local_smoke_report.txt](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/dashboard_layer/09_local_smoke_report.txt:1>)
- [fig/dashboard/dashboard_v1_4.png](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/fig/dashboard/dashboard_v1_4.png>)
- [fig/dashboard/dashboard_v1_5.png](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/fig/dashboard/dashboard_v1_5.png>)
- [fig/dashboard/dashboard_v1_9.png](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/fig/dashboard/dashboard_v1_9.png>)

## 8. Planned figures and tables

### Tables
- global predictive metrics
- per-dataset predictive metrics
- latency by model
- scenario comparison examples
- failure-mode inventory

### Figures
- architecture diagram
- uncertainty / interval illustration
- scenario comparison chart
- dashboard screenshots for Summary, Analysis, Scenarios, and Technical Audit

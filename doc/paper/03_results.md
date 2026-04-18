# Results

## 1. Predictive model comparison

The predictive layer compared four candidate models:
- `gru`
- `rf`
- `hgb`
- `lstm`

Global metrics from [out/predictive_layer/04_metrics_global_by_model.csv](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/predictive_layer/04_metrics_global_by_model.csv:1>) show:

| model | RMSE | MAE |
|---|---:|---:|
| `gru` | 17.42 | 13.19 |
| `rf` | 18.31 | 13.26 |
| `hgb` | 18.43 | 13.33 |
| `lstm` | 20.01 | 14.99 |

Although `gru` achieved the lowest raw RMSE, the final deployed champion is `rf`, as documented in [out/predictive_layer/champion_record.json](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/predictive_layer/champion_record.json:1>).

## 2. Champion selection result

The final champion-selection outcome is:
- Champion: `rf`
- Fallback: `hgb`
- Best raw performer: `gru`

The deployed system therefore prioritizes:
- stability across subsets
- deployment readiness
- deterministic fallback behavior

This is a central result because the scientific contribution is not only “which model has the best score,” but “which model supports the most reliable PHM application.”

## 3. Per-dataset behavior

Per-dataset results from [out/predictive_layer/04_metrics_by_dataset_by_model.csv](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/predictive_layer/04_metrics_by_dataset_by_model.csv:1>) show variability across the four CMAPSS subsets, reinforcing the importance of stability-aware selection.

For example:
- `gru` performs especially well on `FD001`
- `rf` remains competitive and stable across all subsets
- the spread between best and worst subset performance is lower for `rf` than for the promoted sequence candidate

## 4. Uncertainty and calibration

The predictive layer returns a calibrated confidence band with each prediction. This band is later consumed by the agent layer to support both uncertainty visualization and conservative risk adjustments.

Calibration is not treated as a cosmetic add-on. It is embedded into:
- `Analysis` tab interval explanations
- deterministic `Risk Score` computation
- scenario-comparison interpretation

## 5. Scenario-analysis results

The scenario system produces:
- a proposed scenario payload
- change summary
- assumptions
- safety notes
- baseline vs scenario comparison
- operator-facing interpretation

The implemented scenario pipeline demonstrates two important findings:

1. Deterministic scenarios are auditable and reproducible.
2. Some requested changes produce very small `ΔRUL` and zero `ΔRisk Score` because:
   - the deployed model uses a selected feature subset only
   - some edited fields are not predictive features
   - some local perturbations are too weak to move the champion model output materially

This result is scientifically useful because it exposes the difference between:
- human-meaningful changes
- model-effective changes

## 6. Dashboard as scientific evidence

The dashboard is used in the paper not merely as a demo, but as evidence that the system has been integrated across layers.

Representative screenshots include:
- `Summary` tab for final decision presentation
- `Analysis` tab for uncertainty and interpretability
- `Scenarios` tab for what-if comparison
- `Technical Audit` tab for traceability

This supports the manuscript’s claim that the project is an end-to-end PHM artifact rather than only a modeling notebook pipeline.

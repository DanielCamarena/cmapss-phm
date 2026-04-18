# CMAPSS PHM App

This repository implements a predictive maintenance application for the NASA C-MAPSS turbofan benchmark. The app predicts Remaining Useful Life (RUL), converts that prediction into maintenance-oriented risk and recommendations, and exposes the workflow through a Streamlit dashboard.

## Overview

The project is organized as a three-layer PHM stack:

1. `Predictive Layer`
   - trains multiple RUL models
   - serves the deployed champion model
   - returns point RUL plus a calibrated confidence band

2. `Agent Layer`
   - converts predictive output into `Risk Level`, `Risk Score`, and recommendations
   - runs deterministic what-if scenarios
   - optionally uses an LLM only for intent parsing and explanation improvement

3. `Dashboard Layer`
   - provides operator-facing workflows for manual input and CSV upload
   - shows decision, interpretability, scenario comparison, and audit views

## Architecture

### Predictive -> Agent -> Dashboard

`Dashboard` collects a request payload with:
- `dataset_id`
- `unit_id`
- `cycle`
- `op_setting_1..3`
- `sensor_1..21`

`Agent Layer` trims that payload to the deployed predictive feature subset, calls the predictive service, computes deterministic risk and recommendation outputs, and returns a structured response to the dashboard.

`Predictive Layer` serves a single-row tabular inference path:
- selected features loaded from `out/eda/05_preprocessing_config.json`
- `StandardScaler` loaded from `out/processed/standard_scaler.joblib`
- champion model loaded from `out/predictive_layer/models`
- calibrated confidence band loaded from `out/predictive_layer/05_confidence_band_policy.json`

## Models and champion selection

The implemented candidate models are:
- `RandomForestRegressor` (`rf`)
- `HistGradientBoostingRegressor` (`hgb`)
- `LSTM`
- `GRU`

The current champion record is stored in [out/predictive_layer/champion_record.json](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/predictive_layer/champion_record.json:1>).

Current decision:
- Champion: `rf`
- Fallback: `hgb`
- Best raw RMSE overall: `gru`

Why `rf` won:
- `gru` had the best raw RMSE, but did not clear the promotion rule against the best tabular baseline
- `rf` had the best stability spread among the tabular candidates
- the project selected the most integration-ready stable model, not only the lowest raw RMSE

## Main project folders

- [data](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/data:1>) - C-MAPSS source files, samples, and test scenario inputs
- [src/eda](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/eda:1>) - Plan 1 EDA and preprocessing generation
- [src/research](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/research:1>) - Plan 2 research synthesis
- [src/predictive_layer](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/predictive_layer:1>) - model training, evaluation, calibration, and inference
- [src/agent_layer](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/agent_layer:1>) - deterministic risk logic, recommendations, and scenarios
- [src/dashboard_layer](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/dashboard_layer:1>) - Streamlit application
- [out](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out:1>) - generated artifacts, contracts, metrics, and audit outputs
- [fig](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/fig:1>) - dashboard and EDA figures

## How to run

### 1. Create the conda environment

```powershell
conda env create -f environment.yml
conda activate cmapss
```

If the environment already exists:

```powershell
conda activate cmapss
```

### 2. Launch the dashboard

From the project root:

```powershell
streamlit run src/dashboard_layer/app.py
```

### 3. Optional data configuration

The dashboard can use:
- manual input mode
- CSV upload mode
- an optional configured dataset path for fleet analysis

To preconfigure a dashboard dataset:

```powershell
$env:CMAPSS_DASHBOARD_DATASET_PATH="C:\path\to\dashboard_dataset.csv"
streamlit run src/dashboard_layer/app.py
```

## How to regenerate major artifacts

### Plan 1: EDA and preprocessing

```powershell
conda run -n cmapss python src/eda/run_plan1_eda.py
```

### Plan 2: research package

```powershell
conda run -n cmapss python src/research/run_plan2_research.py
```

### Plan 3: predictive layer

```powershell
conda run -n cmapss python -c "import os, runpy; os.environ['KMP_DUPLICATE_LIB_OK']='TRUE'; import torch; runpy.run_module('src.predictive_layer.run_plan3_predictive_layer', run_name='__main__')"
```

### Plan 4: agent layer

```powershell
conda run -n cmapss python -m src.agent_layer.run_plan4_agent_layer
```

### Plan 5: dashboard artifacts

```powershell
conda run -n cmapss python -m src.dashboard_layer.run_plan5_dashboard_layer
```

## Runtime notes

- The deployed predictive model is currently a tabular `rf`, not a sequence model.
- Scenario execution is deterministic and auditable.
- If `GEMINI_API_KEY` is set, the agent layer may use an LLM only for:
  - scenario-intent parsing fallback
  - explanation wording improvement
- LLM output is never the source of truth for prediction, risk, or comparison values.

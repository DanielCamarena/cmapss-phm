# Appendix: Reproducibility

## Environment

The project environment is defined in [environment.yml](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/environment.yml:1>) with a conda environment named `cmapss`.

## Main runtime commands

### Create environment

```powershell
conda env create -f environment.yml
conda activate cmapss
```

### Launch dashboard

```powershell
streamlit run src/dashboard_layer/app.py
```

### Regenerate Plan 1 artifacts

```powershell
conda run -n cmapss python src/eda/run_plan1_eda.py
```

### Regenerate Plan 2 artifacts

```powershell
conda run -n cmapss python src/research/run_plan2_research.py
```

### Regenerate Plan 3 artifacts

```powershell
conda run -n cmapss python -c "import os, runpy; os.environ['KMP_DUPLICATE_LIB_OK']='TRUE'; import torch; runpy.run_module('src.predictive_layer.run_plan3_predictive_layer', run_name='__main__')"
```

### Regenerate Plan 4 artifacts

```powershell
conda run -n cmapss python -m src.agent_layer.run_plan4_agent_layer
```

### Regenerate Plan 5 artifacts

```powershell
conda run -n cmapss python -m src.dashboard_layer.run_plan5_dashboard_layer
```

## Core reproducibility artifacts

- `data/train_FD001.txt` through `data/train_FD004.txt`
- `data/test_FD001.txt` through `data/test_FD004.txt`
- `out/processed/*.parquet`
- `out/processed/standard_scaler.joblib`
- `out/predictive_layer/models/*`
- `out/predictive_layer/champion_record.json`
- `out/agent_layer/audit_log.jsonl`
- `out/dashboard_layer/contracts_snapshot.json`

## Assumptions

- The deployed predictive champion is currently `rf`.
- Scenario execution is deterministic even if the LLM is unavailable.
- If `GEMINI_API_KEY` is configured, the LLM remains optional and non-central.

## Traceability note

The `Technical Audit` tab, contract snapshots, audit logs, and scenario JSON outputs are part of the reproducibility story, not only debugging aids. They help align the scientific manuscript with the actual implemented system.

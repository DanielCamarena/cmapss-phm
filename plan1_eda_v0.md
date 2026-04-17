# Plan 1 - EDA (C-MAPSS)
Plan ID: `plan1_eda`  
Layer: `predictive_layer` (Layer 1 / capa1)  
Version: `v1.0`  
Status: `active`  
Depends on: `none`  
Last updated: `2026-04-17`

## Goal
Build a reliable understanding of C-MAPSS data quality, structure, and temporal behavior to support robust RUL modeling.

## Scope
- Subsets: `FD001`, `FD002`, `FD003`, `FD004`
- Inputs: `data/train_*.txt`, `data/test_*.txt`, `data/RUL_*.txt`
- Outputs: `out/eda/*`, `fig/eda/*`, `out/processed/*`

## Preconditions
1. Activate environment: `conda activate cmapss`
2. Verify libraries: `python -c "import pandas,numpy,matplotlib,scipy,openpyxl; print('ok')"`
3. Ensure output folders exist: `out/eda`, `fig/eda`

## Phase 1 - Structural Inventory and Validation
### Tasks
1. Count rows per file and subset.
2. Validate expected column count (26 for train/test).
3. Check missing values and malformed rows.
4. Validate data types and suspicious ranges.
5. Validate test units vs. RUL label counts.

### Deliverables
- `out/eda/01_inventory_summary.csv`
- `out/eda/01_schema_report.txt`

## Phase 2 - Statistical Profiling
### Tasks
1. Compute per-variable statistics (mean, std, min, max, quantiles).
2. Split analysis by operational settings and sensors.
3. Detect constant or near-constant sensors.
4. Compute correlation matrices.

### Deliverables
- `out/eda/02_stats_global.csv`
- `out/eda/02_stats_by_dataset.csv`
- `fig/eda/correlation_heatmap_fd001.png` ... `fd004.png`

## Phase 3 - Temporal Analysis by Unit
### Tasks
1. Plot sensor trajectories by `unit_id` (representative sample).
2. Measure sequence length distribution.
3. Analyze trends for key sensors.
4. Detect operational regime shifts.

### Deliverables
- `out/eda/03_sequence_lengths.csv`
- `fig/eda/sensor_trends_fd001.png` ... `fd004.png`
- `fig/eda/unit_examples_fd001.png` ... `fd004.png`

## Phase 4 - RUL-Oriented Analysis
### Tasks
1. Build train RUL target (`max_cycle - cycle`).
2. Analyze RUL distributions (train and test labels).
3. Evaluate target capping options (for example 125/130).
4. Define final training target strategy.

### Deliverables
- `out/eda/04_rul_distribution.csv`
- `fig/eda/rul_histograms.png`
- `out/eda/04_target_definition.txt`

## Phase 5 - Baseline Preprocessing
### Tasks
1. Define final feature set.
2. Define normalization strategy.
3. Build temporal windows for sequence models.
4. Create leakage-safe splits by `unit_id` and time order.
5. Export processed train/valid/test artifacts.

### Deliverables
- `out/eda/05_feature_list.txt`
- `out/eda/05_preprocessing_config.json`
- `out/processed/train_processed.parquet`
- `out/processed/valid_processed.parquet`
- `out/processed/test_processed.parquet`

## Phase 6 - EDA Closure
### Tasks
1. Summarize key findings.
2. Document data risks and mitigation actions.
3. Define baseline modeling handoff.

### Deliverables
- `out/eda/06_findings_summary.md`
- `out/eda/06_risks_and_actions.md`
- `out/eda/06_baseline_plan.md`

## Success Criteria
- End-to-end traceability from raw data to processed datasets.
- Clear target definition and key sensor insights.
- Reproducible input pipeline for model training.

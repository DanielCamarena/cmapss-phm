# Plan 1 - EDA (C-MAPSS)
Plan ID: `plan1_eda`  
Layer: `predictive_layer` (Layer 1)  
Version: `v1.0`  
Status: `active`  
Depends on: `none`  
Last updated: `2026-04-17`  
Detailed source: `prompt.md`

## Goal
Build a reproducible understanding of NASA C-MAPSS data structure, quality, temporal behavior, and target construction so downstream RUL modeling can start from validated inputs rather than assumptions.

## Scope
- Subsets: `FD001`, `FD002`, `FD003`, `FD004`
- Raw inputs: `data/train_FD001.txt` ... `data/train_FD004.txt`, `data/test_FD001.txt` ... `data/test_FD004.txt`, `data/RUL_FD001.txt` ... `data/RUL_FD004.txt`
- Reference input: `data/readme.txt`
- Outputs: `out/eda/*`, `out/processed/*`, `fig/eda/*`

## Preconditions
1. Activate environment: `conda activate cmapss`
2. Verify key libraries: `python -c "import pandas,numpy,matplotlib,scipy,pyarrow; print('ok')"`
3. Ensure output folders exist: `out/eda`, `out/processed`, `fig/eda`
4. Confirm raw data availability for all four subsets before analysis starts.

## Phase 1 - Structural Inventory and Validation
### Tasks
1. Load each train, test, and RUL file with a reproducible parsing rule.
2. Validate expected shape and column count for train/test files.
3. Confirm that each test subset has a matching RUL label count by `unit_id`.
4. Check for missing values, malformed rows, duplicated rows, and impossible identifiers.
5. Produce a schema note with column naming conventions for downstream code.

### Deliverables
- `out/eda/01_inventory_summary.csv`
- `out/eda/01_schema_report.txt`
- `out/eda/01_data_quality_issues.csv`

### Exit Criteria
- All twelve raw files are readable without manual fixes.
- Column counts and row counts are documented for every subset.
- Any parsing anomaly is either resolved or recorded with an explicit mitigation note.

## Phase 2 - Statistical Profiling
### Tasks
1. Compute descriptive statistics for operational settings and sensor variables.
2. Compare distributions across `FD001` to `FD004`.
3. Flag constant, near-constant, or low-information sensors.
4. Compute correlation matrices and highlight strongly redundant variables.
5. Separate findings for operational settings versus sensor channels.

### Deliverables
- `out/eda/02_stats_global.csv`
- `out/eda/02_stats_by_dataset.csv`
- `out/eda/02_low_variance_sensors.csv`
- `fig/eda/02_correlation_heatmap_fd001.png`
- `fig/eda/02_correlation_heatmap_fd002.png`
- `fig/eda/02_correlation_heatmap_fd003.png`
- `fig/eda/02_correlation_heatmap_fd004.png`

### Exit Criteria
- Every raw feature has summary statistics saved.
- Low-information and highly redundant variables are explicitly listed.
- Cross-subset distribution differences are documented for later preprocessing decisions.

## Phase 3 - Temporal Analysis by Unit
### Tasks
1. Compute sequence length per `unit_id` for train and test subsets.
2. Plot representative unit trajectories for key sensors and operational settings.
3. Inspect monotonic, drifting, unstable, or regime-switching behavior over cycles.
4. Compare temporal behavior between single-condition and multi-condition subsets.
5. Identify sensors with visually useful degradation patterns for RUL modeling.

### Deliverables
- `out/eda/03_sequence_lengths.csv`
- `out/eda/03_temporal_notes.txt`
- `fig/eda/03_sensor_trends_fd001.png`
- `fig/eda/03_sensor_trends_fd002.png`
- `fig/eda/03_sensor_trends_fd003.png`
- `fig/eda/03_sensor_trends_fd004.png`
- `fig/eda/03_unit_examples_fd001.png`
- `fig/eda/03_unit_examples_fd002.png`
- `fig/eda/03_unit_examples_fd003.png`
- `fig/eda/03_unit_examples_fd004.png`

### Exit Criteria
- Sequence-length distributions are available for all subsets.
- Representative temporal plots exist for each subset.
- A shortlist of sensors with clear temporal signal is documented.

## Phase 4 - RUL-Oriented Target Analysis
### Tasks
1. Construct train-set RUL labels using `max_cycle - cycle`.
2. Profile train and test RUL distributions by subset.
3. Compare uncapped and capped target strategies, including common caps such as `125` and `130`.
4. Document the trade-off between realism, stability, and modeling simplicity.
5. Recommend a target policy for Plan 2 and Plan 3.

### Deliverables
- `out/eda/04_rul_distribution.csv`
- `out/eda/04_target_definition.txt`
- `fig/eda/04_rul_histograms.png`
- `fig/eda/04_rul_cap_comparison.png`

### Exit Criteria
- Train and test target behavior is quantified for all subsets.
- A primary target policy is selected and justified.
- Any subset-specific target caveat is documented for downstream modeling.

## Phase 5 - Baseline Preprocessing Design
### Tasks
1. Define canonical column names and feature groups.
2. Define normalization strategy with leakage-safe fit/transform boundaries.
3. Define optional feature filtering based on variance and stability findings.
4. Define sequence-window generation rules for sequence models.
5. Define train/validation splitting strategy by `unit_id` and time order.
6. Export baseline processed artifacts for future modeling experiments.

### Deliverables
- `out/eda/05_feature_list.txt`
- `out/eda/05_preprocessing_config.json`
- `out/eda/05_split_strategy.txt`
- `out/processed/train_processed.parquet`
- `out/processed/valid_processed.parquet`
- `out/processed/test_processed.parquet`

### Exit Criteria
- Preprocessing rules are documented precisely enough to reimplement without ambiguity.
- Processed datasets can be regenerated from raw data using the documented rules.
- Split policy prevents leakage across units and future cycles.

## Phase 6 - EDA Closure and Handoff
### Tasks
1. Summarize key structural, statistical, and temporal findings.
2. Document data risks, caveats, and mitigation actions.
3. Record assumptions that Plan 2 research and Plan 3 implementation must respect.
4. Produce a short modeling handoff note with recommended next decisions.

### Deliverables
- `out/eda/06_findings_summary.md`
- `out/eda/06_risks_and_actions.md`
- `out/eda/06_baseline_plan.md`

### Exit Criteria
- Findings are traceable from raw files to processed outputs.
- Risks and mitigations are explicit enough for downstream planning.
- Plan 2 can begin without reopening unresolved basic data questions.

## Success Criteria
- End-to-end traceability exists from raw NASA C-MAPSS files to processed artifacts.
- Data quality, target policy, and preprocessing decisions are documented with evidence.
- The project has a reproducible EDA handoff ready for research and predictive-layer implementation.

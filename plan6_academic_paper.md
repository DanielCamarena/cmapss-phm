# Plan 6 - Academic Paper Production
Plan ID: `plan6_academic_paper`  
Layer: `paper` (Cross-layer synthesis)  
Version: `v1.0`  
Status: `active`  
Depends on: `plan2_research`, `plan3_predictive_layer`, `plan4_agent_layer`, `plan5_dashboard_layer`  
Last updated: `2026-04-18`  
Detailed source: `prompt.md`

## Goal
Produce the final academic paper for the CMAPSS PHM project, aligned with the implemented system rather than a conceptual prototype, and structured as a standard scientific manuscript that integrates predictive modeling, agent-layer reasoning, and dashboard-based human interaction as one engineering artifact.

## Scope
- Paper output target: a complete manuscript draft suitable for journal or conference adaptation
- Scientific scope: C-MAPSS RUL prediction, deterministic risk logic, scenario analysis, and traceable dashboard integration
- Evidence sources:
  - `out/eda/*`
  - `out/research/*`
  - `out/predictive_layer/*`
  - `out/agent_layer/*`
  - `out/dashboard_layer/*`
  - `fig/eda/*`
  - `fig/dashboard/*`
- Implementation sources:
  - `src/predictive_layer/*`
  - `src/agent_layer/*`
  - `src/dashboard_layer/*`

## Paper Positioning
- Primary contribution type: engineering + applied AI system paper
- Application domain: predictive maintenance / prognostics and health management
- Core thesis: the project is not only a predictive model benchmark, but a deployable PHM decision system that couples:
  - calibrated RUL prediction
  - deterministic risk and recommendation logic
  - scenario-based what-if analysis
  - traceable dashboard interaction for technical and operator users

## Proposed Scientific Structure
1. `Abstract`
2. `Introduction`
3. `Related Work`
4. `Methodology`
5. `System Architecture`
6. `Experiments`
7. `Results`
8. `Discussion`
9. `Conclusion`

## Codebase-to-Paper Mapping
### Predictive methodology
- `src/predictive_layer/config.py`
- `src/predictive_layer/data_loader.py`
- `src/predictive_layer/train_rf.py`
- `src/predictive_layer/train_hgb.py`
- `src/predictive_layer/train_lstm.py`
- `src/predictive_layer/train_gru_or_tcn.py`
- `src/predictive_layer/evaluate_models.py`
- `src/predictive_layer/calibration.py`
- `src/predictive_layer/inference_service.py`

### Agent-layer methodology
- `src/agent_layer/orchestrator.py`
- `src/agent_layer/risk_engine.py`
- `src/agent_layer/recommender.py`
- `src/agent_layer/scenario_rules.py`
- `src/agent_layer/scenario_interpreter.py`
- `src/agent_layer/llm_client.py`
- `src/agent_layer/tools.py`

### Dashboard / engineering artifact
- `src/dashboard_layer/app.py`
- `src/dashboard_layer/backend_adapter.py`
- `src/dashboard_layer/components.py`

### Reproducibility and preprocessing
- `src/eda/run_plan1_eda.py`
- `src/research/run_plan2_research.py`
- `environment.yml`
- `README.md`
- `USER_GUIDE.md`

## Section-by-Section Objectives

## Section 1 - Abstract
### Objective
Write a compact summary of the problem, system, methods, key results, and engineering contribution.

### Must include
- C-MAPSS as the benchmark and data source
- multi-model predictive layer with champion selection
- deterministic agent layer for risk and recommendation logic
- dashboard as the interactive PHM artifact
- headline performance result and deployment-oriented contribution

### Required evidence
- `out/predictive_layer/champion_record.json`
- `out/predictive_layer/04_metrics_global_by_model.csv`

### Exit Criteria
- The abstract states both scientific and engineering contributions in under one page.

## Section 2 - Introduction
### Objective
Motivate why predictive maintenance systems need more than point RUL prediction and argue for a full PHM decision stack.

### Must include
- the operational importance of RUL estimation
- the gap between benchmark modeling and usable PHM applications
- the need for interpretability, uncertainty, safety, and traceability
- the role of scenarios and technical audit in trustworthy deployment

### Required figures/tables
- Figure: high-level project overview diagram (`Predictive -> Agent -> Dashboard`)

### Code/artifact mapping
- conceptual summary grounded in:
  - `README.md`
  - `src/dashboard_layer/app.py`
  - `out/dashboard_layer/01_screen_map_final.txt`

### Exit Criteria
- The introduction frames the work as an integrated AI system, not only a model comparison paper.

## Section 3 - Related Work
### Objective
Situate the paper relative to:
- CMAPSS RUL prediction literature
- PHM decision-support systems
- explainable and trustworthy AI in maintenance applications
- scenario / human-in-the-loop maintenance analytics

### Must include
- classic CMAPSS predictive literature
- works focused on sequence models and benchmark optimization
- works on deployable PHM systems and decision support
- distinction between benchmark-only studies and operationally traceable systems

### Required evidence
- `out/research/01_ficha_nasa_cmapss.txt`
- `out/research/01_ficha_damage_propagation.txt`
- `out/research/01_ficha_ramasso2014.txt`
- `out/research/01_cross_source_notes.txt`

### Exit Criteria
- The related-work section clearly positions this project as an end-to-end engineering artifact with scientific evaluation.

## Section 4 - Methodology
### Objective
Describe the data, preprocessing, target definition, candidate models, calibration, deterministic risk logic, and scenario methodology.

### Subsections
1. Dataset and problem definition
2. Preprocessing and feature selection
3. Predictive modeling candidates
4. Champion selection rule
5. Confidence-band calibration
6. Deterministic risk and recommendation policy
7. Scenario parsing, validation, and comparison pipeline

### Must include
- capped-RUL target definition
- selected feature subset
- tabular vs sequence modeling rationale
- calibrated confidence-band construction
- deterministic risk-score rules
- non-central LLM design for scenario intent parsing

### Required figures/tables
- Table: dataset subsets and operating conditions
- Table: selected predictive features vs removed low-variance features
- Table: candidate models and intended role
- Figure: scenario pipeline (`parse -> validate -> build payload -> predict -> compare -> explain`)

### Code/artifact mapping
- Data and preprocessing:
  - `src/eda/run_plan1_eda.py`
  - `out/eda/05_preprocessing_config.json`
  - `out/eda/04_target_definition.txt`
- Predictive methodology:
  - `src/predictive_layer/*`
  - `out/research/02_metodologia_propuesta.txt`
  - `out/research/02_model_matrix.csv`
- Risk and scenarios:
  - `src/agent_layer/*`
  - `out/agent_layer/02_risk_scoring_design.txt`
  - `out/agent_layer/05_scenario_assistant_flow.txt`
  - `out/agent_layer/06_scenario_assistant_policy.txt`

### Exit Criteria
- A reader can reconstruct the modeling and decision logic from the paper without reading the code.

## Section 5 - System Architecture
### Objective
Present the implemented AI application as a modular engineering system.

### Must include
- Predictive Layer responsibilities
- Agent Layer responsibilities
- Dashboard Layer responsibilities
- contract boundaries and data flow between layers
- traceability and audit paths

### Required figures/tables
- Figure: layered architecture diagram
- Figure: runtime inference flow
- Table: key contract fields exchanged across layers
- Table: service states (`ok`, `fallback`, `degraded`, `error_validacion`, `sin_datos`)

### Code/artifact mapping
- `src/predictive_layer/inference_service.py`
- `src/agent_layer/orchestrator.py`
- `src/agent_layer/tools.py`
- `src/dashboard_layer/backend_adapter.py`
- `src/dashboard_layer/app.py`
- `out/dashboard_layer/01_ui_backend_contract_v1.json`
- `out/dashboard_layer/03_mapping_fields_table.csv`
- `out/predictive_layer/06_output_schema_v1.json`
- `out/agent_layer/01_output_contract_v1.json`

### Exit Criteria
- The paper explains the app as a reproducible software artifact with explicit contracts and state handling.

## Section 6 - Experiments
### Objective
Define the evaluation protocol for both scientific performance and engineering behavior.

### Experiment groups
1. Predictive-model comparison
2. Champion-selection justification
3. Calibration and uncertainty behavior
4. Scenario-analysis behavior
5. Failure modes and degraded/fallback behavior
6. Dashboard / interaction validation

### Validation strategy
- Predictive performance:
  - compare RMSE and MAE across all candidate models
  - report per-dataset and global metrics
- Stability:
  - compare spread across subsets
- Scenario validation:
  - verify deterministic scenario execution
  - show baseline vs scenario deltas
  - analyze low-impact and high-impact scenario cases
- Engineering validation:
  - service states
  - local smoke tests
  - latency
  - auditability

### Required figures/tables
- Table: global model performance
- Table: per-dataset model performance
- Table: latency by model
- Figure: calibration / confidence-band summary
- Figure: scenario comparison example(s)
- Table: failure cases and observed handling

### Code/artifact mapping
- `out/predictive_layer/04_metrics_global_by_model.csv`
- `out/predictive_layer/04_metrics_by_dataset_by_model.csv`
- `out/predictive_layer/04_latency_by_model.csv`
- `out/predictive_layer/05_calibration_report.md`
- `out/predictive_layer/05_robustness_results.csv`
- `out/agent_layer/08_failure_modes.txt`
- `out/agent_layer/08_test_matrix.txt`
- `out/dashboard_layer/09_test_matrix.txt`
- `out/dashboard_layer/09_local_smoke_report.txt`

### Exit Criteria
- The paper’s experiments evaluate both prediction quality and system behavior under realistic conditions.

## Section 7 - Results
### Objective
Report the measured outcomes and connect them to the paper’s claims.

### Must include
- final champion selection result:
  - `rf` champion
  - `hgb` fallback
  - `gru` best raw RMSE but not promoted
- model-performance outcomes
- stability and latency observations
- scenario outcomes:
  - meaningful scenario cases
  - low-impact scenario cases
  - explanation of why some changes barely affect RUL
- dashboard evidence showing operator-facing outputs

### Required figures/tables
- Figure: final dashboard screenshot(s)
- Figure: Summary / Analysis / Scenarios examples
- Table: champion-selection summary
- Table: scenario comparison examples with `ΔRUL` and `ΔRisk Score`

### Code/artifact mapping
- `out/predictive_layer/champion_record.json`
- `out/predictive_layer/04_champion_decision_record.md`
- `fig/dashboard/dashboard_v1_*.png`
- `out/agent_layer/05_scenario_examples.json`
- `data/test_input.csv`
- `data/test_input_reference.md`

### Exit Criteria
- Results are presented as evidence, not only as implementation claims.

## Section 8 - Discussion
### Objective
Interpret the results, explain tradeoffs, and discuss engineering constraints.

### Must include
- why a stable tabular model was selected over a slightly better raw sequence model
- how uncertainty influences risk and recommendation logic
- why some scenario changes have little effect due to feature selection and local sensitivity
- limitations of single-row tabular serving
- cost, latency, and reliability considerations
- safety and interpretability constraints

### Engineering constraints to address
- cost:
  - keeping LLM optional and non-central
  - using deterministic risk/scenario execution
- latency:
  - tabular model serving and dashboard responsiveness
- reliability:
  - fallback model
  - explicit service states
- safety:
  - deterministic validation
  - protected identifiers
  - scenario safety notes

### Required evidence
- `out/predictive_layer/08_residual_risks.md`
- `out/predictive_layer/08_deploy_checklist.txt`
- `out/agent_layer/08_failure_modes.txt`
- `out/dashboard_layer/08_state_handling_guide.txt`
- `out/dashboard_layer/07_audit_ux_rules.txt`

### Exit Criteria
- The discussion addresses both scientific limitations and deployment tradeoffs honestly.

## Section 9 - Conclusion
### Objective
Close the paper by summarizing the scientific findings and engineering contribution.

### Must include
- the value of combining predictive modeling with deterministic decision support
- the contribution of the dashboard as a scientific demo and engineering artifact
- the role of traceability and auditability
- future work directions

### Suggested future work points
- richer local explanation / sensitivity methods
- broader scenario libraries and preset policies
- stronger fleet analytics and longitudinal evaluation
- online or near-real-time deployment experiments

### Exit Criteria
- The conclusion leaves a clear final claim about the contribution and next steps.

## Reproducibility Requirements
### Must document
- data source files in `data/`
- preprocessing pipeline
- selected features
- model artifacts and champion record
- environment setup via `environment.yml`
- runtime commands from `README.md`
- LLM optionality and non-central role
- assumptions used in scenarios and dashboard interactions

### Required tables/appendices
- Table: software environment and dependency stack
- Appendix: command-line entrypoints for Plans 1-5
- Appendix: contract and artifact inventory

### Code/artifact mapping
- `environment.yml`
- `README.md`
- `USER_GUIDE.md`
- `out/processed/standard_scaler.joblib`
- `out/predictive_layer/models/*`

### Exit Criteria
- Another researcher can reproduce the system setup and locate the main artifacts.

## Traceability and Auditability Requirements
### Must document
- audit-record generation
- trace payload fields
- scenario audit JSON
- Technical Audit tab behavior
- service-state handling and fallback visibility

### Required figures/tables
- Figure: Technical Audit screenshot
- Table: trace fields and their meaning
- Table: scenario-response contract

### Code/artifact mapping
- `src/agent_layer/orchestrator.py`
- `src/agent_layer/tools.py`
- `src/dashboard_layer/app.py`
- `out/agent_layer/audit_log.jsonl`
- `out/dashboard_layer/contracts_snapshot.json`
- `out/dashboard_layer/contract_integration_checklist.txt`

### Exit Criteria
- The paper makes traceability a first-class contribution, not a side note.

## Demo-to-Paper Narrative Mapping
### Objective
Connect the dashboard demo to the manuscript’s scientific claims.

### Narrative mapping
- `Summary` tab -> operational decision outcome
- `Analysis` tab -> interpretability and uncertainty
- `Scenarios` tab -> controlled what-if reasoning
- `Technical Audit` tab -> auditability and reproducibility

### Required figures
- one figure per core tab or a composite dashboard figure

### Exit Criteria
- The demo is clearly positioned as evidence of system integration, not only as a presentation artifact.

## Figure and Table Inventory
### Core figures
1. Layered system architecture
2. Predictive inference flow
3. Champion-selection summary chart
4. Model performance comparison
5. Confidence-band / uncertainty illustration
6. Summary-tab screenshot
7. Analysis-tab screenshot
8. Scenarios-tab screenshot
9. Technical Audit screenshot
10. Example scenario delta comparison

### Core tables
1. CMAPSS subsets and problem setup
2. Selected vs removed features
3. Candidate models and roles
4. Global model metrics
5. Per-dataset model metrics
6. Latency and engineering tradeoffs
7. Scenario examples and deltas
8. Failure modes and handling
9. Reproducibility checklist
10. Traceability / contract field mapping

## Writing Workflow

## Phase 1 - Evidence freeze and manuscript skeleton
### Tasks
1. Freeze the evidence artifacts that the paper will cite.
2. Define the final paper outline and subsection hierarchy.
3. Build a mapping table from code modules to manuscript sections.

### Deliverables
- `doc/paper/01_outline.md`
- `doc/paper/01_code_to_section_map.csv`
- `doc/paper/01_evidence_inventory.csv`

### Exit Criteria
- The manuscript skeleton is fixed before drafting begins.

## Phase 2 - Methodology and architecture drafting
### Tasks
1. Draft dataset, preprocessing, and modeling sections.
2. Draft agent-layer and scenario methodology.
3. Draft architecture and contracts section.

### Deliverables
- `doc/paper/02_methodology.md`
- `doc/paper/02_architecture.md`

### Exit Criteria
- Method and system sections are specific enough to support experiments and results.

## Phase 3 - Experiments and results drafting
### Tasks
1. Build paper-ready tables from predictive and scenario artifacts.
2. Select representative dashboard and scenario figures.
3. Draft experiments and results sections using frozen evidence.

### Deliverables
- `doc/paper/03_experiments.md`
- `doc/paper/03_results.md`
- `doc/paper/assets/`

### Exit Criteria
- Results are evidence-backed and figure/table references are stable.

## Phase 4 - Discussion, conclusion, and reproducibility
### Tasks
1. Draft discussion around tradeoffs, engineering constraints, and limitations.
2. Draft conclusion and future work.
3. Draft reproducibility and traceability appendix material.

### Deliverables
- `doc/paper/04_discussion.md`
- `doc/paper/04_conclusion.md`
- `doc/paper/appendix_reproducibility.md`

### Exit Criteria
- The manuscript can defend both scientific merit and engineering rigor.

## Phase 5 - Full paper assembly and final QA
### Tasks
1. Assemble the full paper draft in one manuscript file.
2. Verify consistency between text, numbers, screenshots, and code artifacts.
3. Check that claims about scenarios, auditability, and dashboard behavior match implementation.
4. Remove any stale claims from earlier planning-stage assumptions.

### Deliverables
- `doc/paper/final_paper_draft.md` or target venue source format
- `doc/paper/final_figure_table_index.csv`
- `doc/paper/final_claim_checklist.txt`

### Exit Criteria
- The paper is aligned with the implemented application.
- Every major claim is traceable to code or artifact evidence.
- The manuscript is ready for formatting into the target academic venue.

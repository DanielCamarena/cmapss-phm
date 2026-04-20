# Plan 7 - Presentation Deck Production
Plan ID: `plan7_ppt`  
Layer: `presentation` (Cross-layer synthesis)  
Version: `v1.0`  
Status: `active`  
Depends on: `plan2_research`, `plan3_predictive_layer`, `plan4_agent_layer`, `plan5_dashboard_layer`, `plan6_academic_paper`  
Last updated: `2026-04-19`  
Detailed source: `prompt.md`

## Goal
Produce the final PPT presentation for the CMAPSS PHM application, aligned with the implemented system and current academic-paper narrative, so the deck can support project demos, thesis defenses, technical reviews, and academic presentations.

## Scope
- Output target: a slide deck suitable for live presentation and export to PDF
- Core story: NASA C-MAPSS predictive maintenance application as an end-to-end AI engineering artifact
- Evidence sources:
  - `doc/paper/*`
  - `out/eda/*`
  - `out/research/*`
  - `out/predictive_layer/*`
  - `out/agent_layer/*`
  - `out/dashboard_layer/*`
  - `fig/dashboard/*`
  - `fig/eda/*`
- Implementation sources:
  - `src/predictive_layer/*`
  - `src/agent_layer/*`
  - `src/dashboard_layer/*`

## Presentation Positioning
- Primary format: technical-academic presentation deck
- Audience types:
  - academic evaluators
  - project supervisors
  - engineering reviewers
  - PHM / AI demo audiences
- Core thesis: the project is not just an RUL benchmark experiment, but a deployable PHM system integrating:
  - calibrated RUL prediction
  - deterministic risk and recommendation logic
  - scenario-based what-if analysis
  - dashboard-centered traceability and auditability

## Presentation Objectives
1. Explain the problem and why it matters.
2. Show the AI system architecture clearly.
3. Present the predictive-model portfolio and champion-selection logic.
4. Demonstrate how prediction becomes decision support.
5. Show dashboard workflows as evidence of system integration.
6. Present evaluation evidence, engineering tradeoffs, and limitations.
7. Leave the audience with a coherent scientific and engineering contribution claim.

## Proposed Deck Structure
1. `Title`
2. `Motivation and Problem`
3. `NASA C-MAPSS Context`
4. `Project Objectives and Contributions`
5. `System Architecture`
6. `Data and Preprocessing`
7. `Predictive Layer`
8. `Agent Layer`
9. `Dashboard Layer`
10. `Experiments and Results`
11. `Scenarios and Interpretability`
12. `Engineering Constraints`
13. `Limitations and Future Work`
14. `Conclusion`
15. `Backup / Appendix`

## Codebase-to-Slides Mapping
### Problem and methodology slides
- `doc/paper/main.tex`
- `doc/paper/02_methodology.md`
- `doc/paper/03_experiments.md`
- `doc/paper/03_results.md`

### Predictive-layer slides
- `src/predictive_layer/config.py`
- `src/predictive_layer/data_loader.py`
- `src/predictive_layer/evaluate_models.py`
- `src/predictive_layer/inference_service.py`
- `out/predictive_layer/champion_record.json`
- `out/predictive_layer/04_metrics_global_by_model.csv`
- `out/predictive_layer/04_metrics_by_dataset_by_model.csv`
- `out/predictive_layer/04_latency_by_model.csv`

### Agent-layer slides
- `src/agent_layer/orchestrator.py`
- `src/agent_layer/risk_engine.py`
- `src/agent_layer/recommender.py`
- `src/agent_layer/scenario_rules.py`
- `src/agent_layer/scenario_interpreter.py`
- `src/agent_layer/llm_client.py`
- `out/agent_layer/02_risk_scoring_design.txt`
- `out/agent_layer/05_scenario_examples.json`

### Dashboard and demo slides
- `src/dashboard_layer/app.py`
- `src/dashboard_layer/backend_adapter.py`
- `src/dashboard_layer/components.py`
- `fig/dashboard/dashboard_v1_4.png`
- `fig/dashboard/dashboard_v1_5.png`
- `fig/dashboard/dashboard_v1_8.png`
- `fig/dashboard/dashboard_v1_9.png`

## Slide-by-Slide Objectives

## Slide 1 - Title
### Objective
Introduce the project clearly as a PHM application rather than only a model experiment.

### Must include
- project title
- domain: predictive maintenance / PHM
- benchmark: NASA C-MAPSS
- presenter / affiliation / date

### Exit Criteria
- The first slide immediately communicates scope, domain, and system identity.

## Slide 2 - Motivation and Problem
### Objective
Explain why RUL prediction matters operationally and why point prediction alone is not enough.

### Must include
- maintenance decision challenge
- need for uncertainty, risk, and explainability
- gap between benchmark models and usable systems

### Required visuals
- compact problem statement diagram or 3-point challenge summary

### Exit Criteria
- The audience understands the practical motivation before methods appear.

## Slide 3 - NASA C-MAPSS Context
### Objective
Summarize the benchmark and the PHM prediction setting.

### Must include
- subsets `FD001`-`FD004`
- engine trajectories and cycle-based degradation
- operational settings and sensors

### Required figures/tables
- Table: C-MAPSS subset structure

### Required evidence
- `data/readme.txt`
- `doc/paper/main.tex`

### Exit Criteria
- The data source and task definition are clear in one slide.

## Slide 4 - Project Objectives and Contributions
### Objective
State what the project built and what is scientifically / technically novel.

### Must include
- predictive layer contribution
- deterministic agent-layer contribution
- dashboard contribution
- auditability / reproducibility contribution

### Exit Criteria
- The audience can distinguish project contributions from standard benchmark modeling.

## Slide 5 - System Architecture
### Objective
Present the three-layer system in one clean visual.

### Must include
- `Predictive -> Agent -> Dashboard`
- contracts / payload flow
- traceability path

### Required visuals
- architecture diagram adapted from the paper

### Required evidence
- `doc/paper/main.tex`
- `out/dashboard_layer/01_ui_backend_contract_v1.json`

### Exit Criteria
- The full system flow is understandable in under one minute.

## Slide 6 - Data and Preprocessing
### Objective
Show how raw C-MAPSS data becomes model-ready input.

### Must include
- selected predictive features
- removed low-variance features
- capped RUL target policy
- standardization / preprocessing flow

### Required figures/tables
- Table: selected vs removed features

### Required evidence
- `out/eda/05_preprocessing_config.json`
- `out/eda/04_target_definition.txt`

### Exit Criteria
- The audience understands the final predictive input representation.

## Slide 7 - Predictive Layer
### Objective
Present the candidate models and the serving model.

### Must include
- `rf`, `hgb`, `lstm`, `gru`
- tabular vs sequence distinction
- champion and fallback selection
- confidence-band output

### Required figures/tables
- Table: candidate models and roles
- chart: global model performance

### Required evidence
- `out/research/02_model_matrix.csv`
- `out/predictive_layer/04_metrics_global_by_model.csv`
- `out/predictive_layer/champion_record.json`

### Exit Criteria
- The audience knows what was trained, what won, and what was deployed.

## Slide 8 - Agent Layer
### Objective
Explain how RUL becomes decision support.

### Must include
- deterministic `risk_level`
- `risk_score`
- recommendation mapping
- service-state handling
- non-central LLM policy

### Required visuals
- compact decision pipeline diagram

### Required evidence
- `src/agent_layer/risk_engine.py`
- `src/agent_layer/recommender.py`
- `out/agent_layer/06_scenario_assistant_policy.txt`

### Exit Criteria
- The audience understands that decision logic is deterministic and auditable.

## Slide 9 - Dashboard Layer
### Objective
Present the UI as the project demo and engineering artifact.

### Must include
- `Summary`
- `Analysis`
- `Scenarios`
- `Technical Audit`

### Required figures
- dashboard screenshot collage or one slide per main tab

### Required evidence
- `fig/dashboard/dashboard_v1_4.png`
- `fig/dashboard/dashboard_v1_5.png`
- `fig/dashboard/dashboard_v1_9.png`
- `fig/dashboard/dashboard_v1_8.png`

### Exit Criteria
- The audience sees the full user-facing system, not only the backend.

## Slide 10 - Experiments and Results
### Objective
Present the main predictive results and champion-selection outcome.

### Must include
- global RMSE / MAE
- per-dataset behavior
- latency tradeoffs
- why `rf` was selected over `gru`

### Required figures/tables
- Table or chart: global model metrics
- Table: per-dataset metrics
- Table or bar chart: latency

### Required evidence
- `out/predictive_layer/04_metrics_global_by_model.csv`
- `out/predictive_layer/04_metrics_by_dataset_by_model.csv`
- `out/predictive_layer/04_latency_by_model.csv`
- `out/predictive_layer/04_champion_decision_record.md`

### Exit Criteria
- Results are presented as evidence-backed tradeoffs, not only leaderboard numbers.

## Slide 11 - Scenarios and Interpretability
### Objective
Show how the system supports what-if reasoning and explanation.

### Must include
- scenario parsing modes
- deterministic baseline-vs-scenario comparison
- `ΔRUL` and `ΔRisk Score`
- explanation of low-impact vs meaningful scenarios

### Required figures
- Scenarios tab screenshot
- scenario comparison figure

### Required evidence
- `out/agent_layer/05_scenario_examples.json`
- `data/test_input.csv`
- `data/test_input_reference.md`

### Exit Criteria
- The audience understands how scenario support works and what its limitations are.

## Slide 12 - Engineering Constraints
### Objective
Explain deployment tradeoffs beyond accuracy.

### Must include
- cost: optional LLM, deterministic fallback
- latency: model-serving and dashboard response
- safety: validation and protected identifiers
- reliability: fallback model and service states
- traceability: audit records and contracts

### Required evidence
- `out/predictive_layer/08_deploy_checklist.txt`
- `out/agent_layer/08_failure_modes.txt`
- `out/dashboard_layer/07_audit_ux_rules.txt`
- `out/dashboard_layer/08_state_handling_guide.txt`

### Exit Criteria
- The presentation addresses engineering realism, not just modeling outcomes.

## Slide 13 - Limitations and Future Work
### Objective
State current constraints honestly and show credible next steps.

### Must include
- tabular single-row serving limitation
- limited local sensitivity in some scenarios
- simple uncertainty policy
- richer explainability / fleet / scenario directions

### Required evidence
- `out/predictive_layer/08_residual_risks.md`
- `doc/paper/04_discussion.md`

### Exit Criteria
- Limitations are explicit and future work is concrete.

## Slide 14 - Conclusion
### Objective
Close with a clear scientific and engineering contribution statement.

### Must include
- benchmark + system integration message
- deployed champion lesson
- deterministic decision-support takeaway
- traceable PHM artifact contribution

### Exit Criteria
- The audience leaves with one coherent project claim.

## Slide 15 - Backup / Appendix
### Objective
Support Q&A without crowding the main story.

### Suggested backup topics
- full model metric tables
- service-state taxonomy
- feature list
- contract field mapping
- scenario parsing examples
- reproducibility commands

### Exit Criteria
- Key reviewer questions can be answered from the deck without improvising unsupported details.

## Required Figures and Tables
### Core figures
1. Layered system architecture
2. Predictive / decision flow
3. Dashboard Summary screenshot
4. Dashboard Analysis screenshot
5. Dashboard Scenarios screenshot
6. Dashboard Technical Audit screenshot
7. Scenario comparison chart
8. Champion-selection summary chart

### Core tables
1. C-MAPSS subsets and conditions
2. Selected vs removed features
3. Candidate models and roles
4. Global model metrics
5. Per-dataset model metrics
6. Latency / engineering tradeoffs
7. Scenario example comparison
8. Failure modes and handling

## Experiments and Validation Strategy for the Deck
### Must present
- predictive model comparison
- champion-selection rationale
- uncertainty / calibration narrative
- scenario-analysis examples
- failure / degraded-case handling
- dashboard integration evidence

### Presentation validation rules
- every result slide must trace to a real artifact
- screenshots must match the implemented dashboard
- no stale prototype claims
- no metric shown without a source artifact

### Exit Criteria
- The deck is evidence-backed and aligned with the implemented app.

## Reproducibility and Traceability Requirements
### Must document in slides or backup
- data source
- environment setup
- model artifacts
- service contracts
- audit and trace fields
- non-central role of the LLM

### Required evidence
- `environment.yml`
- `README.md`
- `USER_GUIDE.md`
- `out/dashboard_layer/contracts_snapshot.json`
- `out/agent_layer/audit_log.jsonl`

### Exit Criteria
- The presentation can defend system reproducibility and auditability during Q&A.

## Slide Asset and Source Mapping
### Primary text sources
- `doc/paper/main.tex`
- `doc/paper/README.md`
- `doc/paper/final_figure_table_index.csv`

### Primary metric sources
- `out/predictive_layer/*`
- `out/agent_layer/*`
- `out/dashboard_layer/*`

### Primary image sources
- `fig/dashboard/*`
- `fig/eda/*`

## Production Workflow

## Phase 1 - Deck framing and slide skeleton
### Tasks
1. Freeze the presentation audience, objective, and time budget.
2. Define the final slide sequence and speaking narrative.
3. Map each slide to a source artifact.

### Deliverables
- `doc/ppt/01_slide_outline.md`
- `doc/ppt/01_storyline_map.csv`

### Exit Criteria
- The deck structure is fixed before slide drafting starts.

## Phase 2 - Evidence freeze and slide content drafting
### Tasks
1. Freeze the figures, metrics, screenshots, and tables used by the deck.
2. Draft slide text at headline + evidence level.
3. Build concise speaker-note summaries.

### Deliverables
- `doc/ppt/02_evidence_inventory.csv`
- `doc/ppt/02_slide_content.md`

### Exit Criteria
- Every slide has a real source and a clear message.

## Phase 3 - Visual assembly
### Tasks
1. Create the final slide deck in PPT-compatible form.
2. Insert charts, screenshots, and diagrams.
3. Standardize layout, typography, and labeling.

### Deliverables
- `doc/ppt/final_presentation.pptx`
- `doc/ppt/assets/`

### Exit Criteria
- The deck is visually coherent and presentation-ready.

## Phase 4 - QA and rehearsal support
### Tasks
1. Verify consistency between slides, code, paper, and artifacts.
2. Prepare backup slides and anticipated Q&A notes.
3. Export a PDF version of the deck if needed.

### Deliverables
- `doc/ppt/final_slide_index.csv`
- `doc/ppt/final_claim_checklist.txt`
- `doc/ppt/final_presentation.pdf`

### Exit Criteria
- The deck is ready for defense, demo, or technical presentation.

## Success Criteria
- The PPT presents the CMAPSS PHM app as a coherent engineering and research system.
- The deck is aligned with the current implementation and paper package.
- Every major slide is traceable to real code, metrics, or screenshots.
- The presentation supports both live demo storytelling and technical evaluation.

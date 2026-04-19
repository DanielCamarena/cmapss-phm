# Slide Content Draft - CMAPSS PHM Presentation

## Slide 1 - Title
- Title: `Traceable Predictive Maintenance for NASA C-MAPSS`
- Subtitle: `An end-to-end PHM system with calibrated RUL prediction, deterministic decision support, and auditable scenarios`
- Footer: presenter, affiliation, date

## Slide 2 - Motivation and Problem
- Predictive maintenance needs more than a point estimate.
- Real PHM systems must communicate:
  - uncertainty
  - risk
  - actionability
  - traceability
- Benchmark modeling and deployable decision support are different problems.

## Slide 3 - NASA C-MAPSS Context
- Four benchmark subsets: `FD001-FD004`
- Each unit is a run-to-failure trajectory
- Inputs: three operational settings + sensor measurements
- Task: predict Remaining Useful Life before failure

## Slide 4 - Project Objectives and Contributions
- Build a calibrated predictive layer
- Add deterministic risk and recommendation logic
- Add scenario-based what-if analysis
- Deliver an interactive dashboard with technical auditability

## Slide 5 - System Architecture
- `Dashboard -> Agent -> Predictive`
- Contract-driven payload flow
- Predictive returns:
  - `rul_pred`
  - `confidence_band`
  - `model_version`
  - `trace`
- Agent returns:
  - `risk_level`
  - `risk_score`
  - `recommendation_text`
  - `service_status`
  - `audit_record_id`

## Slide 6 - Data and Preprocessing
- Selected predictive feature subset: 16 features
- Removed low-variance variables
- Training-only `StandardScaler`
- Operational target: capped RUL with cap `125`

## Slide 7 - Predictive Layer and Champion Selection
- Candidate models:
  - `rf`
  - `hgb`
  - `lstm`
  - `gru`
- Best raw RMSE: `gru`
- Deployed champion: `rf`
- Fallback: `hgb`
- Key reason: better stability / serving readiness tradeoff

## Slide 8 - Agent Layer and Deterministic Decision Logic
- Deterministic mapping from:
  - `rul_pred`
  - confidence width
  - service status
- Outputs:
  - `risk_level`
  - `risk_score`
  - recommendation text
- LLM role:
  - optional
  - non-central
  - only for scenario-intent interpretation / wording support

## Slide 9 - Dashboard Layer and User Workflow
- `Summary`: operational decision
- `Analysis`: explanation and uncertainty
- `Scenarios`: baseline vs what-if comparison
- `Technical Audit`: traceability and contracts

## Slide 10 - Experiments and Results
- Global predictive metrics
- Per-dataset performance
- Latency tradeoffs
- Champion-selection rationale
- Main message:
  - the best benchmark model was not the deployed model

## Slide 11 - Scenarios and Interpretability
- Scenarios compare:
  - baseline RUL
  - scenario RUL
  - risk score
  - risk level
- Parsing is:
  - deterministic first
  - optionally LLM-assisted
  - always validated deterministically
- Important result:
  - some edits have low impact because they target non-features or locally insensitive features

## Slide 12 - Engineering Constraints
- Cost:
  - optional LLM
  - deterministic core logic
- Latency:
  - tabular serving is fast and simple
- Reliability:
  - explicit fallback model
  - service-state propagation
- Safety:
  - scenario validation
  - protected identifiers
- Traceability:
  - audit records
  - contract snapshots

## Slide 13 - Limitations and Future Work
- Single-row tabular serving
- Simple uncertainty policy
- Some scenario edits produce low local sensitivity
- Future work:
  - richer local explanations
  - more realistic scenario libraries
  - stronger fleet analytics
  - deployment-time experiments

## Slide 14 - Conclusion
- This project is both:
  - a scientific PHM study
  - an implemented AI engineering artifact
- Main lesson:
  - deployable PHM quality depends on more than raw RMSE
- Final contribution:
  - prediction + deterministic decision support + dashboard traceability

## Slide 15 - Backup / Appendix
- full metrics
- feature list
- service states
- contract mapping
- reproducibility commands
- scenario parsing examples

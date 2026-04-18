from __future__ import annotations

import csv
import json
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]
DOC_DIR = ROOT / "doc"
OUT_EDA = ROOT / "out" / "eda"
OUT_PROCESSED = ROOT / "out" / "processed"
OUT_RESEARCH = ROOT / "out" / "research"


def ensure_dirs() -> None:
    OUT_RESEARCH.mkdir(parents=True, exist_ok=True)


def read_pdf_text(name: str) -> tuple[int, str]:
    reader = PdfReader(str(DOC_DIR / name))
    text = "\n".join((page.extract_text() or "") for page in reader.pages)
    return len(reader.pages), text


def load_plan1_context() -> dict:
    preprocessing = json.loads((OUT_EDA / "05_preprocessing_config.json").read_text(encoding="utf-8"))
    target_definition = (OUT_EDA / "04_target_definition.txt").read_text(encoding="utf-8")
    findings = (OUT_EDA / "06_findings_summary.md").read_text(encoding="utf-8")
    risks = (OUT_EDA / "06_risks_and_actions.md").read_text(encoding="utf-8")
    temporal = (OUT_EDA / "03_temporal_notes.txt").read_text(encoding="utf-8")
    return {
        "preprocessing": preprocessing,
        "target_definition": target_definition,
        "findings": findings,
        "risks": risks,
        "temporal": temporal,
    }


def write_text(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


def write_source_notes(pdf_info: dict[str, tuple[int, str]], plan1: dict) -> None:
    nasa_pages, nasa_text = pdf_info["NASA_CMAPSS.pdf"]
    damage_pages, damage_text = pdf_info["Damage Propagation Modeling.pdf"]
    ramasso_pages, ramasso_text = pdf_info["Ramasso2014.pdf"]

    nasa_note = f"""
Source note: NASA C-MAPSS user guide
File: doc/NASA_CMAPSS.pdf
Pages extracted: {nasa_pages}

Purpose
- Describe the simulator structure, configuration space, and generated variables used to build the benchmark.

Key technical takeaways
- C-MAPSS is a turbofan simulation benchmark intended to emulate engine behavior under varying flight and health conditions.
- The data structure aligns with the benchmark format observed in Plan 1: unit trajectories over cycles, three operational settings, and twenty-one retained sensors.
- The guide emphasizes simulation realism and modularity rather than direct field deployment assumptions, so any predictive system should treat benchmark performance as internal validation rather than production equivalence.
- Multi-condition behavior matters operationally; this supports Plan 1's warning that FD002 and FD004 may need condition-aware normalization.

Implications for Plan 3
- Preserve `dataset_id`, `unit_id`, and `cycle` through preprocessing and inference.
- Keep operational settings as first-class inputs instead of treating them as metadata only.
- Avoid assuming one global sensor distribution across all subsets without explicit validation.

Connection to Plan 1
- Plan 1 confirmed consistent parsing across all subsets and identified a reduced baseline feature set after low-variance filtering.
- The simulator documentation supports keeping operating-condition information in the predictive contract because it materially changes the signal context.
"""
    write_text(OUT_RESEARCH / "01_ficha_nasa_cmapss.txt", nasa_note)

    damage_note = f"""
Source note: Damage Propagation Modeling for Aircraft Engine Run-to-Failure Simulation
File: doc/Damage Propagation Modeling.pdf
Pages extracted: {damage_pages}

Purpose
- Explain how degradation was injected into the turbofan simulation used to generate run-to-failure data.

Key technical takeaways
- The benchmark faults are simulated via deterioration of module flow and efficiency, with damage growth imposed over time.
- Failure is related to a health-index style operational margin criterion rather than a direct observed sensor threshold.
- Fault growth is progressive and suitable for RUL framing, but the benchmark remains a synthetic approximation of real maintenance conditions.
- The paper positions the task clearly as remaining useful life estimation in cycles.

Implications for Plan 3
- Sequence-aware models are well motivated because degradation accumulates over time rather than appearing as independent static samples.
- Calibration and uncertainty reporting matter because the benchmark labels reflect simulated failure progression, not direct physical failure measurements from field assets.
- Robustness testing should include partial missing data and operating-condition shifts because the generation process couples degradation with complex sensor responses.

Connection to Plan 1
- Plan 1 selected capped RUL with raw target retention. That is compatible with the benchmark's progressive-failure framing while avoiding early-life domination during optimization.
- The exported processed artifacts should retain raw identifiers so later evaluation can remain traceable to the simulated run-to-failure trajectories.
"""
    write_text(OUT_RESEARCH / "01_ficha_damage_propagation.txt", damage_note)

    ramasso_note = f"""
Source note: Review and Analysis of Algorithmic Approaches Developed for Prognostics on CMAPSS Dataset
File: doc/Ramasso2014.pdf
Pages extracted: {ramasso_pages}

Purpose
- Summarize how the PHM literature has used CMAPSS and what methodological pitfalls appear repeatedly.

Key technical takeaways
- The survey highlights several recurring difficulty sources: sensor noise, operating-condition variability, and multiple simultaneous fault modes.
- Preprocessing, feature selection, condition handling, uncertainty management, and evaluation consistency are all major determinants of benchmark performance.
- The literature review argues for clearer and more consistent comparison rules across publications, especially around dataset interpretation and metric reporting.
- CMAPSS is useful not only for prediction models but also for testing feature extraction, feature selection, health assessment, and uncertainty workflows.

Implications for Plan 3
- Compare candidate models under one consistent preprocessing and evaluation regime.
- Report per-subset performance instead of only one global score.
- Preserve a tabular baseline even if a sequence model is expected to win, because literature comparisons are often confounded by inconsistent baselines.

Connection to Plan 1
- Plan 1's documented risks around condition-aware normalization, feature pruning, and capped targets map directly to the survey's warnings about preprocessing sensitivity and evaluation inconsistency.
- The reduced feature list and proposed 30/50-step windows provide a grounded baseline rather than arbitrary modeling choices.
"""
    write_text(OUT_RESEARCH / "01_ficha_ramasso2014.txt", ramasso_note)

    cross_source = f"""
Cross-source synthesis

Common agreements
- CMAPSS is a valid benchmark for data-driven RUL development when the task is framed as cycle-based degradation forecasting.
- Operating conditions and degradation dynamics materially affect sensor behavior and must influence preprocessing and evaluation.
- Benchmark comparisons are only useful when target policy, preprocessing, and metrics are explicitly documented.

Main cautions
- The data are simulated, so benchmark success does not equal field-readiness.
- Complex subsets with multiple conditions or multiple fault modes require stronger robustness checks than single-condition subsets.
- Reported gains can be misleading when papers use inconsistent target capping or hidden preprocessing differences.

Direct link to Plan 1 outputs
- Target policy from Plan 1: capped RUL at 125 as default, with uncapped raw RUL preserved.
- Preprocessing from Plan 1: train-only `StandardScaler`, reduced feature set, leakage-safe unit-based split.
- Risks from Plan 1: multi-condition normalization, sensitivity to feature removal, and the need for grouped cross-validation in later model comparison.
"""
    write_text(OUT_RESEARCH / "01_cross_source_notes.txt", cross_source)


def write_problem_and_method(plan1: dict) -> None:
    preprocessing = plan1["preprocessing"]
    selected_features = preprocessing["selected_features"]
    removed_features = preprocessing["removed_low_variance_features"]

    problem_definition = f"""
Predictive problem definition

Task
- Predict remaining useful life in cycles for a given engine trajectory from CMAPSS sensor and operational-setting data.

Prediction unit
- Primary unit: row-level or window-level observations tied to `dataset_id`, `unit_id`, and `cycle`.
- Business-facing unit: latest known state of one engine trajectory for downstream risk and recommendation layers.

Required inputs
- `dataset_id`
- `unit_id`
- `cycle`
- operational settings: `op_setting_1`, `op_setting_2`, `op_setting_3`
- retained baseline features from Plan 1: {", ".join(selected_features)}

Recommended target policy
- Default supervised target: `rul_capped` with cap `125`
- Audit target retained in storage: uncapped raw `rul`

Known benchmark difficulty drivers
- FD002 and FD004 combine multiple operating conditions.
- FD003 and FD004 contain multiple fault modes.
- Sensor noise and long early-life trajectories can skew optimization if uncapped targets dominate training.
"""
    write_text(OUT_RESEARCH / "02_problem_definition.txt", problem_definition)

    model_rows = [
        {
            "model_family": "RandomForestRegressor",
            "input_shape": "row-level tabular",
            "strengths": "strong baseline, robust to scaling noise, fast iteration",
            "weaknesses": "limited temporal memory, larger model artifacts",
            "recommended_role": "baseline",
            "priority": "high",
        },
        {
            "model_family": "HistGradientBoostingRegressor",
            "input_shape": "row-level tabular",
            "strengths": "fast training, competitive baseline, interpretable feature importance",
            "weaknesses": "requires handcrafted temporal features or lag summaries",
            "recommended_role": "baseline or challenger",
            "priority": "high",
        },
        {
            "model_family": "LSTM",
            "input_shape": "windowed sequence",
            "strengths": "captures temporal degradation patterns directly",
            "weaknesses": "higher training cost, more sensitive to window design",
            "recommended_role": "primary challenger",
            "priority": "high",
        },
        {
            "model_family": "GRU or TCN",
            "input_shape": "windowed sequence",
            "strengths": "sequence modeling with lower runtime or better optimization behavior",
            "weaknesses": "more implementation complexity than tabular baselines",
            "recommended_role": "primary challenger",
            "priority": "high",
        },
        {
            "model_family": "Hybrid tabular + sequence ensemble",
            "input_shape": "row-level plus sequence outputs",
            "strengths": "can combine stable baseline and temporal model",
            "weaknesses": "highest orchestration complexity",
            "recommended_role": "optional stretch",
            "priority": "medium",
        },
    ]
    with (OUT_RESEARCH / "02_model_matrix.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(model_rows[0].keys()))
        writer.writeheader()
        writer.writerows(model_rows)

    methodology = f"""
Proposed predictive methodology

Primary direction
- Use a contract-first predictive layer with one tabular baseline track and one sequence-model track.
- Start from the Plan 1 processed artifacts and preserve raw identifiers for traceability.

Feature policy
- Keep the Plan 1 retained feature set as the default modeling input: {", ".join(selected_features)}.
- Do not permanently ban removed features ({", ".join(removed_features)}); treat them as excluded from the baseline only.

Target policy
- Optimize primarily on capped RUL with cap 125.
- Retain raw uncapped RUL for ablation, calibration, and audit.

Candidate model strategy
- Baseline: HistGradientBoostingRegressor and RandomForestRegressor on engineered row-level features.
- Sequence challengers: LSTM and GRU or TCN using 30-step and 50-step windows from Plan 1.
- Optional ensemble only after one sequence model and one tabular model are stable and comparable.

Selection philosophy
- Choose the champion using both predictive quality and integration readiness.
- Favor models that maintain stable per-subset performance over models that only optimize one global score.
"""
    write_text(OUT_RESEARCH / "02_metodologia_propuesta.txt", methodology)

    target_policy = """
Target policy decision

Primary target
- `rul_capped` with cap `125`

Why this is the default
- Plan 1 showed the need to avoid long early-life trajectories dominating optimization.
- The damage-propagation benchmark is still a cycle-to-failure problem, so capped RUL remains consistent with the intended task while improving optimization balance.
- The literature review warns that inconsistent target definitions make CMAPSS comparisons unreliable; using one explicit default resolves that risk.

Secondary target
- `rul_linear` uncapped

How to use it
- Keep uncapped RUL in stored artifacts and use it for ablations, calibration review, and technical audit outputs.
"""
    write_text(OUT_RESEARCH / "02_target_policy_decision.txt", target_policy)


def write_contracts_and_pipeline(plan1: dict) -> None:
    preprocessing = plan1["preprocessing"]
    payload_example = {
        "request": {
            "dataset_id": "FD001",
            "unit_id": 1,
            "cycle": 192,
            "op_settings": {
                "op_setting_1": 0.0012,
                "op_setting_2": -0.0004,
                "op_setting_3": 100.0,
            },
            "sensors": {feature: "float" for feature in preprocessing["selected_features"] if feature.startswith("sensor_")},
            "source": "dashboard.manual_input",
        },
        "response": {
            "rul_pred": 37.4,
            "confidence_band": {"lower": 30.2, "upper": 44.8, "method": "empirical_calibration"},
            "target_policy": {"name": "rul_capped", "cap": 125},
            "model_version": "predictive-layer-v1/champion",
            "service_status": "ok",
            "trace": {
                "dataset_id": "FD001",
                "preprocessing_version": "plan1-baseline-v1",
                "feature_schema_version": "v1",
            },
            "timestamp": "ISO-8601",
        },
    }

    api_contract = f"""
RUL layer API contract

Input contract
- Required identifiers: `dataset_id`, `unit_id`, `cycle`
- Required operating context: `op_setting_1`, `op_setting_2`, `op_setting_3`
- Required sensor payload: baseline selected features from Plan 1 preprocessing
- Optional context: source metadata, ingestion timestamp, operator note

Output contract
- `rul_pred`: numeric prediction in cycles
- `confidence_band`: lower, upper, and method
- `target_policy`: target name and cap if applicable
- `model_version`
- `service_status`: `ok|degraded|fallback|error_validacion|sin_datos`
- `trace`: preprocessing version, feature schema version, dataset id
- `timestamp`

Design constraints
- Output must stay serializable and consumable by later agent and dashboard layers.
- Errors must be structured rather than raised as raw stack traces.
"""
    write_text(OUT_RESEARCH / "03_api_contract_rul_layer.txt", api_contract)

    inference_pipeline = """
Inference pipeline design

1. Validate request schema and required fields.
2. Normalize payload into canonical CMAPSS column names.
3. Apply the preprocessing contract learned on the training split only.
4. Route input through the champion model.
5. Convert raw prediction into user-facing `rul_pred`.
6. Attach confidence band from calibration policy.
7. Emit trace metadata and service status.
8. Log audit record for downstream technical inspection.

Out-of-distribution handling
- If feature ranges are outside expected training support, return `degraded` with an OOD note rather than silently treating the prediction as fully reliable.

Fallback behavior
- If the champion model is unavailable, use the best validated tabular baseline and mark `service_status=fallback`.
"""
    write_text(OUT_RESEARCH / "03_inference_pipeline.txt", inference_pipeline)

    (OUT_RESEARCH / "03_output_payload_example.json").write_text(json.dumps(payload_example, indent=2), encoding="utf-8")

    error_policy = """
Error policy

Validation errors
- Missing identifiers or missing required features: `error_validacion`
- Empty or non-parsable numeric values: `error_validacion`

Data sufficiency errors
- No usable history for a sequence model: downgrade to tabular fallback if available, otherwise `sin_datos`

System errors
- Model artifact unavailable: `fallback` if challenger or baseline exists, otherwise `degraded`
- Preprocessing schema mismatch: `degraded` and block prediction if feature alignment cannot be trusted

Operator-facing rule
- Every non-`ok` response must include a short explanation string suitable for dashboard display and a technical reason suitable for audit logs.
"""
    write_text(OUT_RESEARCH / "03_error_policy.txt", error_policy)


def write_evaluation_and_acceptance() -> None:
    eval_protocol = """
Evaluation protocol

Primary comparison target
- capped RUL with cap 125

Secondary comparison target
- uncapped linear RUL

Primary metrics
- RMSE
- MAE

Secondary metrics
- per-subset RMSE and MAE
- performance by RUL band: early-life, mid-life, late-life
- latency per inference request
- robustness under noise and partial missing features

Validation rules
- Keep splits grouped by `unit_id`
- Preserve cycle order inside each unit
- Do not fit scalers or feature transforms on validation or test units
- Report results separately for FD001, FD002, FD003, and FD004
"""
    write_text(OUT_RESEARCH / "04_eval_protocol.txt", eval_protocol)

    metric_definitions = """
Metric definitions

RMSE
- Main optimization metric for champion selection because large late-life misses should be penalized.

MAE
- Secondary stability metric because it is easier to interpret in cycles.

Subset stability
- Difference between best and worst subset RMSE should be monitored explicitly to prevent one-model-overfits-one-subset decisions.

Optional PHM score
- Include for comparability with benchmark literature if implemented consistently and documented clearly.
"""
    write_text(OUT_RESEARCH / "04_metric_definitions.txt", metric_definitions)

    robustness = """
Robustness test plan

1. Add controlled Gaussian noise to selected sensor channels.
2. Mask small subsets of sensor values to simulate partial missing input.
3. Compare simple subsets (FD001, FD003) versus multi-condition subsets (FD002, FD004).
4. Compare performance by RUL bands to detect late-life instability.
5. Record whether fallback predictions remain within acceptable error envelopes.
"""
    write_text(OUT_RESEARCH / "04_robustness_test_plan.txt", robustness)

    acceptance = """
Acceptance criteria

Baseline acceptance
- At least one tabular baseline trains successfully and produces fully traceable predictions.
- Per-subset metrics are reported for all four datasets.

Champion promotion rules
- Candidate must improve global RMSE by at least 5% over the best tabular baseline or materially improve per-subset stability.
- No subset may degrade by more than 10% RMSE relative to the best available baseline without an explicit waiver.
- Confidence-band generation and structured service status must be implemented.
- Median single-request inference latency should remain operationally reasonable for local dashboard use.

Release gate
- End-to-end smoke test from processed input to structured output must pass before agent-layer integration begins.
"""
    write_text(OUT_RESEARCH / "04_acceptance_criteria.txt", acceptance)


def write_backlog_and_release() -> None:
    backlog = """
Integration backlog for Plan 3

P0
- Implement row-level tabular training baselines.
- Implement deterministic preprocessing loader from Plan 1 config.
- Define the v1 inference schema and structured output payload.
- Add evaluation scripts that report global and per-subset metrics.

P1
- Implement sequence-model training with 30-step and 50-step windows.
- Add calibration or empirical confidence-band estimation.
- Add fallback routing between champion and stable baseline.

P2
- Add optional ensemble or hybrid strategies.
- Add expanded robustness and drift checks.
- Add richer trace and monitoring outputs for higher layers.
"""
    write_text(OUT_RESEARCH / "05_integration_backlog.txt", backlog)

    release_plan = """
Release plan

MVP
- One trained baseline model
- Reproducible preprocessing
- One inference service returning structured RUL output

V1
- Champion versus challenger comparison
- Confidence band policy
- Dashboard-consumable service states

V2
- Robustness hardening
- Better calibration and monitoring
- Optional ensemble or advanced sequence architecture
"""
    write_text(OUT_RESEARCH / "05_release_plan.txt", release_plan)

    handoff = """
Plan 3 handoff checklist

- Plan 1 processed parquet artifacts exist and are readable
- Target policy is frozen: capped RUL 125 primary, raw RUL retained
- Baseline feature set is frozen for first-pass modeling
- Grouped unit-based validation is required
- Output payload must include traceability metadata and service status
- Per-subset reporting is mandatory
"""
    write_text(OUT_RESEARCH / "05_plan3_handoff_checklist.txt", handoff)


def write_closure() -> None:
    master_plan = """
Master plan for the RUL layer

Chosen direction
- Build one rigorous predictive layer that compares stable tabular baselines with sequence challengers under one controlled preprocessing and evaluation regime.

Why this is the right direction
- It respects the benchmark's time-dependent degradation process.
- It keeps a simple baseline for reproducibility and fallback.
- It addresses the major literature risks: inconsistent preprocessing, weak subset reporting, and unclear target choices.

Immediate next step
- Execute Plan 3 with baseline tabular models first, then sequence challengers, then champion selection and contract hardening.
"""
    write_text(OUT_RESEARCH / "06_master_plan_rul_layer.txt", master_plan)

    risks = """
Research risks and mitigations

- Risk: complex subsets may favor condition-aware or regime-aware preprocessing.
Mitigation: require per-subset reporting and compare failures by dataset complexity.

- Risk: a sequence model may outperform globally but be too brittle for integration.
Mitigation: include service-state rules and keep a tabular fallback.

- Risk: target capping can distort early-life behavior.
Mitigation: retain raw RUL and run ablation checks on uncapped targets.

- Risk: literature comparisons can be misleading if metric definitions drift.
Mitigation: freeze metric definitions and report them alongside every model result.
"""
    write_text(OUT_RESEARCH / "06_risks_mitigations.txt", risks)

    open_questions = """
Open questions

- Should operating conditions be normalized globally or by inferred regime for FD002 and FD004?
- Which sequence architecture offers the best quality-to-complexity trade-off in this repository: LSTM, GRU, or TCN?
- Is the optional PHM scoring metric needed for stakeholder comparison, or are RMSE and MAE sufficient for the first release?
- Should confidence bands be derived empirically from residuals or from model ensembles?
"""
    write_text(OUT_RESEARCH / "06_open_questions.txt", open_questions)


def main() -> None:
    ensure_dirs()
    pdf_info = {
        "NASA_CMAPSS.pdf": read_pdf_text("NASA_CMAPSS.pdf"),
        "Damage Propagation Modeling.pdf": read_pdf_text("Damage Propagation Modeling.pdf"),
        "Ramasso2014.pdf": read_pdf_text("Ramasso2014.pdf"),
    }
    plan1 = load_plan1_context()
    write_source_notes(pdf_info, plan1)
    write_problem_and_method(plan1)
    write_contracts_and_pipeline(plan1)
    write_evaluation_and_acceptance()
    write_backlog_and_release()
    write_closure()
    print("Plan 2 research execution complete.")
    print(f"Artifacts written to: {OUT_RESEARCH}")


if __name__ == "__main__":
    main()

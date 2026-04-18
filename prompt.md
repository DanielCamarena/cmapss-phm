# Base Guide - CMAPSS PHM App Replication

## 1) Project statement

This project develops a functional AI application for predictive maintenance of turbofan engines using the NASA C-MAPSS benchmark.

The app is organized in three layers:
- `predictive_layer` (Layer 1): RUL prediction.
- `agent_layer` (Layer 2): risk logic, recommendations, and scenario assistant.
- `dashboard_layer` (Layer 3): final user-facing dashboard.

Target outcome:
- ingest sensor and operational data,
- estimate remaining useful life (RUL),
- compute risk level and risk score,
- produce actionable maintenance recommendations,
- present results in an interactive and traceable dashboard.

---

## 2) Plan naming and version convention (mandatory)

Use exactly these plan files:
- `plan1_eda.md`
- `plan2_research.md`
- `plan3_predictive_layer.md`
- `plan4_agent_layer.md`
- `plan5_dashboard_layer.md`

Each plan must include this metadata block at the top:
- `Plan ID`
- `Layer`
- `Version` (semantic format, for example `v1.0`, `v1.1`)
- `Status` (`draft|active|implemented|superseded`)
- `Depends on`
- `Last updated` (YYYY-MM-DD)
- `Detailed source` (link to detailed `.txt` plan)

Dependency rules:
- Plan 3 depends on Plan 1 and Plan 2.
- Plan 4 depends on Plan 3.
- Plan 5 depends on Plan 3 and Plan 4.

---

## 3) Layer prompts used to produce planning files

### Plan 1 prompt
Create a work plan to explore NASA C-MAPSS data, with executable deliverables and explicit exit criteria. Save it as `plan1_eda.md`.

### Plan 2 prompt
Create a work plan to review documents/references and define the predictive RUL methodology for the application. Save it as `plan2_research.md`.

### Plan 3 prompt
Create a work plan to implement `predictive_layer` (multi-model training, champion selection, inference contract, and integration readiness). Save it as `plan3_predictive_layer.md`.

### Plan 4 prompt
Create a work plan to implement `agent_layer` (risk logic, recommendations, LLM-assisted scenarios, deterministic fallback, and contract governance). Save it as `plan4_agent_layer.md`.

### Plan 5 prompt
Create a work plan to implement the final dashboard in `src/dashboard_layer`, aligned with current implementation:
- tabs: `Summary`, `Analysis`, `Scenarios`, `Technical Audit`
- integration with `predictive_layer` and `agent_layer`
- service states and traceability
Save it as `plan5_dashboard_layer.md`.

---

## 4) Dashboard

### Summary

Refine the Summary tab behavior and data logic.

1. Risk Score usage:
- Do not display Risk Score as a standalone metric.
- Use it only to support the Risk Level interpretation.
- Integrate it into the explanation text (e.g., “Condition is healthy due to low risk score”).
- Keep the UI focused on clear labels like “HEALTHY”, not raw numeric scores.

2. Risk communication:
- Risk Level must be the primary status indicator.
- Priority codes (P1, P2, P3) must not be shown as standalone labels.
- Express urgency in plain language within the recommendation.

3. RUL evolution:
- The “Recent RUL Evolution” chart must be computed using historical data from the same unit_id.
- When a CSV is loaded:
  - filter rows by selected unit_id
  - sort by cycle
  - compute predicted RUL for the last N cycles
- The chart must show a meaningful trend, not a single point.

4. Fallback behavior:
- If no historical data is available:
  - either hide the chart
  - or clearly indicate “insufficient history”

5. Consistency:
- Ensure the RUL trend aligns with the current prediction.
- The trend must help interpret degradation (stable / declining / rapidly declining).

Explain the required data flow and implement the changes.

### Analysis

Refactor the Analysis tab to enforce a clear hierarchical structure, without removing valuable functionality.

Context:
The current Analysis tab contains useful information (model output, uncertainty, history, fleet context, and technical metadata), but it is poorly structured and mixes multiple levels of interpretation.

Goal:
Reorganize the Analysis tab into a layered interpretability structure, improving clarity while preserving all meaningful analytical content.

---

Target hierarchy:

1. Model Explanation (always visible)
Purpose: explain the current prediction and risk.

Include:
- Predicted RUL (reference)
- RUL interval (confidence band, clearly visualized)
- Risk Score (visible and explained)
- Short natural-language explanation linking RUL, uncertainty, and risk

Remove from this layer:
- Band Width (redundant)
- raw technical metadata

---

2. Temporal Behavior (always visible)
Purpose: show how the prediction behaves over time.

Include:
- Predicted RUL vs cycle (selected unit)
- Optional uncertainty over time if available
- Clear interpretation (stable / degrading / unstable)

Keep existing logic for full unit history, but improve readability.

---

3. Fleet Context (visible only when dataset/CSV is available)
Purpose: contextualize the unit within the fleet.

Include:
- Top-N highest-risk units
- Risk distribution across fleet
- Fleet snapshot table (simplified)
- Highlight current unit position if possible

Ensure:
- charts are meaningful (avoid misleading labels like “critical” when all are healthy)

---

4. Technical Diagnostics (on-demand / collapsible sections)
Move the following into expandable sections:
- Decision Breakdown
- Feature Boundary
- Model Context (offline metrics)
- Traceability (schema, scaler, versions)
- Full per-cycle detailed table

These should not clutter the main Analysis view.

---

5. Cleanup and consistency

- Remove redundant elements:
  - Band Width
  - duplicated fields already shown in Summary
- Remove opaque labels like P1/P2/P3
- Clearly separate:
  - model output
  - uncertainty
  - risk logic
  - historical behavior
  - fleet context

- Ensure Analysis complements Summary:
  - Summary = decision layer
  - Analysis = explanation + validation

---

Requirements:
- Do not remove existing computations unless they are redundant
- Prioritize interpretability over raw technical exposure
- Preserve all useful data, but reorganize it into the hierarchy above

---

Output:
1. Explain the refactoring plan
2. Show how each existing section is reassigned to the new structure
3. Implement the changes

### Scenarios

Refactor the Scenarios tab to follow a non-central LLM architecture.

Core principle:
The LLM must NOT be the source of truth or the core decision logic.
The LLM may assist with interpreting user intent and improving explanation text, but all scenario execution, validation, prediction, risk computation, and comparison must remain deterministic and auditable.

Target design:

1. User-driven scenario authoring
- Add a scenario input area (e.g. “Describe scenario (what-if)”).
- The user must be able to describe intended changes in either:
  - natural / semi-natural language
  - explicit deterministic syntax

Examples of supported inputs:
- “increase cycle by 25”
- “decrease sensor_3 by 0.1”
- “set op_setting_1 to 0.6”
- “cycle +25”
- “sensor_11 -0.1”
- “op_setting_2 = 0.3”
- “apply high load profile”

2. Two parsing modes with the same downstream pipeline

A. Deterministic parser (mandatory, built-in)
- Must always exist and work without any LLM
- Must support common practical instructions, not only rigid symbolic syntax
- At minimum support:
  - “increase X by Y”
  - “decrease X by Y”
  - “set X to Y”
  - “X +Y”
  - “X -Y”
  - “X = Y”
  - simple presets such as “apply high load profile”

B. LLM-assisted parser (optional)
- If LLM is available, it may assist with interpreting more flexible natural-language inputs
- It must output the same structured change representation as the deterministic parser
- Its output must always pass through the same deterministic validation layer
- The LLM may also improve explanation wording, but must not control final scenario values directly

3. Parsing strategy
Implement parsing so that:
- deterministic parsing is attempted first for supported instruction patterns
- if deterministic parsing fails and LLM is available, use LLM-assisted parsing
- if neither succeeds, return a clear structured parsing error

In all cases, produce the same internal representation, for example:
{
  "changes": [
    {"field": "cycle", "op": "add", "value": 25},
    {"field": "sensor_3", "op": "add", "value": -0.1},
    {"field": "op_setting_1", "op": "set", "value": 0.6}
  ]
}

4. Deterministic core pipeline (source of truth)
Refactor the flow into explicit stages:
- parse_intent(...)
- build_scenario_payload(...)
- validate_scenario(...)
- run_baseline_prediction(...)
- run_scenario_prediction(...)
- compare_baseline_vs_scenario(...)
- generate_interpretation(...)

The deterministic core must compute:
- baseline_rul
- scenario_rul
- delta_rul
- baseline_risk_score
- scenario_risk_score
- delta_risk_score
- baseline_risk_level
- scenario_risk_level

5. Preserve auditability
Always produce:
- proposed_payload
- change_summary
- assumptions
- safety_notes
- comparison
- comparison_interpretation
- operator_guidance
- assistant_mode (`rules_only` or `llm_enabled`)
- llm_model_used
- service_status

Also show:
- original user input
- parsed structured changes
- previous vs new values for changed fields
- parsing_status

6. UI transparency
Make the parser/assistant status explicit in the Scenarios tab.

Show:
- assistant_mode: `rules_only` or `llm_enabled`
- llm_available: true/false
- llm_used: true/false
- llm_model: model name or `none`
- parsing_mode: `deterministic` or `llm-assisted`
- parsing_status: success / failed

The user must always know whether the system used deterministic parsing only or LLM-assisted parsing.

7. UI behavior
Refactor the tab to follow this order:
- scenario input
- assistant/parsing status
- run scenario button
- parsed changes
- change summary
- assumptions
- safety notes
- baseline vs scenario comparison (RUL and Risk Score)
- delta metrics (ΔRUL, ΔRisk Score)
- expandable JSON / audit details

8. Fallback behavior
Do NOT use a fixed hardcoded scenario as the primary fallback.
Fallback must still be user-driven:
- deterministic parsing of user instructions
- deterministic validation
- deterministic execution

A fixed template may exist only as an optional demo/default example, not as the real scenario engine.

9. Interpretability
Make the output clearly explain:
- what changed
- why those changes were applied
- how they affected predicted RUL
- how they affected Risk Score and risk level

10. Safety and validation
Add deterministic validation for:
- allowed fields
- valid operations
- numeric bounds
- protected identifiers (e.g. dataset_id / unit_id if policy says they are locked)

If parsing fails or the scenario is invalid, return a clear validation message explaining why.

Output required:
1. Explain how the new non-central-LLM architecture works
2. Map current components to the refactored pipeline
3. Define the supported deterministic instruction patterns
4. Explain how LLM-assisted parsing is integrated without becoming central
5. Implement the refactor

## README

Generate three files for this project:

1. README.md
- Technical overview of the PHM app
- Architecture (Predictive → Agent → Dashboard)
- Models used and champion selection
- How to run the project and launch the dashboard

2. USER_GUIDE.md
- How to use the dashboard (Manual vs CSV)
- Explanation of Summary, Analysis, Scenarios, Technical Audit tabs
- Meaning of RUL, Risk Level, Risk Score, and recommendations

3. environment.yml
- Conda environment named `cmapss`
- Include all required dependencies to run the project

Output the three files clearly separated.

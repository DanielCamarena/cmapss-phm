# Base Guide - CMAPSS PHM App Replication

## 1) Project statement

This project develops a functional AI application for predictive maintenance of turbofan engines using the NASA C-MAPSS benchmark.

The app is organized in three layers:
- `predictive_layer` (Layer 1 / capa1): RUL prediction.
- `agent_layer` (Layer 2 / capa2): risk logic, recommendations, and scenario assistant.
- `dashboard_layer` (Layer 3 / capa3): final user-facing dashboard.

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


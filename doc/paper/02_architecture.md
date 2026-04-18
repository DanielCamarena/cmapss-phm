# System Architecture

## 1. Layered architecture

The system is implemented as a three-layer PHM stack:

1. `Predictive Layer`
2. `Agent Layer`
3. `Dashboard Layer`

The architecture is deliberately modular so that prediction, decision logic, and user interaction can be evaluated independently while still forming one coherent deployed system.

## 2. Predictive Layer

Primary responsibilities:
- load the selected predictive feature schema
- apply the stored preprocessing artifacts
- run the deployed champion model
- attach a calibrated confidence band
- expose model version and trace metadata

Core implementation:
- [src/predictive_layer/inference_service.py](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/predictive_layer/inference_service.py:1>)
- [src/predictive_layer/config.py](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/predictive_layer/config.py:1>)

Runtime outputs include:
- `rul_pred`
- `confidence_band`
- `target_policy`
- `model_version`
- `service_status`
- `trace`
- `timestamp`

## 3. Agent Layer

Primary responsibilities:
- validate decision requests
- call the predictive layer through a controlled boundary
- compute deterministic risk and recommendations
- execute deterministic what-if scenarios
- preserve auditability and trace consistency

Core implementation:
- [src/agent_layer/orchestrator.py](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/agent_layer/orchestrator.py:1>)
- [src/agent_layer/tools.py](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/agent_layer/tools.py:1>)
- [src/agent_layer/risk_engine.py](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/agent_layer/risk_engine.py:1>)
- [src/agent_layer/recommender.py](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/agent_layer/recommender.py:1>)

The agent layer is the source of:
- `risk_level`
- `risk_score`
- `recommendation_text`
- recommendation alternatives
- scenario comparison artifacts
- audit log entries

## 4. Dashboard Layer

Primary responsibilities:
- collect inputs from manual mode or CSV-upload mode
- call the agent layer through the backend adapter
- render operator-facing and technical views
- surface service states and audit metadata

Core implementation:
- [src/dashboard_layer/app.py](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/dashboard_layer/app.py:1>)
- [src/dashboard_layer/backend_adapter.py](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/dashboard_layer/backend_adapter.py:1>)
- [src/dashboard_layer/components.py](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/dashboard_layer/components.py:1>)

The four runtime tabs are:
- `Summary`
- `Analysis`
- `Scenarios`
- `Technical Audit`

## 5. Contract boundaries

The layers communicate through explicit structured contracts frozen in the generated artifacts.

Representative contract sources:
- [out/predictive_layer/06_output_schema_v1.json](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/predictive_layer/06_output_schema_v1.json:1>)
- [out/agent_layer/01_output_contract_v1.json](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/agent_layer/01_output_contract_v1.json:1>)
- [out/dashboard_layer/01_ui_backend_contract_v1.json](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/dashboard_layer/01_ui_backend_contract_v1.json:1>)

The dashboard sends the full raw engine record, but the predictive boundary trims it to the selected feature subset. This is implemented in [src/agent_layer/tools.py](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/src/agent_layer/tools.py:1>).

## 6. Service states and reliability

The current application explicitly models service states:
- `ok`
- `fallback`
- `degraded`
- `error_validacion`
- `sin_datos`

These states are surfaced in the dashboard and preserved in agent responses and audit logs. This allows the system to remain informative even when a primary path is unavailable or a request is invalid.

## 7. Traceability and auditability

Traceability is implemented across layers through:
- model-version identifiers
- preprocessing version tags
- fallback-model references
- audit record IDs
- timestamped responses
- JSONL audit logs

Relevant artifacts:
- [out/agent_layer/audit_log.jsonl](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/agent_layer/audit_log.jsonl:1>)
- [out/dashboard_layer/contracts_snapshot.json](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/dashboard_layer/contracts_snapshot.json:1>)
- [out/dashboard_layer/contract_integration_checklist.txt](<C:/Users/quant/Dropbox/Math4ML/BEIHANG/cmapss_phm/out/dashboard_layer/contract_integration_checklist.txt:1>)

The `Technical Audit` tab exposes this traceability directly to users and evaluators, allowing the dashboard demo to function as scientific evidence of reproducible system integration rather than only as a visual interface.

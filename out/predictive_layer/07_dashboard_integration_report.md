# Dashboard Integration Report

- The predictive layer returns a JSON-serializable payload with `rul_pred`, `confidence_band`, `model_version`, `service_status`, `trace`, and `timestamp`.
- The champion is currently a tabular model, which keeps single-record dashboard integration straightforward.
- Fallback behavior is explicit and marked via `service_status=fallback` when needed.

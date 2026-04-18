# Discussion

## 1. Why the tabular champion won

The key discussion point is that the best benchmark scorer was not deployed. The `gru` model achieved the best raw RMSE, but `rf` was selected because the system’s goals extend beyond isolated predictive accuracy.

The deployed application required:
- stable behavior across CMAPSS subsets
- simple and reliable tabular serving
- straightforward deterministic fallback
- low integration complexity

This illustrates a common PHM engineering tradeoff: the model with the lowest benchmark error may not be the best model for a traceable, user-facing decision system.

## 2. Engineering constraints

### Cost
- the LLM is optional and non-central
- scenario execution remains deterministic even when no LLM is available
- this design reduces runtime dependence on paid inference services

### Latency
- the deployed champion is a tabular model
- tabular serving is computationally cheaper than sequence-model serving
- this supports responsive dashboard interactions

### Reliability
- the predictive layer exposes service states
- the system includes a deterministic fallback model
- the dashboard surfaces fallback and degraded states explicitly

### Safety
- risk and recommendations are deterministic
- scenario validation protects key identifiers and allowed fields
- scenario outputs include safety notes
- the Technical Audit tab preserves traceability for debugging and review

## 3. Scenario sensitivity limitations

One recurring observation in the implemented app is that some scenario requests produce minimal changes in RUL and no change in `Risk Score`.

This is not necessarily a scenario-engine failure. In the current system it often arises because:
- some requested edits affect variables not used by the deployed champion model
- some features have low local sensitivity at the selected operating point
- the deterministic risk policy is threshold-based, so small RUL shifts may not change the risk category or score

This is an important discussion point for the paper because it demonstrates that scenario analysis must be interpreted relative to the deployed model’s actual feature usage and sensitivity, not only to domain intuition.

## 4. Traceability as a system contribution

Many PHM studies report prediction performance but stop before the decision and governance layers. This work includes:
- explicit contracts
- audit records
- service-state propagation
- scenario provenance
- dashboard-visible traceability

These engineering elements are not ancillary. They directly support trustworthy deployment and scientific reproducibility.

## 5. Limitations

The current implementation has several limitations that should be stated clearly:
- the deployed predictive champion is a single-row tabular model
- the uncertainty policy is empirical and relatively simple
- scenario presets and deterministic parsing remain limited compared with fully domain-aware maintenance simulators
- evaluation emphasizes local execution and artifact traceability rather than online field deployment

## 6. Future work

Suggested future work:
- stronger local explanation or sensitivity analysis
- richer fleet-level and temporal scenario analytics
- broader scenario grammars and preset libraries
- additional evaluation on deployment realism, online latency, and operational adoption

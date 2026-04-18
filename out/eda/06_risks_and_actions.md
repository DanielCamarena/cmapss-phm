# Risks And Actions

- Risk: multi-condition subsets may require condition-aware normalization.
Action: compare per-dataset and per-regime performance in Plan 2 and Plan 3.
- Risk: low-variance sensors may still be useful in interaction with other channels.
Action: treat removal as a baseline choice, not a hard exclusion for all future models.
- Risk: capped targets can improve optimization while hiding early-life resolution.
Action: keep uncapped raw RUL available for ablation and calibration checks.
- Risk: unit-based splitting by sorted IDs is deterministic but not stratified by lifetime.
Action: revisit with grouped cross-validation during model comparison.
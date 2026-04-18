# Baseline Plan

1. Start with tabular baselines on processed row-level artifacts.
2. Use the documented capped-RUL policy with cap=125 as the default supervised target.
3. Compare against uncapped RUL before freezing the modeling choice.
4. Add sequence windows in Plan 2 or Plan 3 using the documented 30/50-cycle candidates.
5. Track performance separately for FD001/FD003 versus FD002/FD004 because operating conditions differ.

## Recommended next handoff
- Research phase should justify target capping and metric choices.
- Predictive-layer implementation should preserve dataset_id, unit_id, and cycle through inference traces.
- Any future feature pruning should be benchmarked against the full retained baseline set.
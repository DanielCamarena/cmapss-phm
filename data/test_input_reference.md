# `test_input.csv` Scenario Reference

This file defines four physically consistent CMAPSS-style engine snapshots using only the raw dashboard input schema:

- `dataset_id`
- `unit_id`
- `cycle`
- `op_setting_1..3`
- `sensor_1..21`

No RUL field is included. The scenarios are driven by operating settings and sensor values only.

## Scenario Map

### `unit_id = 1` - Nominal / low degradation
- Intended condition: stable cruise operation with low compressor stress and high remaining margin.
- Key pattern:
  - lower `sensor_2`, `sensor_3`, `sensor_4`, `sensor_11`, `sensor_17`
  - higher `sensor_7`, `sensor_12`, `sensor_15`, `sensor_20`, `sensor_21`
- Expected qualitative outcome:
  - highest relative RUL of the four
  - lowest relative risk

### `unit_id = 9002` - Early degradation
- Intended condition: mild compressor efficiency loss with small but coherent drift from nominal values.
- Key pattern:
  - modest increase in `sensor_2`, `sensor_3`, `sensor_4`, `sensor_11`
  - slight decrease in `sensor_7`, `sensor_12`, `sensor_15`, `sensor_20`, `sensor_21`
- Expected qualitative outcome:
  - lower RUL than `1`
  - still materially better than `3` and `4`

### `unit_id = 3` - Moderate degradation
- Intended condition: clearer HPC degradation signal, consistent with reduced margin and increased maintenance urgency.
- Key pattern:
  - further increase in `sensor_2`, `sensor_3`, `sensor_4`, `sensor_11`, `sensor_17`
  - further decrease in `sensor_7`, `sensor_12`, `sensor_15`, `sensor_20`, `sensor_21`
- Expected qualitative outcome:
  - lower RUL than `2`
  - elevated risk relative to the first two rows

### `unit_id = 4` - Severe degradation / near-maintenance
- Intended condition: strongest degradation pattern in the set, with stressed compressor signatures and reduced efficiency-related indicators.
- Key pattern:
  - highest `sensor_2`, `sensor_3`, `sensor_4`, `sensor_11`, `sensor_17`
  - lowest `sensor_7`, `sensor_12`, `sensor_15`, `sensor_20`, `sensor_21`
- Expected qualitative outcome:
  - lowest relative RUL of the four
  - highest relative risk

## Intended Ordering

From healthiest to most degraded:

`1 < 2 < 3 < 4`

In terms of severity, this means:

`1` best condition, `4` worst condition.

## Validation Note

These rows were constructed to be physically coherent with the CMAPSS sensor schema and to represent distinct degradation conditions. If the deployed predictor does not separate them clearly, that points to a model or preprocessing issue rather than a problem with the scenario definitions themselves.

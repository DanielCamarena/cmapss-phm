# User Guide

This guide explains how to use the PHM dashboard for single-engine decisions, analysis, scenario comparison, and audit review.

## Launching the dashboard

Activate the conda environment and start Streamlit:

```powershell
conda activate cmapss
streamlit run src/dashboard_layer/app.py
```

## Input modes

The left sidebar is the `Request Console`. The dashboard supports two input modes.

### Manual mode

Use this when you want to type or edit a single engine record directly.

Manual mode exposes:
- `dataset_id`
- `unit_id`
- `cycle`
- `op_setting_1..3`
- `sensor_1..21`

This is useful for:
- checking a single observation
- stress-testing specific sensor edits
- starting from a known record and then adjusting values manually

### CSV upload mode

Use this when you already have engine monitoring rows in CSV form.

Workflow:
1. upload a CSV that follows the same schema as `data/sample_input.csv`
2. choose `Selected Uploaded Row`
3. click `Decision` to score that record

You can also click `Load Selected Row Into Manual Mode` to copy that row into the editable manual form without losing the uploaded CSV.

CSV mode also enables fleet-level views in the `Analysis` tab because the dashboard can compare the selected unit against other rows in the uploaded dataset.

## What the main tabs mean

## Summary

`Summary` is the decision layer.

It answers:
- how much useful life is left
- what the condition status is
- how urgent action is
- whether recent same-unit behavior looks stable or degrading

Main outputs:
- `Predicted RUL`
- `Risk Level`
- `Urgency`
- `Immediate Action`
- `Recent RUL Evolution`

Use this tab when you want the fastest operator-facing answer.

## Analysis

`Analysis` is the explanation and validation layer.

It expands the decision into:
- model explanation
- uncertainty / confidence interval
- temporal behavior across cycles
- fleet context when a dataset is available
- technical diagnostics in expandable sections

Use this tab when you want to understand:
- why the current prediction looks the way it does
- how certain it is
- how the selected unit compares to the fleet

## Scenarios

`Scenarios` is the what-if comparison layer.

It lets you describe a hypothetical change, such as:
- `increase cycle by 25`
- `set op_setting_1 to 0.6`
- `decrease sensor_11 by 0.1`
- `apply high load profile`

The tab shows:
- parsing transparency
- parsed changes
- change summary
- assumptions
- safety notes
- baseline vs scenario comparison
- `ΔRUL`
- `ΔRisk Score`

Important:
- scenario execution is deterministic
- if an LLM is available, it may help interpret natural-language intent
- prediction, risk, and comparison remain deterministic and auditable

## Technical Audit

`Technical Audit` is the traceability layer.

It includes:
- audit record metadata
- model version
- trace payload
- contract snapshots
- recent agent audit entries
- full scenario JSON when applicable

Use this tab for debugging, trace review, or technical validation.

## Meaning of the main metrics

## RUL

`RUL` means `Remaining Useful Life`.

It is the predicted number of cycles remaining before failure, according to the deployed predictive model.

Higher RUL generally means:
- more remaining life
- lower urgency

Lower RUL generally means:
- less remaining life
- higher maintenance concern

## Risk Level

`Risk Level` is the main condition label returned by deterministic risk rules.

Possible values:
- `healthy`
- `warning`
- `critical`
- `unknown`

It is derived from:
- predicted RUL
- confidence-band width
- predictive service state such as `fallback` or `degraded`

## Risk Score

`Risk Score` is the numeric severity score used inside the deterministic risk engine.

It is mainly used in:
- `Analysis`
- `Scenarios`

It is not meant to replace `Risk Level`; instead, it supports it.

Interpretation:
- lower score -> lower concern
- higher score -> higher concern

The score can increase because of:
- lower predicted RUL
- wider confidence interval
- fallback or degraded upstream service

## Recommendations

Recommendations are deterministic action texts mapped from the current risk state.

Examples:
- continue operation under normal monitoring
- plan maintenance soon
- schedule immediate inspection and maintenance action

The dashboard also expresses urgency in plain language so operators do not need to interpret internal priority codes.

## Scenario results

Scenario results compare:
- baseline prediction
- scenario prediction after the requested edits

You will see:
- what changed
- the scenario payload actually executed
- how RUL changed
- how Risk Score changed
- whether the risk level changed

If a scenario request is invalid, the tab returns a validation error instead of silently guessing.

## Notes and limitations

- The deployed predictive model currently uses only a selected feature subset, not every raw field shown in the dashboard.
- Some scenario changes may have little effect if they target:
  - fields not used by the deployed model
  - features with low local sensitivity at the selected operating point
- `cycle` is tracked in the request and scenario system, but it is not currently a predictive feature for the deployed `rf` champion model.

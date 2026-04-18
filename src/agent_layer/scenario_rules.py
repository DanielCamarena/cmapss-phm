from __future__ import annotations

import re
from copy import deepcopy


ALLOWED_FIELDS = {
    "cycle",
    *[f"op_setting_{idx}" for idx in range(1, 4)],
    *[f"sensor_{idx}" for idx in range(1, 22)],
}
PROTECTED_FIELDS = {"dataset_id", "unit_id"}
ALLOWED_OPERATIONS = {"set", "add"}
FIELD_BOUNDS = {
    "cycle": (1.0, 10000.0),
    "default": (-1_000_000.0, 1_000_000.0),
}
DEFAULT_SCENARIO_PROMPT = "cycle +25; op_setting_1 = 0.6; sensor_11 -0.1"
SCENARIO_PRESETS = {
    "apply high load profile": [
        {"field": "op_setting_1", "op": "add", "value": 0.2, "source_text": "apply high load profile"},
        {"field": "op_setting_2", "op": "add", "value": 0.1, "source_text": "apply high load profile"},
        {"field": "sensor_11", "op": "add", "value": -0.1, "source_text": "apply high load profile"},
        {"field": "sensor_12", "op": "add", "value": -0.1, "source_text": "apply high load profile"},
    ],
}


def _parse_numeric(value: str) -> float:
    return float(value.strip())


def _normalize_field(field: str) -> str:
    return field.strip().lower()


def _build_change_record(field: str, operation: str, value: float, source_text: str) -> dict:
    return {
        "field": field,
        "op": operation,
        "value": float(value),
        "source_text": source_text.strip(),
    }


def _deterministic_parse_statement(statement: str) -> dict | None:
    text = statement.strip()
    if not text:
        return None

    preset_key = text.lower()
    if preset_key in SCENARIO_PRESETS:
        return {"preset": preset_key, "changes": SCENARIO_PRESETS[preset_key]}

    patterns = [
        (r"^(cycle|op_setting_\d+|sensor_\d+)\s*=\s*(-?\d+(?:\.\d+)?)$", "set"),
        (r"^(cycle|op_setting_\d+|sensor_\d+)\s*([+-])\s*(\d+(?:\.\d+)?)$", "delta"),
        (r"^increase\s+(cycle|op_setting_\d+|sensor_\d+)\s+by\s+(\d+(?:\.\d+)?)$", "increase"),
        (r"^decrease\s+(cycle|op_setting_\d+|sensor_\d+)\s+by\s+(\d+(?:\.\d+)?)$", "decrease"),
        (r"^set\s+(cycle|op_setting_\d+|sensor_\d+)\s+to\s+(-?\d+(?:\.\d+)?)$", "set_to"),
    ]
    for pattern, mode in patterns:
        match = re.match(pattern, text, flags=re.IGNORECASE)
        if not match:
            continue
        field = _normalize_field(match.group(1))
        if mode == "set":
            return _build_change_record(field, "set", _parse_numeric(match.group(2)), text)
        if mode == "set_to":
            return _build_change_record(field, "set", _parse_numeric(match.group(2)), text)
        if mode == "increase":
            return _build_change_record(field, "add", _parse_numeric(match.group(2)), text)
        if mode == "decrease":
            return _build_change_record(field, "add", -_parse_numeric(match.group(2)), text)
        sign = match.group(2)
        magnitude = _parse_numeric(match.group(3))
        return _build_change_record(field, "add", magnitude if sign == "+" else -magnitude, text)
    return None


def parse_intent_deterministically(intent_text: str) -> tuple[list[dict], list[str]]:
    raw_statements = re.split(r"[;\n,]+", intent_text)
    changes: list[dict] = []
    errors: list[str] = []
    for statement in raw_statements:
        if not statement.strip():
            continue
        parsed = _deterministic_parse_statement(statement)
        if parsed is None:
            errors.append(
                f"Could not parse `{statement.strip()}`. Use forms like `increase cycle by 25`, "
                "`decrease sensor_3 by 0.1`, `set op_setting_1 to 0.6`, `sensor_11 -0.1`, or `apply high load profile`."
            )
            continue
        if "changes" in parsed:
            changes.extend(parsed["changes"])
        else:
            changes.append(parsed)
    return changes, errors


def validate_scenario(base_payload: dict, structured_changes: list[dict]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    for change in structured_changes:
        field = change["field"]
        operation = change.get("op") or change.get("operation")
        value = float(change["value"])

        if field in PROTECTED_FIELDS:
            errors.append(f"`{field}` is protected and cannot be modified by scenario policy.")
            continue
        if field not in ALLOWED_FIELDS:
            errors.append(f"`{field}` is not an allowed scenario field.")
            continue
        if operation not in ALLOWED_OPERATIONS:
            errors.append(f"`{operation}` is not a supported operation for `{field}`.")
            continue

        if field == "cycle":
            current_value = float(base_payload["cycle"])
        elif field.startswith("op_setting_"):
            if field not in base_payload.get("op_settings", {}):
                errors.append(f"`{field}` is not present in the current request payload.")
                continue
            current_value = float(base_payload["op_settings"][field])
        else:
            if field not in base_payload.get("sensors", {}):
                errors.append(f"`{field}` is not present in the current request payload.")
                continue
            current_value = float(base_payload["sensors"][field])

        proposed_value = value if operation == "set" else current_value + value
        lower, upper = FIELD_BOUNDS.get(field, FIELD_BOUNDS["default"])
        if proposed_value < lower or proposed_value > upper:
            errors.append(f"`{field}` would become {proposed_value:.4f}, outside the allowed range [{lower}, {upper}].")

    return len(errors) == 0, errors


def build_scenario_payload(base_payload: dict, structured_changes: list[dict]) -> tuple[dict, list[str], list[str], list[str]]:
    proposed = deepcopy(base_payload)
    change_summary: list[str] = []
    assumptions: list[str] = []
    safety_notes: list[str] = []

    for change in structured_changes:
        field = change["field"]
        operation = change.get("op") or change.get("operation")
        delta_or_value = float(change["value"])

        if field == "cycle":
            current_value = float(proposed["cycle"])
            proposed_value = delta_or_value if operation == "set" else current_value + delta_or_value
            proposed["cycle"] = int(round(proposed_value))
            verb = "set" if operation == "set" else "shifted"
            change_summary.append(f"`cycle` {verb} from {int(current_value)} to {int(round(proposed_value))}.")
            assumptions.append("Cycle changes are interpreted as operating-time shifts while dataset_id and unit_id remain locked.")
            continue

        bucket_name = "op_settings" if field.startswith("op_setting_") else "sensors"
        current_value = float(proposed[bucket_name][field])
        proposed_value = delta_or_value if operation == "set" else current_value + delta_or_value
        proposed[bucket_name][field] = round(proposed_value, 4)
        if operation == "set":
            change_summary.append(f"`{field}` set from {current_value:.4f} to {proposed_value:.4f}.")
        else:
            change_summary.append(
                f"`{field}` shifted by {delta_or_value:+.4f}, from {current_value:.4f} to {proposed_value:.4f}."
            )

        if field.startswith("op_setting_"):
            assumptions.append("Operating-setting edits assume the requested shift remains within a plausible operating envelope.")
        else:
            assumptions.append("Sensor edits are treated as what-if perturbations for comparative sensitivity analysis only.")

    assumptions = list(dict.fromkeys(assumptions))
    safety_notes.extend(
        [
            "Scenario execution is deterministic and auditable; the LLM never controls prediction or risk computation.",
            "Protected identifiers (`dataset_id`, `unit_id`) remain locked to the active request.",
            "Scenario outputs support comparative analysis and do not replace engineering review or physical inspection.",
        ]
    )
    proposed["source"] = "dashboard.scenario"
    return proposed, change_summary, assumptions, safety_notes

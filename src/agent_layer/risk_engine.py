from __future__ import annotations


def compute_risk(rul_pred: float | None, confidence_band: dict | None, upstream_status: str, thresholds: dict) -> dict:
    if rul_pred is None:
        return {
            "risk_level": "unknown",
            "risk_score": None,
            "rationale": "No valid RUL prediction was available, so risk could not be computed deterministically.",
        }

    if rul_pred <= thresholds["critical_max"]:
        base_level = "critical"
        base_score = 90
    elif rul_pred <= thresholds["warning_max"]:
        base_level = "warning"
        base_score = 60
    else:
        base_level = "healthy"
        base_score = 25

    spread = None
    if confidence_band and confidence_band.get("lower") is not None and confidence_band.get("upper") is not None:
        spread = float(confidence_band["upper"]) - float(confidence_band["lower"])
        if spread >= 40:
            base_score += 10
        elif spread >= 20:
            base_score += 5

    if upstream_status == "fallback":
        base_score += 5
    elif upstream_status == "degraded":
        base_score += 10

    base_score = max(0, min(100, base_score))
    rationale_parts = [f"RUL prediction is {rul_pred:.2f} cycles, which maps to `{base_level}` under the frozen threshold policy."]
    if spread is not None:
        rationale_parts.append(f"Confidence-band width is {spread:.2f} cycles and contributes to the final risk score.")
    if upstream_status in {"fallback", "degraded"}:
        rationale_parts.append(f"Upstream predictive status is `{upstream_status}`, so the score is conservatively adjusted.")
    return {
        "risk_level": base_level,
        "risk_score": base_score,
        "rationale": " ".join(rationale_parts),
    }

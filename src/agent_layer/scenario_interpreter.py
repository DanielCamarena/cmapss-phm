from __future__ import annotations

from .llm_client import enrich_scenario_text


def compare_baseline_vs_scenario(baseline: dict, scenario: dict) -> dict:
    base_rul = baseline.get("rul_pred")
    scenario_rul = scenario.get("rul_pred")
    base_risk_score = baseline.get("risk_score")
    scenario_risk_score = scenario.get("risk_score")

    delta_rul = None
    if base_rul is not None and scenario_rul is not None:
        delta_rul = round(float(scenario_rul) - float(base_rul), 3)

    delta_risk_score = None
    if base_risk_score is not None and scenario_risk_score is not None:
        delta_risk_score = round(float(scenario_risk_score) - float(base_risk_score), 3)

    return {
        "baseline_rul": base_rul,
        "scenario_rul": scenario_rul,
        "delta_rul": delta_rul,
        "baseline_risk_score": base_risk_score,
        "scenario_risk_score": scenario_risk_score,
        "delta_risk_score": delta_risk_score,
        "baseline_risk_level": baseline.get("risk_level"),
        "scenario_risk_level": scenario.get("risk_level"),
    }


def generate_interpretation(change_summary: list[str], comparison: dict) -> dict:
    delta_rul = comparison.get("delta_rul")
    delta_risk_score = comparison.get("delta_risk_score")
    scenario_risk_level = comparison.get("scenario_risk_level")
    if delta_rul is None:
        comparison_interpretation = "Scenario execution could not compute a valid RUL delta for the requested changes."
    else:
        rul_direction = "increased" if delta_rul > 0 else ("decreased" if delta_rul < 0 else "did not materially change")
        if delta_risk_score is None:
            risk_text = "Risk-score change is unavailable."
        elif delta_risk_score > 0:
            risk_text = f"Risk Score increased by {delta_risk_score:.2f}."
        elif delta_risk_score < 0:
            risk_text = f"Risk Score decreased by {abs(delta_risk_score):.2f}."
        else:
            risk_text = "Risk Score did not materially change."
        comparison_interpretation = (
            f"The requested scenario {rul_direction} predicted RUL by {abs(delta_rul):.2f} cycles. "
            f"{risk_text} The resulting scenario risk level is `{scenario_risk_level}`."
        )

    operator_guidance = (
        "Use the scenario result to compare sensitivity before changing maintenance action. "
        "Re-run with narrower edits if the current scenario is too broad."
    )
    if change_summary:
        operator_guidance += f" Applied changes: {' '.join(change_summary[:2])}"
    return {
        "comparison_interpretation": comparison_interpretation,
        "operator_guidance": operator_guidance,
    }


def optionally_enrich_explanation(interpretation_payload: dict, model_name: str) -> tuple[dict, str | None]:
    prompt = (
        "Rewrite the following scenario explanation for an operator. Preserve all numeric deltas and risk labels.\n\n"
        f"Interpretation: {interpretation_payload['comparison_interpretation']}\n"
        f"Guidance: {interpretation_payload['operator_guidance']}"
    )
    text, used_model = enrich_scenario_text(prompt, model_name)
    if text:
        interpretation_payload["comparison_interpretation"] = text.strip()
    return interpretation_payload, used_model

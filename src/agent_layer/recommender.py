from __future__ import annotations


RECOMMENDATION_CATALOG = {
    "critical": {
        "recommendation_text": "Schedule immediate inspection and maintenance action before additional cycles are consumed.",
        "recommendation_priority": "P1",
        "recommendation_alternatives": [
            "Remove the unit from normal operation until inspection is completed.",
            "Review recent sensor history and confirm whether the degradation pattern is accelerating.",
        ],
    },
    "warning": {
        "recommendation_text": "Plan maintenance in the near term and increase monitoring frequency for this unit.",
        "recommendation_priority": "P2",
        "recommendation_alternatives": [
            "Prioritize the unit in the next maintenance window.",
            "Run what-if scenarios to test sensitivity to operating-condition changes.",
        ],
    },
    "healthy": {
        "recommendation_text": "Continue operation under normal monitoring while keeping the unit in the routine review queue.",
        "recommendation_priority": "P3",
        "recommendation_alternatives": [
            "Track trend changes rather than scheduling immediate intervention.",
            "Use periodic scenario checks to detect sensitivity to operating-condition shifts.",
        ],
    },
    "unknown": {
        "recommendation_text": "Do not act on this request until the predictive input contract is satisfied and a valid forecast is available.",
        "recommendation_priority": "P1",
        "recommendation_alternatives": [
            "Validate the request payload and retry prediction.",
            "Inspect upstream service logs for validation or availability issues.",
        ],
    },
}


def build_recommendation(risk_level: str, upstream_status: str) -> dict:
    record = RECOMMENDATION_CATALOG[risk_level].copy()
    safety_notes: list[str] = []
    if upstream_status == "fallback":
        safety_notes.append("Recommendation is based on predictive fallback mode rather than the primary champion.")
    if upstream_status == "degraded":
        safety_notes.append("Recommendation should be treated cautiously because the predictive layer reported degraded service.")
    record["safety_notes"] = safety_notes
    return record

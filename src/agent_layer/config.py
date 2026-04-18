from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class AgentSettings:
    root: Path
    out_dir: Path
    dashboard_out_dir: Path
    predictive_contract: dict
    predictive_examples: dict
    fallback_policy_text: str
    predictive_schema: dict
    risk_thresholds: dict
    llm_model: str | None


def load_settings() -> AgentSettings:
    root = Path(__file__).resolve().parents[2]
    predictive_examples = json.loads((root / "out" / "predictive_layer" / "06_contract_examples.json").read_text(encoding="utf-8"))
    predictive_schema = json.loads((root / "out" / "predictive_layer" / "06_output_schema_v1.json").read_text(encoding="utf-8"))
    return AgentSettings(
        root=root,
        out_dir=root / "out" / "agent_layer",
        dashboard_out_dir=root / "out" / "dashboard_layer",
        predictive_contract=json.loads((root / "out" / "predictive_layer" / "champion_record.json").read_text(encoding="utf-8")),
        predictive_examples=predictive_examples,
        fallback_policy_text=(root / "out" / "predictive_layer" / "05_fallback_policy.txt").read_text(encoding="utf-8"),
        predictive_schema=predictive_schema,
        risk_thresholds={"critical_max": 20, "warning_max": 60},
        llm_model=os.getenv("GEMINI_MODEL") or "gemini-2.5-flash",
    )


def settings_as_dict(settings: AgentSettings) -> dict:
    data = asdict(settings)
    for key in ["root", "out_dir", "dashboard_out_dir"]:
        data[key] = str(data[key])
    return data

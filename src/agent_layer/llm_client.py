from __future__ import annotations

import json
import os
import re


def llm_available() -> bool:
    return bool(os.getenv("GEMINI_API_KEY"))


def enrich_scenario_text(prompt: str, model_name: str) -> tuple[str | None, str | None]:
    if not llm_available():
        return None, None
    try:
        from google import genai

        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        response = client.models.generate_content(model=model_name, contents=prompt)
        text = getattr(response, "text", None)
        return text, model_name
    except Exception:
        return None, None


def _extract_json_block(text: str) -> str | None:
    stripped = text.strip()
    if not stripped:
        return None

    fenced_match = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", stripped, flags=re.DOTALL | re.IGNORECASE)
    if fenced_match:
        return fenced_match.group(1).strip()

    object_match = re.search(r"(\{.*\})", stripped, flags=re.DOTALL)
    if object_match:
        return object_match.group(1).strip()

    array_match = re.search(r"(\[.*\])", stripped, flags=re.DOTALL)
    if array_match:
        return array_match.group(1).strip()

    return None


def parse_scenario_intent(prompt: str, model_name: str) -> tuple[list[dict] | None, str | None]:
    if not llm_available():
        return None, None
    try:
        from google import genai

        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        response = client.models.generate_content(
            model=model_name,
            contents=(
                "Convert the user's scenario request into JSON with this exact structure:\n"
                '{"changes":[{"field":"cycle","op":"add","value":25}]}\n'
                "Allowed fields: cycle, op_setting_1..3, sensor_1..21. "
                "Allowed operations: set, add. "
                "Interpret presets explicitly. Example:\n"
                'Input: "Increase cycle by 25 and apply high load profile"\n'
                'Output: {"changes":[{"field":"cycle","op":"add","value":25},{"field":"op_setting_1","op":"add","value":0.2},{"field":"op_setting_2","op":"add","value":0.1},{"field":"sensor_11","op":"add","value":-0.1},{"field":"sensor_12","op":"add","value":-0.1}]}\n'
                "Return JSON only, with no explanation.\n\n"
                f"User scenario: {prompt}"
            ),
        )
        text = getattr(response, "text", None)
        if not text:
            return None, None
        json_block = _extract_json_block(text)
        if not json_block:
            return None, None
        parsed = json.loads(json_block)
        if isinstance(parsed, dict):
            parsed = parsed.get("changes")
        if not isinstance(parsed, list):
            return None, None
        normalized: list[dict] = []
        for item in parsed:
            if not isinstance(item, dict):
                return None, None
            normalized.append(
                {
                    "field": str(item["field"]).strip().lower(),
                    "op": str(item.get("op", item.get("operation"))).strip().lower(),
                    "value": float(item["value"]),
                    "source_text": prompt,
                }
            )
        return normalized, model_name
    except Exception:
        return None, None

"""Prompt templates for alerts, reports, and VLM verification — Blueprint v2.0."""

import json
from pathlib import Path
from typing import Any

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def load_prompt(name: str) -> dict[str, str]:
    path = PROMPTS_DIR / name
    if path.suffix == ".json":
        return json.loads(path.read_text())
    return {"system": path.read_text(), "user_template": ""}


def format_alert_prompt(
    camera_id: str,
    camera_location: str,
    timestamp: str,
    violation_type: str,
    count: int,
    confidence: float,
    risk_level: str,
) -> dict[str, str]:
    tpl = load_prompt("alert_generation.json")
    user = tpl["user_template"].format(
        camera_id=camera_id,
        camera_location=camera_location,
        timestamp=timestamp,
        violation_type=violation_type,
        count=count,
        confidence=confidence,
        risk_level=risk_level,
    )
    return {"system": tpl["system"], "user": user}


def format_vlm_verifier_prompt(
    yolo_class: str,
    confidence: float,
    height_estimate: str = "unknown",
) -> dict[str, str]:
    tpl = load_prompt("vlm_secondary_verifier.json")
    user = tpl["user_template"].format(
        height_estimate=height_estimate,
        yolo_class=yolo_class,
        confidence=round(confidence * 100, 1),
    )
    return {"system": tpl["system"], "user": user}

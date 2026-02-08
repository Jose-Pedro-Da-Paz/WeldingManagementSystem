from __future__ import annotations

from typing import Any


def build_finding(rule_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    finding = {
        "severity": payload.get("severity", "INFO"),
        "rule_id": rule_id,
        "field": payload.get("field"),
        "message": payload.get("message", "Rule triggered."),
        "reference": payload.get("reference"),
        "needs_verification": payload.get("needs_verification", True),
    }
    if payload.get("confidence"):
        finding["confidence"] = payload["confidence"]
    return finding

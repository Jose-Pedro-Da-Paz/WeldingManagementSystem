from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None

SCHEMA_PATH = Path(__file__).resolve().parent / "schema" / "rule_pack.schema.json"
REQUIRED_KEYS = {"standard", "part", "version", "scope", "metadata", "definitions", "variables", "rules", "ranges", "tests", "validations"}


class RuleSchemaError(ValueError):
    pass


def load_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _fallback_validate(rule_pack: dict[str, Any]) -> None:
    missing = REQUIRED_KEYS - set(rule_pack.keys())
    if missing:
        raise RuleSchemaError(f"Rule pack validation failed: missing keys {sorted(missing)}")
    if not isinstance(rule_pack.get("rules"), list):
        raise RuleSchemaError("Rule pack validation failed: rules must be an array")


def validate_rule_pack(rule_pack: dict[str, Any]) -> None:
    if Draft202012Validator is None:
        _fallback_validate(rule_pack)
        return

    validator = Draft202012Validator(load_schema())
    errors = sorted(validator.iter_errors(rule_pack), key=lambda err: err.path)
    if errors:
        details = "; ".join(error.message for error in errors)
        raise RuleSchemaError(f"Rule pack validation failed: {details}")

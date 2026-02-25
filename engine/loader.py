from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from .schema import validate_rule_pack


class RulePackLoader:
    def __init__(self, rules_root: Path | str):
        self.rules_root = Path(rules_root)

    def _read_json(self, path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _merge(self, base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
        merged = deepcopy(base)
        for key in ("variables", "rules", "ranges", "tests", "validations"):
            merged.setdefault(key, [])
            merged[key].extend(incoming.get(key, []))

        merged.setdefault("definitions", {})
        defs = incoming.get("definitions", {})
        for k, v in defs.items():
            if isinstance(v, dict):
                merged["definitions"].setdefault(k, {}).update(v)
            elif isinstance(v, list):
                merged["definitions"].setdefault(k, [])
                merged["definitions"][k].extend(x for x in v if x not in merged["definitions"][k])
            else:
                merged["definitions"][k] = v
        for key in ("standard", "part", "version", "scope", "metadata"):
            if key in incoming:
                merged[key] = incoming[key]
        return merged

    def load(self, relative_rule_path: str) -> dict[str, Any]:
        path = self.rules_root / relative_rule_path
        pack = self._read_json(path)

        aggregate: dict[str, Any] = {
            "standard": pack.get("standard"),
            "part": pack.get("part", ""),
            "version": pack.get("version", ""),
            "scope": pack.get("scope", ""),
            "metadata": pack.get("metadata", {}),
            "definitions": {},
            "variables": [],
            "rules": [],
            "ranges": [],
            "tests": [],
            "validations": [],
        }

        for include in pack.get("includes", []):
            included_pack = self.load(include)
            aggregate = self._merge(aggregate, included_pack)

        aggregate = self._merge(aggregate, pack)

        for override in pack.get("overrides", []):
            aggregate = self._merge(aggregate, override)

        validate_rule_pack(aggregate)
        return aggregate

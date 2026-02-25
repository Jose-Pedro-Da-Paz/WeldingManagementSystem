from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .explanations import build_finding
from .math.functions import FUNCTION_REGISTRY


@dataclass
class EvalContext:
    payload: dict[str, Any]
    previous_payload: dict[str, Any] | None = None

    def get(self, field_path: str) -> Any:
        value: Any = self.payload
        for part in field_path.split("."):
            if not isinstance(value, dict):
                return None
            value = value.get(part)
        return value

    def previous(self, field_path: str) -> Any:
        if not self.previous_payload:
            return None
        value: Any = self.previous_payload
        for part in field_path.split("."):
            if not isinstance(value, dict):
                return None
            value = value.get(part)
        return value


class RuleEvaluator:
    def __init__(self, pack: dict[str, Any], debug: bool = False):
        self.pack = pack
        self.debug = debug

    def _eval_predicate(self, ctx: EvalContext, predicate: dict[str, Any]) -> bool:
        field = predicate.get("field", "")
        op = predicate.get("op")
        expected = predicate.get("value")
        current = ctx.get(field)

        ops = {
            "eq": lambda: current == expected,
            "neq": lambda: current != expected,
            "gt": lambda: current is not None and current > expected,
            "gte": lambda: current is not None and current >= expected,
            "lt": lambda: current is not None and current < expected,
            "lte": lambda: current is not None and current <= expected,
            "in": lambda: current in expected,
            "not_in": lambda: current not in expected,
            "exists": lambda: (current is not None) is bool(expected),
            "not_exists": lambda: (current is None) is bool(expected),
            "changed": lambda: (ctx.previous(field) != current) is bool(expected),
            "regex": lambda: isinstance(current, str) and bool(re.search(expected, current)),
        }
        if op not in ops:
            raise ValueError(f"Unsupported operator: {op}")
        return ops[op]()

    def _evaluate_when(self, ctx: EvalContext, when: dict[str, Any]) -> bool:
        if "all" in when:
            return all(self._eval_predicate(ctx, p) for p in when["all"])
        if "any" in when:
            return any(self._eval_predicate(ctx, p) for p in when["any"])
        if "not" in when:
            return not self._evaluate_when(ctx, when["not"])
        return True

    def _apply_expression(self, expression: str, payload: dict[str, Any]) -> Any:
        match = re.match(r"(?P<func>[A-Z_]+)\((?P<args>.*)\)", expression)
        if not match:
            raise ValueError(f"Invalid expression: {expression}")
        func_name = match.group("func")
        args_raw = [arg.strip() for arg in match.group("args").split(",") if arg.strip()]
        func = FUNCTION_REGISTRY[func_name]

        resolved_args = []
        for arg in args_raw:
            if arg.startswith("inputs.") or arg.startswith("context.") or arg.startswith("computed."):
                value = payload
                for part in arg.split("."):
                    value = value.get(part, None) if isinstance(value, dict) else None
                resolved_args.append(value)
            else:
                resolved_args.append(arg.strip("\"'"))
        return func(*resolved_args)

    def evaluate(self, payload: dict[str, Any], previous_payload: dict[str, Any] | None = None) -> dict[str, Any]:
        ctx = EvalContext(payload=payload, previous_payload=previous_payload)
        findings: list[dict[str, Any]] = []
        required_tests: list[dict[str, Any]] = []
        approval_ranges: list[dict[str, Any]] = []
        computed: dict[str, Any] = {}
        debug_rules: list[str] = []
        invalid = False

        for validation in self.pack.get("validations", []):
            applies = validation.get("applies_to")
            if applies and payload.get("doc_type") not in applies:
                continue
            missing = [field for field in validation.get("require_fields", []) if EvalContext(payload).get(field) is None]
            if missing:
                findings.append({
                    "severity": validation["severity"],
                    "rule_id": validation["id"],
                    "field": ",".join(missing),
                    "message": validation.get("message"),
                    "reference": validation.get("reference"),
                    "needs_verification": validation.get("needs_verification", True),
                })
                if validation["severity"] == "ERROR":
                    invalid = True

        for rule in self.pack.get("rules", []):
            applies = rule.get("applies_to")
            if applies and payload.get("doc_type") not in applies:
                continue
            if self._evaluate_when(ctx, rule.get("when", {})):
                debug_rules.append(rule["id"])
                then = rule.get("then", {})
                if then.get("add_finding"):
                    findings.append(build_finding(rule["id"], then["add_finding"]))
                if then.get("invalidate"):
                    invalid = True

        for test_rule in self.pack.get("tests", []):
            if self._evaluate_when(ctx, test_rule.get("when", {})):
                required_tests.append({
                    "id": test_rule["id"],
                    "tests": test_rule.get("require", []),
                    "reference": test_rule.get("reference"),
                    "needs_verification": test_rule.get("needs_verification", True),
                })

        augmented_payload = {**payload, "computed": computed}
        for range_rule in self.pack.get("ranges", []):
            if self._evaluate_when(ctx, range_rule.get("when", {})):
                result = self._apply_expression(range_rule["compute"]["expression"], augmented_payload)
                out_field = range_rule["compute"]["output_field"]
                if out_field.startswith("computed."):
                    computed[out_field.split(".", 1)[1]] = result
                approval_ranges.append({
                    "id": range_rule["id"],
                    "output_field": out_field,
                    "value": result,
                    "reference": range_rule.get("reference"),
                    "needs_verification": range_rule.get("needs_verification", True),
                })

        severities = {f.get("severity") for f in findings}
        status = "INVALID" if invalid or "ERROR" in severities else "WARNING" if "WARNING" in severities else "VALID"
        output = {
            "status": status,
            "findings": findings,
            "required_tests": required_tests,
            "approval_ranges": approval_ranges,
            "computed": computed,
        }
        if self.debug:
            output["debug"] = {"triggered_rules": debug_rules}
        return output

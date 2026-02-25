from engine.explanations import build_explanations
from engine.loader import load_ruleset


def _evaluate_rule(rule: dict, current: dict, previous: dict) -> dict | None:
    trigger = rule.get("trigger", {})
    variable = trigger.get("variable")

    if trigger.get("change") and previous.get(variable) == current.get(variable):
        return None

    if "equals" in trigger and current.get(variable) != trigger["equals"]:
        return None

    effect = rule.get("effect", {})
    severity = "error" if effect.get("require_new_test") else "warning"

    return {
        "rule_id": rule.get("id"),
        "severity": severity,
        "variable": variable,
        "message": rule.get("message", "Rule triggered"),
        "reference": rule.get("reference"),
    }


def evaluate_rules(standard_slug: str, current: dict, previous: dict | None = None) -> dict:
    previous = previous or {}
    ruleset = load_ruleset(standard_slug)

    triggered = []
    for rule in ruleset.get("rules", []):
        result = _evaluate_rule(rule, current, previous)
        if result:
            triggered.append(result)

    errors = [r for r in triggered if r["severity"] == "error"]
    warnings = [r for r in triggered if r["severity"] == "warning"]

    status = "INVALID" if errors else "WARNING" if warnings else "VALID"
    explanations = build_explanations(triggered)

    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "explanations": explanations,
    }

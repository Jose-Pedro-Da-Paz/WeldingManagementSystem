from pathlib import Path

import pytest

from engine.evaluator import RuleEvaluator
from engine.loader import RulePackLoader
from engine.schema import RuleSchemaError, validate_rule_pack

RULES_ROOT = Path(__file__).resolve().parent.parent / "rules"


def load_pack(path: str) -> dict:
    return RulePackLoader(RULES_ROOT).load(path)


def base_payload(doc_type="PQR"):
    return {
        "doc_type": doc_type,
        "standard": "ISO_15614_1",
        "context": {"product_form": "plate", "pressure_equipment": True},
        "inputs": {
            "process": "135",
            "base_material_group": "1.2",
            "thickness_tested_mm": 12,
            "joint_type": "BW",
            "position": "PA",
            "wps_valid": True,
            "pqr_valid": True,
            "wpq_valid": True,
            "months_since_last_continuity": 2,
            "traceability_matrix": True,
            "welding_coordinator_assigned": True,
        },
        "history": {"previous_versions": []},
    }


def test_schema_valid_pack_loads():
    pack = load_pack("iso_15614_1/rules.json")
    assert pack["standard"] == "ISO_15614"


def test_schema_invalid_pack_raises():
    with pytest.raises(RuleSchemaError):
        validate_rule_pack({"standard": "X"})


def test_rule_changed_operator_invalidates_process_change():
    pack = load_pack("iso_15614_1/rules.json")
    evaluator = RuleEvaluator(pack)
    payload = base_payload()
    prev = base_payload()
    prev["inputs"]["process"] = "141"
    result = evaluator.evaluate(payload, previous_payload=prev)
    assert result["status"] == "INVALID"
    assert any(f["rule_id"] == "iso15614_essential_var_change_process" for f in result["findings"])


def test_required_tests_generated_for_process_135():
    pack = load_pack("iso_15614_1/rules.json")
    result = RuleEvaluator(pack).evaluate(base_payload())
    ids = {t["id"] for t in result["required_tests"]}
    assert "tests_for_process_135" in ids


def test_approval_ranges_computed_thickness():
    pack = load_pack("iso_15614_1/rules.json")
    result = RuleEvaluator(pack).evaluate(base_payload())
    assert "thickness_approved_mm" in result["computed"]


def test_validation_required_fields_missing():
    pack = load_pack("iso_15614_1/rules.json")
    payload = base_payload()
    del payload["inputs"]["base_material_group"]
    result = RuleEvaluator(pack).evaluate(payload)
    assert result["status"] == "INVALID"
    assert any(f["rule_id"] == "required_fields_pqr" for f in result["findings"])


def test_iso9606_continuity_rule_triggers():
    pack = load_pack("iso_9606_1/rules.json")
    payload = base_payload(doc_type="WPQ")
    payload["inputs"]["months_since_last_continuity"] = 8
    result = RuleEvaluator(pack).evaluate(payload)
    assert result["status"] == "INVALID"


def test_iso9606_position_range_generated():
    pack = load_pack("iso_9606_1/rules.json")
    payload = base_payload(doc_type="WPQ")
    result = RuleEvaluator(pack).evaluate(payload)
    assert any(r["id"] == "range_position_approval" for r in result["approval_ranges"])


def test_iso3834_traceability_missing_invalid():
    pack = load_pack("iso_3834/rules.json")
    payload = base_payload(doc_type="quality_dossier")
    payload["inputs"]["traceability_matrix"] = False
    result = RuleEvaluator(pack).evaluate(payload)
    assert result["status"] == "INVALID"


def test_ped_includes_other_packs_and_gating_rule():
    pack = load_pack("ped_2014_68_eu/rules.json")
    payload = base_payload(doc_type="pressure_dossier")
    payload["inputs"]["wps_valid"] = False
    result = RuleEvaluator(pack).evaluate(payload)
    assert any(f["rule_id"] == "ped_requires_valid_qualifications" for f in result["findings"])


def test_debug_output_contains_triggered_rules():
    pack = load_pack("iso_15614_1/rules.json")
    payload = base_payload()
    prev = base_payload()
    prev["inputs"]["process"] = "141"
    result = RuleEvaluator(pack, debug=True).evaluate(payload, previous_payload=prev)
    assert "debug" in result
    assert "iso15614_essential_var_change_process" in result["debug"]["triggered_rules"]


def test_operator_matrix_smoke():
    pack = {
        "standard": "TEST", "part": "1", "version": "1", "scope": "test", "metadata": {"source": "x", "compiled_by": "x", "compiled_at": "x", "coverage_notes": "x", "copyright_notice": "x"},
        "definitions": {}, "variables": [], "ranges": [], "tests": [], "validations": [],
        "rules": [
            {"id": "op_any", "when": {"any": [{"field": "inputs.process", "op": "in", "value": ["135", "141"]}, {"field": "inputs.base_material_group", "op": "regex", "value": "^9"}]}, "then": {"add_finding": {"severity": "WARNING", "field": "inputs.process", "message": "any"}}},
            {"id": "op_not", "when": {"not": {"all": [{"field": "inputs.thickness_tested_mm", "op": "lt", "value": 1}]}}, "then": {"add_finding": {"severity": "INFO", "field": "inputs.thickness_tested_mm", "message": "not"}}},
            {"id": "op_cmp", "when": {"all": [{"field": "inputs.thickness_tested_mm", "op": "gte", "value": 12}, {"field": "inputs.thickness_tested_mm", "op": "lte", "value": 20}, {"field": "inputs.process", "op": "not_in", "value": ["111"]}, {"field": "inputs.optional", "op": "not_exists", "value": True}, {"field": "inputs.process", "op": "neq", "value": "999"}]}, "then": {"add_finding": {"severity": "INFO", "field": "inputs.process", "message": "cmp"}}}
        ]
    }
    payload = base_payload()
    result = RuleEvaluator(pack).evaluate(payload)
    assert len(result["findings"]) == 3

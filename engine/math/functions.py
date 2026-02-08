from __future__ import annotations


def range_thickness(tested: float, product_form: str) -> dict[str, float | str]:
    factor = 2.0 if product_form == "plate" else 1.5
    return {"min": round(tested * 0.5, 3), "max": round(tested * factor, 3), "unit": "mm"}


def range_diameter(diameter: float) -> dict[str, float | str]:
    return {"min": round(diameter * 0.5, 3), "max": round(diameter * 2.0, 3), "unit": "mm"}


def range_position(position: str) -> dict[str, str | list[str]]:
    mapping = {
        "PA": ["PA"],
        "PF": ["PA", "PC", "PF"],
        "HL": ["PA", "PC", "HL"],
    }
    return {"approved": mapping.get(position, [position]), "basis": position}


def needs_requalification(changeset: dict, essential_vars: list[str]) -> bool:
    return any(changeset.get(field, False) for field in essential_vars)


FUNCTION_REGISTRY = {
    "RANGE_THICKNESS": range_thickness,
    "RANGE_DIAMETER": range_diameter,
    "RANGE_POSITION": range_position,
    "NEEDS_REQUALIFICATION": needs_requalification,
}

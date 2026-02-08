import json
from pathlib import Path

RULES_BASE_PATH = Path(__file__).resolve().parent / "rules"


def load_ruleset(standard_slug: str) -> dict:
    rules_path = RULES_BASE_PATH / standard_slug / "rules.json"
    with rules_path.open("r", encoding="utf-8") as file:
        return json.load(file)

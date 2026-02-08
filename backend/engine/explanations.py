def build_explanations(results: list[dict]) -> list[dict]:
    return [
        {
            "rule_id": result["rule_id"],
            "message": result["message"],
            "reference": result.get("reference"),
        }
        for result in results
    ]

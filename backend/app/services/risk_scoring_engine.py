
def score(severity: str, confidence: float, asset_criticality: float) -> dict:
    sev = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}.get(severity, 2)
    value = round(sev * confidence * asset_criticality * 25, 2)
    if value >= 85:
        level = "Critical"
    elif value >= 65:
        level = "High"
    elif value >= 35:
        level = "Medium"
    else:
        level = "Low"
    return {"risk_score": min(100, value), "risk_level": level}

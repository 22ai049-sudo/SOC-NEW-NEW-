
def lookup(indicator: str) -> dict:
    return {"source": "VirusTotal", "indicator": indicator, "malicious": indicator.startswith("203."), "score": 82}

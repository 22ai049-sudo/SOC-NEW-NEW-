
def parse_log(raw_log: str) -> dict:
    lowered = raw_log.lower()
    severity = "Medium"
    if "ransomware" in lowered or "encrypted" in lowered:
        severity = "Critical"
    elif "malware" in lowered or "failed password" in lowered or "brute" in lowered:
        severity = "High"

    return {
        "normalized": raw_log.strip(),
        "severity": severity,
        "indicators": [w for w in ["failed password", "malware", "ransomware", "exfiltration"] if w in lowered],
    }

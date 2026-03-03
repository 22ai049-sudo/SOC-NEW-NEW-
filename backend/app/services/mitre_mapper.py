MITRE_MAP = {
    "failed password": {"tactic": "Credential Access", "technique_id": "T1110.001", "description": "Password Guessing"},
    "malware": {"tactic": "Execution", "technique_id": "T1204.002", "description": "User Execution: Malicious File"},
    "ransomware": {"tactic": "Impact", "technique_id": "T1486", "description": "Data Encrypted for Impact"},
    "exfiltration": {"tactic": "Exfiltration", "technique_id": "T1041", "description": "Exfiltration Over C2 Channel"},
}


def map_mitre(indicators: list[str]) -> list[dict]:
    return [MITRE_MAP[i] for i in indicators if i in MITRE_MAP] or [
        {"tactic": "Discovery", "technique_id": "T1087", "description": "Account Discovery"}
    ]

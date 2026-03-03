
def generate_mitigation(incident: dict) -> dict:
    steps = [
        "Contain affected endpoint",
        "Block malicious IP/hash",
        "Collect forensic snapshot",
        "Recover and validate",
    ]
    return {"incident_id": incident["id"], "steps": steps, "status": "pending_approval"}

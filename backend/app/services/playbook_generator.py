
def generate(incident: dict) -> dict:
    return {
        "incident_id": incident["id"],
        "containment": ["isolate-host", "disable-account"],
        "isolation": ["segment-network"],
        "blocking": ["block-ip"],
        "recovery": ["restore-backup", "patch"],
        "forensics": ["memory-dump", "disk-image"],
    }

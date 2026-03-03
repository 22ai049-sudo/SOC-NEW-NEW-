
def normalize(event: dict) -> dict:
    return {"source": event.get("source", "unknown"), "message": event.get("message", ""), "severity": event.get("severity", "Medium")}

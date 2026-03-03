from app.services.log_parser import parse_log


def detect_threat(raw_log: str) -> dict:
    parsed = parse_log(raw_log)
    classification = "suspicious"
    if parsed["severity"] in {"High", "Critical"}:
        classification = "malicious"
    return {"classification": classification, **parsed, "confidence": 0.91 if classification == "malicious" else 0.65}

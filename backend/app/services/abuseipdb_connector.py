
def lookup(ip: str) -> dict:
    return {"source": "AbuseIPDB", "ip": ip, "abuse_confidence": 76 if ip.startswith("203.") else 10}

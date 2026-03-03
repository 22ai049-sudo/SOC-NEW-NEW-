from app.services import vt_connector, abuseipdb_connector


def enrich(source: str, indicators: list[str]) -> dict:
    vt = [vt_connector.lookup(i) for i in indicators]
    abuse = abuseipdb_connector.lookup(source)
    return {
        "reputation_score": max([v["score"] for v in vt], default=20),
        "malware_detection": any(v["malicious"] for v in vt),
        "cves": ["CVE-2024-0001"],
        "threat_actors": ["TA-demo"],
        "sources": vt + [abuse],
    }

from app.services.rag_knowledge_base import KB


def retrieve_context(indicators: list[str]) -> list[str]:
    refs = [KB["mitre"], KB["playbooks"]]
    if "malware" in indicators or "ransomware" in indicators:
        refs.append(KB["malware"])
    return refs

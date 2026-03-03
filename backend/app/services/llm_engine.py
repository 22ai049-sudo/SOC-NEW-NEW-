from app.services.rag_retriever import retrieve_context


def analyze_event(detection: dict) -> dict:
    refs = retrieve_context(detection.get("indicators", []))
    return {
        "classification": detection["classification"],
        "confidence": round(detection["confidence"] * 100, 2),
        "reasoning": f"Detected indicators: {', '.join(detection.get('indicators', [])) or 'generic anomaly'}",
        "rag_references": refs,
        "suggested_mitigation": "Isolate asset, block IOC, rotate credentials, run EDR scan.",
    }

from datetime import datetime

from app.core import state
from app.services import (
    detector,
    llm_engine,
    mitre_mapper,
    threat_intel_fetcher,
    intel_correlator,
    risk_scoring_engine,
    playbook_generator,
    playbook_repository,
    mitigation_generator,
    agent_orchestrator,
    historical_memory,
)


async def process_log(tenant_id: str, source: str, raw_log: str, asset_criticality: float) -> dict:
    detection = detector.detect_threat(raw_log)
    llm = llm_engine.analyze_event(detection)
    mitre = mitre_mapper.map_mitre(detection["indicators"])
    intel = threat_intel_fetcher.enrich(source, detection["indicators"])
    correlated = intel_correlator.correlate(intel, mitre)
    risk = risk_scoring_engine.score(detection["severity"], detection["confidence"], asset_criticality)

    incident = {
        "id": state.next_id("INC", len(state.incidents) + 1),
        "tenant_id": tenant_id,
        "title": f"{detection['classification'].title()} threat from {source}",
        "severity": risk["risk_level"],
        "source": source,
        "timestamp": datetime.utcnow().isoformat(),
        "confidence": detection["confidence"],
        "mitre_ids": [m["technique_id"] for m in mitre],
        "risk_score": risk["risk_score"],
        "status": "Open",
        "details": {"llm": llm, "mitre": mitre, "intel": correlated},
    }

    playbook = playbook_generator.generate(incident)
    playbook_repository.save(playbook)
    incident["details"]["mitigation"] = mitigation_generator.generate_mitigation(incident)
    incident["details"]["agent"] = agent_orchestrator.run(incident)
    state.incidents.append(incident)
    state.tenant_dashboards[tenant_id]["ingested"] += 1
    historical_memory.append(incident)
    return incident

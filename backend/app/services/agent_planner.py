
def plan(incident: dict) -> dict:
    return {"incident_id": incident["id"], "decision": "execute_playbook", "rationale": "High risk incident requires immediate orchestration"}

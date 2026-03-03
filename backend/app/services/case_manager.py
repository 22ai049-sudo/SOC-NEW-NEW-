from datetime import datetime

from app.core import state


def create_case(tenant_id: str, incident_id: str, assigned_to: str, notes: str) -> dict:
    case = {
        "id": state.next_id("CASE", len(state.cases) + 1),
        "tenant_id": tenant_id,
        "incident_id": incident_id,
        "assigned_to": assigned_to,
        "notes": notes,
        "status": "Open",
        "created_at": datetime.utcnow().isoformat(),
    }
    state.cases.append(case)
    return case


def update_case(case_id: str, status: str, notes: str) -> dict | None:
    for c in state.cases:
        if c["id"] == case_id:
            c["status"] = status
            if notes:
                c["notes"] += f"\n{notes}"
            c["updated_at"] = datetime.utcnow().isoformat()
            return c
    return None

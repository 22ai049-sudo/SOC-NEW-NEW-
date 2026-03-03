from datetime import datetime

from app.core import state


def status(tenant_id: str) -> list[dict]:
    now = datetime.utcnow()
    data = []
    for inc in state.incidents:
        if inc["tenant_id"] != tenant_id:
            continue
        created = datetime.fromisoformat(inc["timestamp"]) if isinstance(inc["timestamp"], str) else inc["timestamp"]
        hours = state.sla_policy_hours.get(inc["severity"], 24)
        elapsed = (now - created).total_seconds() / 3600
        data.append({"incident_id": inc["id"], "severity": inc["severity"], "deadline_hours": hours, "elapsed_hours": round(elapsed, 2), "breached": elapsed > hours})
    return data

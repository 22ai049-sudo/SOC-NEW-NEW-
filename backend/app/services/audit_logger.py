from datetime import datetime

from app.core import state


def log(action: str, user: str, tenant_id: str, payload: dict | None = None) -> None:
    state.audit_logs.append(
        {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "user": user,
            "tenant_id": tenant_id,
            "payload": payload or {},
        }
    )

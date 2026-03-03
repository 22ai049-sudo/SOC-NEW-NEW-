from collections import defaultdict
from datetime import datetime

users = {
    "admin": {"username": "admin", "hashed_password": "", "role": "Admin", "tenant_id": "tenant-a"},
    "manager": {"username": "manager", "hashed_password": "", "role": "Manager", "tenant_id": "tenant-a"},
    "analyst": {"username": "analyst", "hashed_password": "", "role": "Analyst", "tenant_id": "tenant-a"},
}

incidents: list[dict] = []
cases: list[dict] = []
audit_logs: list[dict] = []
agent_activity: list[dict] = []
siem_status = {"splunk": "connected", "wazuh": "connected", "normalized_events": 0}

sla_policy_hours = {"Critical": 1, "High": 4, "Medium": 24, "Low": 72}

tenant_dashboards = defaultdict(lambda: {"ingested": 0, "mitigated": 0})


def next_id(prefix: str, seq: int) -> str:
    return f"{prefix}-{datetime.utcnow().strftime('%Y%m%d')}-{seq:04d}"

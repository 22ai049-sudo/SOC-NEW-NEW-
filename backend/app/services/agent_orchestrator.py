from datetime import datetime

from app.core import state
from app.services import agent_planner, agent_executor, agent_auditor


def run(incident: dict) -> dict:
    plan = agent_planner.plan(incident)
    exe = agent_executor.execute(plan)
    aud = agent_auditor.audit(exe)
    activity = {"timestamp": datetime.utcnow().isoformat(), "incident_id": incident["id"], "plan": plan, "execution": exe, "audit": aud}
    state.agent_activity.append(activity)
    return activity

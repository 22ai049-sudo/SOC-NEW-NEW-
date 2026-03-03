import asyncio
from datetime import datetime
import logging
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import JSONResponse
from jose import JWTError, jwt

from app.core.config import settings
from app.core import state
from app.core.logging_config import setup_logging
from app.models.schemas import UserLogin, TokenResponse, ManualIngestRequest, CaseCreate, CaseUpdate, TenantSwitchRequest
from app.services import (
    auth_manager,
    audit_logger,
    data_ingestion,
    dataset_loader,
    ingestion_scheduler,
    case_manager,
    sla_tracker,
    playbook_repository,
    playbook_executor,
    tenant_manager,
    splunk_connector,
    wazuh_connector,
    rbac_controller,
)

app = FastAPI(title=settings.app_name)
security = HTTPBearer()
metrics_task: asyncio.Task | None = None
logger = logging.getLogger("nexus.api")

setup_logging()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    logger.exception("Unhandled exception on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active:
            self.active.remove(websocket)

    async def broadcast(self, event: dict[str, Any]):
        for ws in list(self.active):
            try:
                await ws.send_json(event)
            except Exception:
                self.disconnect(ws)


ws_manager = ConnectionManager()


def current_user(token: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        payload = jwt.decode(token.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    username = payload.get("sub")
    user = state.users.get(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_role(min_role: str):
    def checker(user: dict = Depends(current_user)) -> dict:
        if not rbac_controller.enforce_role(user, min_role):
            raise HTTPException(status_code=403, detail=f"{min_role} role required")
        return user

    return checker


async def metrics_broadcaster() -> None:
    while True:
        await asyncio.sleep(5)
        for tenant_id in sorted({u["tenant_id"] for u in state.users.values()}):
            tenant_inc = [i for i in state.incidents if i["tenant_id"] == tenant_id and i["status"] != "Closed"]
            avg_risk = round(sum(i["risk_score"] for i in tenant_inc) / len(tenant_inc), 2) if tenant_inc else 0
            await ws_manager.broadcast(
                {
                    "type": "risk_gauge",
                    "data": {
                        "tenant_id": tenant_id,
                        "total_incidents": len(tenant_inc),
                        "avg_risk_score": avg_risk,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                }
            )


@app.on_event("startup")
async def on_startup():
    global metrics_task
    auth_manager.bootstrap_users()
    metrics_task = asyncio.create_task(metrics_broadcaster())


@app.on_event("shutdown")
async def on_shutdown():
    global metrics_task
    if metrics_task:
        metrics_task.cancel()


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name}


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(req: UserLogin):
    user = auth_manager.authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Bad credentials")
    token = auth_manager.create_access_token({"sub": user["username"], "role": user["role"], "tenant_id": user["tenant_id"]})
    logger.info("User login successful username=%s tenant=%s role=%s", user["username"], user["tenant_id"], user["role"])
    return TokenResponse(access_token=token)


@app.get("/api/auth/me")
async def me(user: dict = Depends(current_user)):
    return {"username": user["username"], "role": user["role"], "tenant_id": user["tenant_id"]}


@app.post("/api/ingest/manual")
async def ingest_manual(req: ManualIngestRequest, user: dict = Depends(require_role("Analyst"))):
    incident = await data_ingestion.ingest_manual(user["tenant_id"], req.source, req.raw_log, req.asset_criticality)
    logger.info("Manual ingest completed incident_id=%s tenant=%s", incident["id"], user["tenant_id"])
    audit_logger.log("ingest_manual", user["username"], user["tenant_id"], {"incident_id": incident["id"]})
    await ws_manager.broadcast({"type": "incident_feed", "data": incident})
    return incident


@app.post("/api/ingest/dataset/start")
async def ingest_dataset(user: dict = Depends(require_role("Manager"))):
    created = []
    for item in dataset_loader.SAMPLE_DATASET:
        incident = await data_ingestion.ingest_manual(user["tenant_id"], item["source"], item["raw_log"], item["asset_criticality"])
        created.append(incident)
    await ws_manager.broadcast({"type": "incident_feed_bulk", "data": created})
    return {"ingested": len(created), "incidents": created}


@app.post("/api/ingest/scheduler/toggle")
async def toggle_scheduler(user: dict = Depends(require_role("Manager"))):
    result = ingestion_scheduler.toggle()
    audit_logger.log("scheduler_toggle", user["username"], user["tenant_id"], result)
    return result


@app.get("/api/dashboard/metrics")
async def dashboard_metrics(user: dict = Depends(current_user)):
    tenant_inc = [i for i in state.incidents if i["tenant_id"] == user["tenant_id"]]
    open_inc = [i for i in tenant_inc if i["status"] != "Closed"]
    avg_risk = round(sum(i["risk_score"] for i in open_inc) / len(open_inc), 2) if open_inc else 0
    return {
        "total_incidents": len(open_inc),
        "critical": len([i for i in open_inc if i["severity"] == "Critical"]),
        "high": len([i for i in open_inc if i["severity"] == "High"]),
        "avg_risk_score": avg_risk,
        "mttr_minutes": 8,
    }


@app.get("/api/incidents")
async def get_incidents(user: dict = Depends(current_user)):
    return [i for i in state.incidents if i["tenant_id"] == user["tenant_id"]]


@app.get("/api/incidents/{incident_id}")
async def get_incident(incident_id: str, user: dict = Depends(current_user)):
    inc = next((i for i in state.incidents if i["id"] == incident_id and i["tenant_id"] == user["tenant_id"]), None)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc


@app.post("/api/mitigation/approve")
async def approve_mitigation(payload: dict, user: dict = Depends(require_role("Analyst"))):
    incident_id = payload.get("incident_id")
    incident = next((i for i in state.incidents if i["id"] == incident_id and i["tenant_id"] == user["tenant_id"]), None)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident["status"] = "Investigating"
    audit_logger.log("mitigation_approve", user["username"], user["tenant_id"], {"incident_id": incident_id})
    return {"incident_id": incident_id, "status": "approved"}


@app.post("/api/mitigation/reject")
async def reject_mitigation(payload: dict, user: dict = Depends(require_role("Analyst"))):
    incident_id = payload.get("incident_id")
    incident = next((i for i in state.incidents if i["id"] == incident_id and i["tenant_id"] == user["tenant_id"]), None)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident["status"] = "Open"
    reason = payload.get("reason", "")
    audit_logger.log("mitigation_reject", user["username"], user["tenant_id"], {"incident_id": incident_id, "reason": reason})
    return {"incident_id": incident_id, "status": "rejected", "reason": reason}


@app.post("/api/mitigation/execute")
async def execute_mitigation(payload: dict, user: dict = Depends(require_role("Manager"))):
    incident_id = payload.get("incident_id")
    incident = next((i for i in state.incidents if i["id"] == incident_id and i["tenant_id"] == user["tenant_id"]), None)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    playbook = playbook_repository.get(incident_id)
    result = playbook_executor.execute(playbook) if playbook else {"result": "no_playbook"}
    incident["status"] = "Contained" if result.get("result") == "success" else incident["status"]
    logger.info("Mitigation execution incident_id=%s result=%s", incident_id, result.get("result"))
    audit_logger.log("mitigation_execute", user["username"], user["tenant_id"], {"incident_id": incident_id, "result": result.get("result")})
    await ws_manager.broadcast({"type": "pipeline_stage", "data": {"incident_id": incident_id, "stage": "sandbox_execution", "result": result}})
    return result


@app.get("/api/cases")
async def get_cases(user: dict = Depends(current_user)):
    return [c for c in state.cases if c["tenant_id"] == user["tenant_id"]]


@app.post("/api/cases")
async def post_cases(req: CaseCreate, user: dict = Depends(require_role("Analyst"))):
    case = case_manager.create_case(user["tenant_id"], req.incident_id, req.assigned_to, req.notes)
    audit_logger.log("case_create", user["username"], user["tenant_id"], {"case_id": case["id"], "incident_id": req.incident_id})
    return case


@app.put("/api/cases/{case_id}")
async def put_case(case_id: str, req: CaseUpdate, user: dict = Depends(require_role("Analyst"))):
    case = case_manager.update_case(case_id, req.status, req.notes)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    audit_logger.log("case_update", user["username"], user["tenant_id"], {"case_id": case_id, "status": req.status})
    return case


@app.get("/api/sla/status")
async def get_sla(user: dict = Depends(current_user)):
    return sla_tracker.status(user["tenant_id"])


@app.get("/api/audit")
async def get_audit(user: dict = Depends(current_user)):
    return [a for a in state.audit_logs if a["tenant_id"] == user["tenant_id"]]


@app.get("/api/agents/activity")
async def get_agents_activity(user: dict = Depends(current_user)):
    return [a for a in state.agent_activity if any(i["id"] == a["incident_id"] and i["tenant_id"] == user["tenant_id"] for i in state.incidents)]


@app.get("/api/siem/status")
async def get_siem_status(user: dict = Depends(current_user)):
    return {"splunk": splunk_connector.status(), "wazuh": wazuh_connector.status(), "updated": datetime.utcnow().isoformat()}


@app.post("/api/tenant/switch")
async def switch_tenant(req: TenantSwitchRequest, user: dict = Depends(require_role("Analyst"))):
    tenant_manager.switch_tenant(user, req.tenant_id)
    audit_logger.log("tenant_switch", user["username"], req.tenant_id, {"username": user["username"]})
    return {"tenant_id": req.tenant_id}


@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    await ws_manager.connect(websocket)
    await websocket.send_json({"type": "notifications", "data": {"message": "connected", "timestamp": datetime.utcnow().isoformat()}})
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

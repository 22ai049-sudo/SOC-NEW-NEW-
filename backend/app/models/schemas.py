from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ManualIngestRequest(BaseModel):
    source: str = "manual"
    raw_log: str
    asset_criticality: float = 1.0


class Incident(BaseModel):
    id: str
    tenant_id: str
    title: str
    severity: str
    source: str
    timestamp: datetime
    confidence: float
    mitre_ids: list[str]
    risk_score: float
    status: str = "Open"
    details: dict[str, Any] = Field(default_factory=dict)


class CaseCreate(BaseModel):
    incident_id: str
    assigned_to: str
    notes: str = ""


class CaseUpdate(BaseModel):
    status: str
    notes: str = ""


class TenantSwitchRequest(BaseModel):
    tenant_id: str

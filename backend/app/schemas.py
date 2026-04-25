from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID
from .models import RoleEnum, EventTypeEnum, SeverityEnum

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str
    email: str
    department: str
    role: RoleEnum

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    baseline_computed: bool
    latest_risk_score: Optional[float] = 0.0

    class Config:
        from_attributes = True

class LogIngestRequest(BaseModel):
    user_id: UUID
    event_type: EventTypeEnum
    resource_accessed: Optional[str] = None
    ip_address: Optional[str] = "0.0.0.0"
    metadata: Optional[dict] = Field(default_factory=dict, alias="metadata_")

class LogIngestResponse(BaseModel):
    log_id: UUID
    risk_score: float
    is_anomalous: bool
    alert_created: bool

class ActivityLogResponse(BaseModel):
    id: UUID
    user_id: UUID
    event_type: EventTypeEnum
    resource_accessed: Optional[str]
    ip_address: str
    timestamp: datetime
    metadata_: Optional[dict]
    risk_score: Optional[float]
    is_anomalous: bool
    flag_reason: Optional[str]

    class Config:
        from_attributes = True

class AlertResponse(BaseModel):
    id: UUID
    user_id: UUID
    severity: SeverityEnum
    alert_type: str
    description: str
    triggered_at: datetime
    acknowledged: bool
    
    class Config:
        from_attributes = True

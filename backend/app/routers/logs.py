from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models import ActivityLog, User
from app.schemas import LogIngestRequest, LogIngestResponse, ActivityLogResponse
from app.dependencies import get_current_user
from app.services.scoring_service import process_log

router = APIRouter(prefix="/logs", tags=["logs"])

@router.post("/ingest", response_model=LogIngestResponse)
def ingest_log(request: LogIngestRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Note: In production, scoring could be sent to a background task
    log, risk_score, is_anomalous, alert_created = process_log(request, db)
    return {
        "log_id": log.id,
        "risk_score": risk_score,
        "is_anomalous": is_anomalous,
        "alert_created": alert_created
    }

@router.get("", response_model=List[ActivityLogResponse])
def get_logs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logs = db.query(ActivityLog).order_by(ActivityLog.timestamp.desc()).offset(skip).limit(limit).all()
    return logs

@router.get("/{id}", response_model=ActivityLogResponse)
def get_log(id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    log = db.query(ActivityLog).filter(ActivityLog.id == id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log

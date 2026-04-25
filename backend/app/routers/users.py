from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy import func

from app.database import get_db
from app.models import User, ActivityLog, Alert
from app.schemas import UserResponse, ActivityLogResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=List[UserResponse])
def get_users(dept: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(User)
    if dept:
        query = query.filter(User.department == dept)
    users = query.offset(skip).limit(limit).all()
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    risk_scores = db.query(
        ActivityLog.user_id, 
        func.max(ActivityLog.risk_score).label('max_risk')
    ).filter(
        ActivityLog.timestamp >= thirty_days_ago
    ).group_by(ActivityLog.user_id).all()
    
    risk_map = {r.user_id: r.max_risk for r in risk_scores}
    
    for user in users:
        setattr(user, "latest_risk_score", risk_map.get(user.id) or 0.0)
        
    return users

@router.get("/{id}")
def get_user(id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    baseline = user.baseline
    alerts_count = db.query(Alert).filter(Alert.user_id == id, Alert.acknowledged == False).count()
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    max_risk = db.query(func.max(ActivityLog.risk_score)).filter(
        ActivityLog.user_id == id, 
        ActivityLog.timestamp >= thirty_days_ago
    ).scalar()
    
    setattr(user, "latest_risk_score", max_risk or 0.0)
    
    return {
        "user": user,
        "baseline": baseline,
        "active_alerts": alerts_count
    }

@router.get("/{id}/activity", response_model=List[ActivityLogResponse])
def get_user_activity(id: UUID, skip: int = 0, limit: int = 20, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logs = db.query(ActivityLog).filter(ActivityLog.user_id == id).order_by(ActivityLog.timestamp.desc()).offset(skip).limit(limit).all()
    return logs

@router.get("/{id}/risk-history")
def get_risk_history(id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    logs = db.query(ActivityLog).filter(ActivityLog.user_id == id, ActivityLog.timestamp >= thirty_days_ago).order_by(ActivityLog.timestamp.asc()).all()
    
    # Aggregate by day
    history = {}
    for log in logs:
        day = log.timestamp.strftime("%Y-%m-%d")
        if day not in history:
            history[day] = []
        if log.risk_score is not None:
            history[day].append(log.risk_score)
            
    result = []
    for day, scores in history.items():
        avg_score = sum(scores) / len(scores) if scores else 0
        result.append({"date": day, "avg_risk": avg_score})
        
    return result

@router.get("/{id}/anomalies", response_model=List[ActivityLogResponse])
def get_user_anomalies(id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logs = db.query(ActivityLog).filter(ActivityLog.user_id == id, ActivityLog.is_anomalous == True).order_by(ActivityLog.timestamp.desc()).limit(50).all()
    return logs

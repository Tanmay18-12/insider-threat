from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db
from app.models import User, Alert, ActivityLog, MLModel
from app.dependencies import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/summary")
def get_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_users = db.query(User).count()
    active_alerts = db.query(Alert).filter(Alert.acknowledged == False).count()
    
    last_24h = datetime.utcnow() - timedelta(hours=24)
    avg_risk = db.query(func.avg(ActivityLog.risk_score)).filter(ActivityLog.timestamp >= last_24h).scalar() or 0.0
    
    high_risk_users = db.query(ActivityLog.user_id).filter(ActivityLog.risk_score > 75, ActivityLog.timestamp >= last_24h).distinct().count()
    
    return {
        "total_users": total_users,
        "active_alerts": active_alerts,
        "avg_risk": avg_risk,
        "high_risk_count": high_risk_users
    }

@router.get("/risk-heatmap")
def get_risk_heatmap(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Simple mock or real aggregation
    # Users x Hours
    last_24h = datetime.utcnow() - timedelta(hours=24)
    logs = db.query(ActivityLog.user_id, ActivityLog.timestamp, ActivityLog.risk_score).filter(ActivityLog.timestamp >= last_24h).all()
    
    heatmap = {}
    for log in logs:
        uid = str(log.user_id)
        hour = log.timestamp.hour
        if uid not in heatmap:
            heatmap[uid] = {}
        if hour not in heatmap[uid]:
            heatmap[uid][hour] = []
        heatmap[uid][hour].append(log.risk_score or 0)
        
    # Average them
    result = []
    for uid, hours in heatmap.items():
        for hour, scores in hours.items():
            result.append({
                "user_id": uid,
                "hour": hour,
                "avg_risk": sum(scores)/len(scores)
            })
            
    return result

@router.get("/top-threats")
def get_top_threats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    last_24h = datetime.utcnow() - timedelta(hours=24)
    query = db.query(
        ActivityLog.user_id, 
        User.username,
        func.max(ActivityLog.risk_score).label("max_score")
    ).join(User).filter(ActivityLog.timestamp >= last_24h).group_by(ActivityLog.user_id, User.username).order_by(func.max(ActivityLog.risk_score).desc()).limit(10)
    
    return [{"user_id": str(r[0]), "username": r[1], "risk_score": r[2]} for r in query]

@router.get("/trend")
def get_trend(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    thirty_days = datetime.utcnow() - timedelta(days=30)
    logs = db.query(ActivityLog).filter(ActivityLog.is_anomalous == True, ActivityLog.timestamp >= thirty_days).all()
    
    trend = {}
    for log in logs:
        day = log.timestamp.strftime("%Y-%m-%d")
        trend[day] = trend.get(day, 0) + 1
        
    return [{"date": k, "anomalies": v} for k, v in sorted(trend.items())]

@router.get("/department")
def get_dept_risk(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    last_24h = datetime.utcnow() - timedelta(hours=24)
    query = db.query(
        User.department,
        func.avg(ActivityLog.risk_score).label("avg_risk")
    ).join(ActivityLog).filter(ActivityLog.timestamp >= last_24h).group_by(User.department)
    
    return [{"department": r[0], "avg_risk": r[1] or 0.0} for r in query]

@router.get("/models")
def get_models(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    models = db.query(MLModel).order_by(MLModel.trained_at.desc()).all()
    return models

from sqlalchemy.orm import Session
from datetime import datetime
from app.models import ActivityLog, UserBaseline, User, Alert, SeverityEnum
from app.schemas import LogIngestRequest
from app.services.ml_service import ml_service
from app.services.alert_service import alert_service
from app.config import RISK_THRESHOLD

def process_log(log_data: LogIngestRequest, db: Session):
    user = db.query(User).filter(User.id == log_data.user_id).first()
    baseline = db.query(UserBaseline).filter(UserBaseline.user_id == log_data.user_id).first()
    
    now = datetime.utcnow()
    
    # Simple feature extraction for ML
    features = {
        'hour_of_day': now.hour,
        'is_weekend': int(now.weekday() >= 5),
        'event_type': log_data.event_type.value,
        'resource_sensitivity_score': 1.0 if ('sensitive' in str(log_data.resource_accessed).lower()) else 0.1,
        'session_file_count': 1,
        'failed_auth_count_last_1h': 0,
        'cross_dept_access_flag': 0,
        'ip_changed_flag': 0,
        'cumulative_risk_last_24h': 0,
        'deviation_from_baseline': 0
    }
    
    if user and baseline:
        if log_data.resource_accessed and '/' in log_data.resource_accessed:
            dept = log_data.resource_accessed.split('/')[0].lower()
            if dept != user.department.lower():
                features['cross_dept_access_flag'] = 1
                
        if log_data.event_type == 'FAILED_AUTH':
            features['failed_auth_count_last_1h'] = 1
            
        if now.hour not in (baseline.typical_hours or []):
            features['deviation_from_baseline'] += 0.5
            
    # ML Scoring
    risk_score = ml_service.score_event(features)
    is_anomalous = risk_score > RISK_THRESHOLD
    
    # Save log
    new_log = ActivityLog(
        user_id=log_data.user_id,
        event_type=log_data.event_type,
        resource_accessed=log_data.resource_accessed,
        ip_address=log_data.ip_address,
        metadata_=log_data.metadata,
        risk_score=risk_score,
        is_anomalous=is_anomalous,
        timestamp=now
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    
    alert_created = False
    if is_anomalous:
        severity = SeverityEnum.CRITICAL if risk_score > 90 else SeverityEnum.HIGH
        alert = Alert(
            user_id=log_data.user_id,
            severity=severity,
            alert_type="High Risk Activity",
            description=f"Risk score {risk_score:.2f} detected for {log_data.event_type.value}",
            triggered_at=now,
            activity_log_id=new_log.id
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        alert_created = True
        
        # Publish real-time alert
        alert_data = {
            "alert_id": alert.id,
            "user_id": user.id if user else None,
            "username": user.username if user else "Unknown",
            "severity": severity.value,
            "alert_type": alert.alert_type,
            "risk_score": risk_score,
            "timestamp": now
        }
        alert_service.publish_alert(alert_data)
        
    return new_log, risk_score, is_anomalous, alert_created

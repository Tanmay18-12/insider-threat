import os
import sys
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

# Ensure we can import from backend app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.database import SessionLocal
from app.models import User, ActivityLog, UserBaseline

def build_baselines():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            logs = db.query(ActivityLog).filter(ActivityLog.user_id == user.id).all()
            if not logs:
                continue

            # Compute avg daily logins
            login_logs = [l for l in logs if l.event_type == 'LOGIN']
            days_active = len(set(l.timestamp.date() for l in logs)) or 1
            avg_logins = len(login_logs) / days_active

            # Typical hours
            hours = [l.timestamp.hour for l in logs]
            typical_hours = list(set(hours)) if hours else []

            # Common resources
            resources = [l.resource_accessed for l in logs if l.resource_accessed]
            common_resources = list(set(resources))[:10] # Simplified

            # Avg file accesses
            file_logs = [l for l in logs if 'FILE' in str(l.event_type)]
            avg_file = len(file_logs) / days_active

            # Departments accessed
            depts = [str(r).split('/')[0] for r in resources if '/' in str(r)]
            departments_accessed = list(set(depts))

            baseline = db.query(UserBaseline).filter(UserBaseline.user_id == user.id).first()
            if not baseline:
                baseline = UserBaseline(user_id=user.id)
                db.add(baseline)
            
            baseline.avg_daily_logins = avg_logins
            baseline.typical_hours = typical_hours
            baseline.common_resources = common_resources
            baseline.avg_file_accesses = avg_file
            baseline.departments_accessed = departments_accessed
            baseline.model_version = "1.0"
            
            user.baseline_computed = True

        db.commit()
        print("Baselines built successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    build_baselines()

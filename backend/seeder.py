import random
from datetime import datetime, timedelta
from faker import Faker
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, User, ActivityLog, RoleEnum, EventTypeEnum
import uuid

fake = Faker()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEPARTMENTS = ["Engineering", "Finance", "HR", "Operations", "Legal"]
NUM_USERS = 50
NUM_NORMAL_LOGS = 10000
NUM_ANOMALIES = 200

def get_password_hash(password):
    return pwd_context.hash(password)

def seed_users(db: Session):
    users = []
    # Create 1 admin
    admin = User(
        username="admin",
        email="admin@company.com",
        department="Engineering",
        role=RoleEnum.ADMIN,
        hashed_password=get_password_hash("Admin123!"),
    )
    db.add(admin)
    users.append(admin)
    
    for _ in range(NUM_USERS - 1):
        user = User(
            username=fake.user_name(),
            email=fake.email(),
            department=random.choice(DEPARTMENTS),
            role=RoleEnum.USER,
            hashed_password=get_password_hash("password123"),
        )
        db.add(user)
        users.append(user)
    
    db.commit()
    for u in users:
        db.refresh(u)
    return users

def generate_normal_logs(db: Session, users: list):
    logs = []
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    for _ in range(NUM_NORMAL_LOGS):
        user = random.choice(users)
        
        # 08:00 - 18:00
        days_offset = random.randint(0, 30)
        base_time = start_date + timedelta(days=days_offset)
        hour = random.randint(8, 17)
        minute = random.randint(0, 59)
        timestamp = base_time.replace(hour=hour, minute=minute)
        
        event_type = random.choice(list(EventTypeEnum))
        resource = f"{user.department.lower()}/resource_{random.randint(1, 100)}.txt"
        
        # Calculate risk score base
        score = random.uniform(0, 10) # very low score for normal
        
        log = ActivityLog(
            user_id=user.id,
            event_type=event_type,
            resource_accessed=resource,
            ip_address=fake.ipv4(),
            timestamp=timestamp,
            metadata_={"file_count": random.randint(1, 5)},
            risk_score=score,
            is_anomalous=False
        )
        logs.append(log)
    
    db.bulk_save_objects(logs)
    db.commit()

def generate_anomalous_logs(db: Session, users: list):
    logs = []
    end_date = datetime.utcnow()
    
    # Select specific users for specific anomalies
    off_hours_users = random.sample(users, 10)
    mass_download_users = random.sample(users, 5)
    cross_dept_users = random.sample(users, 8)
    failed_auth_users = random.sample(users, 7)
    priv_esc_users = random.sample(users, 3)
    foreign_ip_users = random.sample(users, 5)

    for i in range(NUM_ANOMALIES):
        anomaly_type = random.choice(["off_hours", "mass_download", "cross_dept", "failed_auth", "priv_esc", "foreign_ip"])
        timestamp = end_date - timedelta(days=random.randint(0, 5))
        
        base_score = 0.0
        user = None
        event_type = EventTypeEnum.FILE_ACCESS
        resource = ""
        ip = fake.ipv4()
        meta = {}
        
        if anomaly_type == "off_hours":
            user = random.choice(off_hours_users)
            timestamp = timestamp.replace(hour=random.choice([22, 23, 0, 1, 2, 3]))
            base_score += 30
            event_type = EventTypeEnum.LOGIN
        elif anomaly_type == "mass_download":
            user = random.choice(mass_download_users)
            meta = {"file_count": random.randint(201, 500)}
            base_score += 15
            event_type = EventTypeEnum.FILE_DOWNLOAD
        elif anomaly_type == "cross_dept":
            user = random.choice(cross_dept_users)
            other_depts = [d for d in DEPARTMENTS if d != user.department]
            resource = f"{random.choice(other_depts).lower()}/sensitive_payroll.xlsx"
            base_score += 20 + 10 # sensitive + cross_dept
        elif anomaly_type == "failed_auth":
            user = random.choice(failed_auth_users)
            event_type = EventTypeEnum.FAILED_AUTH
            base_score += 25
        elif anomaly_type == "priv_esc":
            user = random.choice(priv_esc_users)
            event_type = EventTypeEnum.PRIVILEGE_ESCALATION
            base_score += 50
        elif anomaly_type == "foreign_ip":
            user = random.choice(foreign_ip_users)
            ip = "185.15.59.224" # some static assumed foreign IP
            base_score += 20
            
        # Clamp score
        base_score = min(base_score + random.uniform(5, 20), 100.0)
        
        log = ActivityLog(
            user_id=user.id,
            event_type=event_type,
            resource_accessed=resource or f"{user.department.lower()}/file.txt",
            ip_address=ip,
            timestamp=timestamp,
            metadata_=meta,
            risk_score=base_score,
            is_anomalous=True,
            flag_reason=anomaly_type
        )
        logs.append(log)
        
    db.bulk_save_objects(logs)
    db.commit()

def run_seeder():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Clear existing data
        print("Clearing existing data...")
        db.query(ActivityLog).delete()
        db.query(User).delete()
        db.commit()

        print("Seeding users...")
        users = seed_users(db)
        
        print("Seeding normal logs...")
        generate_normal_logs(db, users)
        
        print("Seeding anomalous logs...")
        generate_anomalous_logs(db, users)
        
        print("Database seeded successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    run_seeder()

import uuid
from sqlalchemy import Column, String, Boolean, Float, DateTime, ForeignKey, Text, Enum, JSON, Uuid
import enum
from datetime import datetime
from sqlalchemy.orm import relationship
from .database import Base

class RoleEnum(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class EventTypeEnum(str, enum.Enum):
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    FILE_ACCESS = "FILE_ACCESS"
    FILE_DOWNLOAD = "FILE_DOWNLOAD"
    FILE_UPLOAD = "FILE_UPLOAD"
    FILE_DELETE = "FILE_DELETE"
    SYSTEM_ACCESS = "SYSTEM_ACCESS"
    NETWORK_REQUEST = "NETWORK_REQUEST"
    PRIVILEGE_ESCALATION = "PRIVILEGE_ESCALATION"
    USB_DEVICE = "USB_DEVICE"
    EMAIL_SENT = "EMAIL_SENT"
    DATABASE_QUERY = "DATABASE_QUERY"
    CONFIG_CHANGE = "CONFIG_CHANGE"
    FAILED_AUTH = "FAILED_AUTH"

class SeverityEnum(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    department = Column(String)
    role = Column(Enum(RoleEnum), default=RoleEnum.USER)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    baseline_computed = Column(Boolean, default=False)
    hashed_password = Column(String)

    activity_logs = relationship("ActivityLog", back_populates="user")
    baseline = relationship("UserBaseline", back_populates="user", uselist=False)
    alerts = relationship("Alert", back_populates="user", foreign_keys="[Alert.user_id]")

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id"))
    event_type = Column(Enum(EventTypeEnum))
    resource_accessed = Column(String, nullable=True)
    ip_address = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_ = Column("metadata", JSON, nullable=True)
    risk_score = Column(Float, nullable=True)
    is_anomalous = Column(Boolean, default=False)
    flag_reason = Column(Text, nullable=True)

    user = relationship("User", back_populates="activity_logs")

class UserBaseline(Base):
    __tablename__ = "user_baselines"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id"), unique=True)
    avg_daily_logins = Column(Float)
    typical_hours = Column(JSON)
    common_resources = Column(JSON)
    avg_file_accesses = Column(Float)
    departments_accessed = Column(JSON)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    model_version = Column(String, nullable=True)

    user = relationship("User", back_populates="baseline")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id"))
    severity = Column(Enum(SeverityEnum))
    alert_type = Column(String)
    description = Column(String)
    triggered_at = Column(DateTime, default=datetime.utcnow)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(Uuid, ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    activity_log_id = Column(Uuid, ForeignKey("activity_logs.id"), nullable=True)

    user = relationship("User", back_populates="alerts", foreign_keys=[user_id])
    activity_log = relationship("ActivityLog")

class MLModel(Base):
    __tablename__ = "ml_models"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    model_name = Column(String, index=True)
    model_type = Column(String)
    accuracy = Column(Float)
    f1_score = Column(Float)
    trained_at = Column(DateTime, default=datetime.utcnow)
    feature_columns = Column(JSON)
    is_active = Column(Boolean, default=False)
    file_path = Column(String)

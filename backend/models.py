"""
SQLAlchemy ORM models for ABPS database.
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, Text, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base
import enum


class DepartmentEnum(str, enum.Enum):
    ENGINEERING = "Engineering"
    SNT = "Signal & Telecom"
    TRD = "Traction Distribution"


class TaskStatusEnum(str, enum.Enum):
    PENDING = "Pending"
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    DEFERRED = "Deferred"


class PlanStatusEnum(str, enum.Enum):
    DRAFT = "Draft"
    PROPOSED = "Proposed"
    APPROVED = "Approved"
    PUBLISHED = "Published"
    REJECTED = "Rejected"


class UserRoleEnum(str, enum.Enum):
    ADMIN = "Admin"
    PLANNER = "Planner"
    CONTROLLER = "Controller"
    APPROVER = "Approver"
    VIEWER = "Viewer"


class Section(Base):
    """Railway section / corridor."""
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True)
    name = Column(String(100))
    zone = Column(String(50))
    division = Column(String(50))
    track_length_km = Column(Float)
    traffic_density = Column(Float, default=1.0)   # 1=low, 2=medium, 3=high
    is_electrified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tasks = relationship("MaintenanceTask", back_populates="section")
    block_windows = relationship("BlockWindow", back_populates="section")


class MaintenanceTask(Base):
    """Maintenance task from TMS / SMMS / TDMS."""
    __tablename__ = "maintenance_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(30), unique=True, index=True)
    source_system = Column(String(10))             # TMS / SMMS / TDMS
    department = Column(String(50))
    section_id = Column(Integer, ForeignKey("sections.id"))
    asset_id = Column(String(30))
    asset_type = Column(String(50))
    description = Column(Text)
    defect_type = Column(String(50))
    severity = Column(Integer)                     # 1 (low) – 5 (critical)
    safety_critical = Column(Boolean, default=False)
    overdue_days = Column(Integer, default=0)
    due_date = Column(DateTime)
    duration_hours = Column(Float)                 # block duration needed
    crew_size = Column(Integer, default=4)
    block_type = Column(String(20))                # Traffic / Power / Both
    status = Column(String(20), default="Pending")
    priority_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    section = relationship("Section", back_populates="tasks")
    schedule_items = relationship("ScheduleItem", back_populates="task")


class BlockWindow(Base):
    """Available time window for a block in a section."""
    __tablename__ = "block_windows"

    id = Column(Integer, primary_key=True, index=True)
    window_id = Column(String(30), unique=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_hours = Column(Float)
    trains_affected = Column(Integer, default=0)
    train_minutes_impact = Column(Float, default=0.0)
    allows_traffic_block = Column(Boolean, default=True)
    allows_power_block = Column(Boolean, default=True)
    capacity_crew = Column(Integer, default=20)
    status = Column(String(20), default="Available")  # Available/Reserved/Sanctioned
    created_at = Column(DateTime, default=datetime.utcnow)

    section = relationship("Section", back_populates="block_windows")
    schedule_items = relationship("ScheduleItem", back_populates="window")


class Plan(Base):
    """A block plan (weekly or monthly)."""
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String(30), unique=True, index=True)
    plan_type = Column(String(10))                  # Weekly / Monthly
    horizon_start = Column(DateTime)
    horizon_end = Column(DateTime)
    status = Column(String(20), default="Draft")
    created_by = Column(Integer, ForeignKey("users.id"))
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    asset_availability_pct = Column(Float, default=0.0)
    blocks_saved = Column(Integer, default=0)
    train_minutes_lost = Column(Float, default=0.0)
    tasks_scheduled = Column(Integer, default=0)
    tasks_unscheduled = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = relationship("ScheduleItem", back_populates="plan")
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])


class ScheduleItem(Base):
    """A single task scheduled in a block window within a plan."""
    __tablename__ = "schedule_items"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id"))
    task_id = Column(Integer, ForeignKey("maintenance_tasks.id"))
    window_id = Column(Integer, ForeignKey("block_windows.id"))
    is_joint_block = Column(Boolean, default=False)
    joint_block_group = Column(String(30), nullable=True)
    confirmed_by_dept = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    plan = relationship("Plan", back_populates="items")
    task = relationship("MaintenanceTask", back_populates="schedule_items")
    window = relationship("BlockWindow", back_populates="schedule_items")


class User(Base):
    """System user with role-based access."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    full_name = Column(String(100))
    email = Column(String(100), unique=True)
    hashed_password = Column(String(200))
    role = Column(String(20), default="Viewer")
    department = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)


class AuditLog(Base):
    """Append-only audit trail for all significant actions."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100))
    entity_type = Column(String(50))
    entity_id = Column(String(30))
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")

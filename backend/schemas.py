"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ── Auth ──────────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: str


# ── Section ───────────────────────────────────────────────────────────────────
class SectionOut(BaseModel):
    id: int
    code: str
    name: str
    zone: str
    division: str
    track_length_km: float
    traffic_density: float
    is_electrified: bool

    class Config:
        from_attributes = True


# ── Task ──────────────────────────────────────────────────────────────────────
class TaskOut(BaseModel):
    id: int
    task_id: str
    source_system: str
    department: str
    section_id: int
    asset_id: str
    asset_type: str
    description: str
    defect_type: str
    severity: int
    safety_critical: bool
    overdue_days: int
    due_date: datetime
    duration_hours: float
    crew_size: int
    block_type: str
    status: str
    priority_score: float

    class Config:
        from_attributes = True


class ScoreBreakdown(BaseModel):
    task_id: str
    total_score: float
    severity_component: float
    urgency_component: float
    asset_criticality_component: float
    traffic_density_component: float
    must_schedule: bool
    label: str


# ── Block Window ──────────────────────────────────────────────────────────────
class WindowOut(BaseModel):
    id: int
    window_id: str
    section_id: int
    start_time: datetime
    end_time: datetime
    duration_hours: float
    trains_affected: int
    train_minutes_impact: float
    allows_traffic_block: bool
    allows_power_block: bool
    capacity_crew: int
    status: str

    class Config:
        from_attributes = True


# ── Plan ──────────────────────────────────────────────────────────────────────
class GeneratePlanRequest(BaseModel):
    plan_type: str           # Weekly / Monthly
    horizon_start: datetime
    horizon_end: datetime
    section_ids: Optional[List[int]] = None   # None = all sections


class PlanOut(BaseModel):
    id: int
    plan_id: str
    plan_type: str
    horizon_start: datetime
    horizon_end: datetime
    status: str
    asset_availability_pct: float
    blocks_saved: int
    train_minutes_lost: float
    tasks_scheduled: int
    tasks_unscheduled: int
    created_at: datetime

    class Config:
        from_attributes = True


class ApprovePlanRequest(BaseModel):
    action: str            # approve / reject
    reason: Optional[str] = None


# ── KPI ───────────────────────────────────────────────────────────────────────
class KPISummary(BaseModel):
    total_tasks: int
    pending_tasks: int
    scheduled_tasks: int
    overdue_tasks: int
    safety_critical_tasks: int
    active_plans: int
    asset_availability_pct: float
    blocks_saved: int
    train_minutes_lost: float


# ── User ──────────────────────────────────────────────────────────────────────
class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    email: str
    role: str
    department: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    full_name: str
    email: str
    password: str
    role: str
    department: Optional[str] = None


# ── Audit ─────────────────────────────────────────────────────────────────────
class AuditLogOut(BaseModel):
    id: int
    action: str
    entity_type: str
    entity_id: str
    old_value: Optional[str]
    new_value: Optional[str]
    details: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


# ── Benchmark ─────────────────────────────────────────────────────────────────
class BenchmarkResult(BaseModel):
    abps_scheduled: int
    abps_unscheduled: int
    abps_blocks_used: int
    abps_blocks_saved: int
    abps_train_minutes: float
    abps_availability: float
    baseline_scheduled: int
    baseline_unscheduled: int
    baseline_blocks: int
    baseline_train_minutes: float
    baseline_availability: float
    improvement_scheduled_pct: float
    improvement_blocks_saved: float
    improvement_train_minutes_pct: float

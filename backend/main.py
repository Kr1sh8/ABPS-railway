"""
FastAPI main application — ABPS REST API.
Run: uvicorn backend.main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import uuid

from backend.database import get_db, engine
from backend import models, schemas
from backend.auth import verify_password, get_password_hash, create_access_token, decode_token
from backend.scoring import compute_priority_score, get_score_label
from backend.optimizer import run_optimizer, run_greedy_baseline

# Create tables if not exists
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ABPS — Automatic Block Planning System",
    description="AI-powered railway maintenance block scheduler | Ministry of Railways PS-26027",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_current_user(token: str, db: Session):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(models.User).filter(models.User.username == payload.get("sub")).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


def add_audit(db: Session, user_id: Optional[int], action: str, entity_type: str,
              entity_id: str, details: str = None, old_val=None, new_val=None):
    log = models.AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        old_value=str(old_val) if old_val else None,
        new_value=str(new_val) if new_val else None,
        details=details,
    )
    db.add(log)
    db.commit()


# ── Auth ──────────────────────────────────────────────────────────────────────
@app.post("/auth/login", response_model=schemas.TokenResponse, tags=["Auth"])
def login(req: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == req.username).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    user.last_login = datetime.utcnow()
    db.commit()
    token = create_access_token({"sub": user.username, "role": user.role})
    add_audit(db, user.id, "LOGIN", "User", user.username)
    return schemas.TokenResponse(access_token=token, role=user.role, full_name=user.full_name)


# ── Sections ──────────────────────────────────────────────────────────────────
@app.get("/sections", response_model=List[schemas.SectionOut], tags=["Sections"])
def get_sections(db: Session = Depends(get_db)):
    return db.query(models.Section).all()


@app.get("/sections/{section_id}", response_model=schemas.SectionOut, tags=["Sections"])
def get_section(section_id: int, db: Session = Depends(get_db)):
    sec = db.query(models.Section).filter(models.Section.id == section_id).first()
    if not sec:
        raise HTTPException(404, "Section not found")
    return sec


# ── Tasks ─────────────────────────────────────────────────────────────────────
@app.get("/tasks", response_model=List[schemas.TaskOut], tags=["Tasks"])
def get_tasks(
    department: Optional[str] = None,
    section_id: Optional[int] = None,
    status: Optional[str] = None,
    min_score: Optional[float] = None,
    db: Session = Depends(get_db)
):
    q = db.query(models.MaintenanceTask)
    if department:
        q = q.filter(models.MaintenanceTask.department == department)
    if section_id:
        q = q.filter(models.MaintenanceTask.section_id == section_id)
    if status:
        q = q.filter(models.MaintenanceTask.status == status)
    if min_score is not None:
        q = q.filter(models.MaintenanceTask.priority_score >= min_score)
    return q.order_by(models.MaintenanceTask.priority_score.desc()).all()


@app.get("/tasks/{task_id}/score", response_model=schemas.ScoreBreakdown, tags=["Tasks"])
def get_task_score(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.MaintenanceTask).filter(models.MaintenanceTask.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    section = db.query(models.Section).filter(models.Section.id == task.section_id).first()
    days_left = (task.due_date - datetime.utcnow()).days
    score = compute_priority_score(
        severity=task.severity,
        overdue_days=task.overdue_days,
        due_date_days_left=days_left,
        asset_type=task.asset_type,
        traffic_density=section.traffic_density if section else 1.0,
        safety_critical=task.safety_critical,
    )
    return schemas.ScoreBreakdown(
        task_id=task.task_id,
        label=get_score_label(score["total_score"]),
        **score
    )


# ── Block Windows ─────────────────────────────────────────────────────────────
@app.get("/windows", response_model=List[schemas.WindowOut], tags=["Windows"])
def get_windows(
    section_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    q = db.query(models.BlockWindow)
    if section_id:
        q = q.filter(models.BlockWindow.section_id == section_id)
    if date_from:
        q = q.filter(models.BlockWindow.start_time >= date_from)
    if date_to:
        q = q.filter(models.BlockWindow.end_time <= date_to)
    return q.order_by(models.BlockWindow.start_time).all()


# ── Plans ─────────────────────────────────────────────────────────────────────
@app.get("/plans", response_model=List[schemas.PlanOut], tags=["Plans"])
def get_plans(db: Session = Depends(get_db)):
    return db.query(models.Plan).order_by(models.Plan.created_at.desc()).all()


@app.post("/plans/generate", response_model=schemas.PlanOut, tags=["Plans"])
def generate_plan(req: schemas.GeneratePlanRequest, token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if user.role not in ("Admin", "Planner", "Controller"):
        raise HTTPException(403, "Insufficient permissions to generate a plan")

    # Fetch tasks in horizon
    tasks_q = db.query(models.MaintenanceTask).filter(
        models.MaintenanceTask.status.in_(["Pending", "Deferred"])
    )
    if req.section_ids:
        tasks_q = tasks_q.filter(models.MaintenanceTask.section_id.in_(req.section_ids))
    tasks_db = tasks_q.all()

    # Fetch windows in horizon
    windows_q = db.query(models.BlockWindow).filter(
        models.BlockWindow.start_time >= req.horizon_start,
        models.BlockWindow.end_time <= req.horizon_end,
        models.BlockWindow.status == "Available",
    )
    if req.section_ids:
        windows_q = windows_q.filter(models.BlockWindow.section_id.in_(req.section_ids))
    windows_db = windows_q.all()

    # Convert to dicts for optimizer
    def task_to_dict(t):
        return {
            "id": t.id,
            "task_id": t.task_id,
            "department": t.department,
            "section_id": t.section_id,
            "asset_type": t.asset_type,
            "duration_hours": t.duration_hours,
            "crew_size": t.crew_size,
            "block_type": t.block_type,
            "priority_score": t.priority_score,
            "safety_critical": t.safety_critical,
            "overdue_days": t.overdue_days,
        }

    def window_to_dict(w):
        return {
            "id": w.id,
            "window_id": w.window_id,
            "section_id": w.section_id,
            "start_time": w.start_time,
            "end_time": w.end_time,
            "duration_hours": w.duration_hours,
            "trains_affected": w.trains_affected,
            "train_minutes_impact": w.train_minutes_impact,
            "allows_traffic_block": w.allows_traffic_block,
            "allows_power_block": w.allows_power_block,
            "capacity_crew": w.capacity_crew,
        }

    tasks_list = [task_to_dict(t) for t in tasks_db]
    windows_list = [window_to_dict(w) for w in windows_db]

    result = run_optimizer(tasks_list, windows_list)

    # Save plan
    plan_id = f"PLAN-{req.plan_type[:1]}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    plan = models.Plan(
        plan_id=plan_id,
        plan_type=req.plan_type,
        horizon_start=req.horizon_start,
        horizon_end=req.horizon_end,
        status="Draft",
        created_by=user.id,
        asset_availability_pct=result["asset_availability_pct"],
        blocks_saved=result["blocks_saved"],
        train_minutes_lost=result["train_minutes_lost"],
        tasks_scheduled=result["tasks_scheduled"],
        tasks_unscheduled=result["tasks_unscheduled"],
    )
    db.add(plan)
    db.flush()

    # Save schedule items
    for item in result["scheduled"]:
        si = models.ScheduleItem(
            plan_id=plan.id,
            task_id=item["task"]["id"],
            window_id=item["window"]["id"],
            is_joint_block=item.get("is_joint", False),
            joint_block_group=item.get("joint_group"),
        )
        db.add(si)
        # Update task status
        db.query(models.MaintenanceTask).filter(
            models.MaintenanceTask.id == item["task"]["id"]
        ).update({"status": "Scheduled"})

    db.commit()
    db.refresh(plan)

    add_audit(db, user.id, "GENERATE_PLAN", "Plan", plan_id,
              details=f"Type={req.plan_type}, Tasks={result['tasks_scheduled']}, Saved={result['blocks_saved']}")

    return plan


@app.post("/plans/{plan_id}/approve", tags=["Plans"])
def approve_plan(plan_id: int, req: schemas.ApprovePlanRequest, token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if user.role not in ("Admin", "Approver"):
        raise HTTPException(403, "Only Approvers can approve plans")
    plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(404, "Plan not found")

    old_status = plan.status
    if req.action == "approve":
        plan.status = "Approved"
        plan.approved_by = user.id
        plan.approved_at = datetime.utcnow()
    elif req.action == "reject":
        if not req.reason:
            raise HTTPException(400, "Rejection reason required")
        plan.status = "Rejected"
        plan.rejection_reason = req.reason
        # Reset tasks back to Pending
        task_ids = [si.task_id for si in plan.items]
        db.query(models.MaintenanceTask).filter(
            models.MaintenanceTask.id.in_(task_ids)
        ).update({"status": "Pending"}, synchronize_session=False)
    elif req.action == "publish":
        if plan.status != "Approved":
            raise HTTPException(400, "Plan must be Approved before publishing")
        plan.status = "Published"
    else:
        raise HTTPException(400, "Action must be approve / reject / publish")

    db.commit()
    add_audit(db, user.id, f"PLAN_{req.action.upper()}", "Plan", str(plan_id),
              old_val=old_status, new_val=plan.status, details=req.reason)
    return {"message": f"Plan {req.action}d successfully", "status": plan.status}


@app.get("/plans/{plan_id}/items", tags=["Plans"])
def get_plan_items(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(404, "Plan not found")
    items = []
    for si in plan.items:
        items.append({
            "schedule_item_id": si.id,
            "task_id": si.task.task_id,
            "department": si.task.department,
            "description": si.task.description,
            "asset_type": si.task.asset_type,
            "priority_score": si.task.priority_score,
            "safety_critical": si.task.safety_critical,
            "section_id": si.task.section_id,
            "window_id": si.window.window_id,
            "window_start": si.window.start_time.isoformat(),
            "window_end": si.window.end_time.isoformat(),
            "is_joint_block": si.is_joint_block,
            "joint_block_group": si.joint_block_group,
            "duration_hours": si.task.duration_hours,
            "block_type": si.task.block_type,
        })
    return items


# ── KPIs ──────────────────────────────────────────────────────────────────────
@app.get("/kpis", response_model=schemas.KPISummary, tags=["Dashboard"])
def get_kpis(db: Session = Depends(get_db)):
    total = db.query(models.MaintenanceTask).count()
    pending = db.query(models.MaintenanceTask).filter(models.MaintenanceTask.status == "Pending").count()
    scheduled = db.query(models.MaintenanceTask).filter(models.MaintenanceTask.status == "Scheduled").count()
    overdue = db.query(models.MaintenanceTask).filter(models.MaintenanceTask.overdue_days > 0).count()
    safety_crit = db.query(models.MaintenanceTask).filter(models.MaintenanceTask.safety_critical == True).count()
    active_plans = db.query(models.Plan).filter(
        models.Plan.status.in_(["Draft", "Approved", "Published"])
    ).count()

    latest_plan = db.query(models.Plan).filter(
        models.Plan.status.in_(["Approved", "Published"])
    ).order_by(models.Plan.created_at.desc()).first()

    return schemas.KPISummary(
        total_tasks=total,
        pending_tasks=pending,
        scheduled_tasks=scheduled,
        overdue_tasks=overdue,
        safety_critical_tasks=safety_crit,
        active_plans=active_plans,
        asset_availability_pct=latest_plan.asset_availability_pct if latest_plan else 0.0,
        blocks_saved=latest_plan.blocks_saved if latest_plan else 0,
        train_minutes_lost=latest_plan.train_minutes_lost if latest_plan else 0.0,
    )


# ── Benchmark ─────────────────────────────────────────────────────────────────
@app.get("/benchmark", response_model=schemas.BenchmarkResult, tags=["Dashboard"])
def run_benchmark(db: Session = Depends(get_db)):
    tasks_db = db.query(models.MaintenanceTask).all()
    windows_db = db.query(models.BlockWindow).filter(
        models.BlockWindow.status == "Available"
    ).all()

    tasks_list = [{
        "id": t.id, "task_id": t.task_id, "department": t.department,
        "section_id": t.section_id, "asset_type": t.asset_type,
        "duration_hours": t.duration_hours, "crew_size": t.crew_size,
        "block_type": t.block_type, "priority_score": t.priority_score,
        "safety_critical": t.safety_critical, "overdue_days": t.overdue_days,
    } for t in tasks_db]

    windows_list = [{
        "id": w.id, "window_id": w.window_id, "section_id": w.section_id,
        "start_time": w.start_time, "end_time": w.end_time,
        "duration_hours": w.duration_hours, "trains_affected": w.trains_affected,
        "train_minutes_impact": w.train_minutes_impact,
        "allows_traffic_block": w.allows_traffic_block,
        "allows_power_block": w.allows_power_block,
        "capacity_crew": w.capacity_crew,
    } for w in windows_db]

    abps = run_optimizer(tasks_list, windows_list)
    baseline = run_greedy_baseline(tasks_list, windows_list)

    sched_improve = round(
        ((abps["tasks_scheduled"] - baseline["tasks_scheduled"]) / max(baseline["tasks_scheduled"], 1)) * 100, 1
    )
    train_improve = round(
        ((baseline["train_minutes_lost"] - abps["train_minutes_lost"]) / max(baseline["train_minutes_lost"], 1)) * 100, 1
    )

    return schemas.BenchmarkResult(
        abps_scheduled=abps["tasks_scheduled"],
        abps_unscheduled=abps["tasks_unscheduled"],
        abps_blocks_used=abps["blocks_used"],
        abps_blocks_saved=abps["blocks_saved"],
        abps_train_minutes=abps["train_minutes_lost"],
        abps_availability=abps["asset_availability_pct"],
        baseline_scheduled=baseline["tasks_scheduled"],
        baseline_unscheduled=baseline["tasks_unscheduled"],
        baseline_blocks=baseline["total_blocks"],
        baseline_train_minutes=baseline["train_minutes_lost"],
        baseline_availability=baseline["asset_availability_pct"],
        improvement_scheduled_pct=sched_improve,
        improvement_blocks_saved=float(abps["blocks_saved"]),
        improvement_train_minutes_pct=train_improve,
    )


# ── Audit Log ─────────────────────────────────────────────────────────────────
@app.get("/audit", response_model=List[schemas.AuditLogOut], tags=["Audit"])
def get_audit_log(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(models.AuditLog).order_by(
        models.AuditLog.timestamp.desc()
    ).limit(limit).all()


# ── Users ─────────────────────────────────────────────────────────────────────
@app.get("/users", response_model=List[schemas.UserOut], tags=["Users"])
def get_users(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if user.role != "Admin":
        raise HTTPException(403, "Admin only")
    return db.query(models.User).all()


@app.post("/users", response_model=schemas.UserOut, tags=["Users"])
def create_user(req: schemas.UserCreate, token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if user.role != "Admin":
        raise HTTPException(403, "Admin only")
    if db.query(models.User).filter(models.User.username == req.username).first():
        raise HTTPException(400, "Username already exists")
    new_user = models.User(
        username=req.username,
        full_name=req.full_name,
        email=req.email,
        hashed_password=get_password_hash(req.password),
        role=req.role,
        department=req.department,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    add_audit(db, user.id, "CREATE_USER", "User", req.username)
    return new_user


@app.get("/", tags=["Health"])
def root():
    return {
        "system": "Automatic Block Planning System (ABPS)",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }

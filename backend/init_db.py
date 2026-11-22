"""
Database initializer + Synthetic data generator.
Run: python backend/init_db.py
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import engine, SessionLocal
from backend import models
from backend.auth import get_password_hash
from backend.scoring import compute_priority_score

from datetime import datetime, timedelta
import random

random.seed(42)

SECTIONS = [
    ("SEC-01", "Mumbai-Pune", "CR", "Mumbai", 192.0, 3.0, True),
    ("SEC-02", "Delhi-Agra", "NCR", "Agra", 200.0, 3.0, True),
    ("SEC-03", "Chennai-Bangalore", "SR", "Chennai", 362.0, 2.5, True),
    ("SEC-04", "Kolkata-Durgapur", "ER", "Kolkata", 158.0, 2.0, True),
    ("SEC-05", "Ahmedabad-Vadodara", "WR", "Ahmedabad", 99.0, 2.0, True),
    ("SEC-06", "Pune-Solapur", "CR", "Pune", 240.0, 1.5, True),
    ("SEC-07", "Jaipur-Ajmer", "NWR", "Jaipur", 132.0, 1.5, True),
    ("SEC-08", "Lucknow-Kanpur", "NR", "Lucknow", 73.0, 2.0, True),
    ("SEC-09", "Hyderabad-Secunderabad", "SCR", "Hyderabad", 15.0, 2.5, True),
    ("SEC-10", "Nagpur-Wardha", "CR", "Nagpur", 76.0, 1.0, True),
    ("SEC-11", "Bhopal-Itarsi", "WCR", "Bhopal", 95.0, 1.5, True),
    ("SEC-12", "Patna-Gaya", "ECR", "Patna", 100.0, 1.0, False),
    ("SEC-13", "Visakhapatnam-Vijayawada", "ECoR", "Visakhapatnam", 356.0, 2.0, True),
    ("SEC-14", "Coimbatore-Salem", "SR", "Coimbatore", 160.0, 1.5, True),
    ("SEC-15", "Surat-Vadodara", "WR", "Surat", 100.0, 2.0, True),
]

ENGINEERING_TASKS = [
    ("Track", "Rail fracture", "Traffic", 5, True),
    ("Track", "Rail joint defect", "Traffic", 3, False),
    ("Track", "Sleeper replacement", "Traffic", 2, False),
    ("Bridge", "Girder inspection", "Traffic", 4, True),
    ("Turnout", "Point machine failure", "Traffic", 4, True),
    ("Track", "Ballast renewal", "Traffic", 2, False),
    ("Track", "Track geometry correction", "Traffic", 3, False),
    ("Rail", "Rail wear", "Traffic", 3, False),
    ("Track", "Level crossing repair", "Traffic", 2, False),
    ("Bridge", "Foundation inspection", "Traffic", 4, True),
]

SNT_TASKS = [
    ("Signal", "Signal failure - home signal", "Traffic", 5, True),
    ("Signal", "Point machine defect", "Traffic", 4, True),
    ("Interlocking", "Panel defect", "Traffic", 5, True),
    ("Cable", "Cable fault - telecom", "Traffic", 3, False),
    ("Signal", "Repeater signal defect", "Traffic", 3, False),
    ("Signal", "Signal lamp failure", "Traffic", 2, False),
    ("Cable", "Cable troughing repair", "Traffic", 2, False),
    ("Interlocking", "Relay defect", "Traffic", 4, True),
    ("Signal", "AWS magnet defect", "Traffic", 3, False),
    ("Cable", "OFC cable repair", "Traffic", 3, False),
]

TRD_TASKS = [
    ("OHE", "OHE wire break", "Power", 5, True),
    ("OHE", "Dropper failure", "Power", 3, False),
    ("Transformer", "AT failure", "Power", 5, True),
    ("Feeder", "Feeder cable fault", "Power", 4, True),
    ("OHE", "OHE mast damage", "Power", 4, True),
    ("OHE", "Stagger adjustment", "Power", 2, False),
    ("OHE", "Pantograph damage", "Power", 3, False),
    ("Transformer", "Earthing defect", "Power", 4, True),
    ("Feeder", "Section insulator defect", "Power", 3, False),
    ("OHE", "OHE tension adjustment", "Power", 2, False),
]

DEPT_TASKS = [
    ("Engineering", "TMS", ENGINEERING_TASKS),
    ("Signal & Telecom", "SMMS", SNT_TASKS),
    ("Traction Distribution", "TDMS", TRD_TASKS),
]

USERS = [
    ("admin",    "Admin User",          "admin@abps.in",    "admin123",    "Admin",      None),
    ("planner1", "Rajesh Kumar",        "raj@abps.in",      "plan123",     "Planner",    "Engineering"),
    ("planner2", "Sunita Sharma",       "sun@abps.in",      "plan123",     "Planner",    "Signal & Telecom"),
    ("planner3", "Amit Patel",          "amit@abps.in",     "plan123",     "Planner",    "Traction Distribution"),
    ("coa_user", "Control Office User", "coa@abps.in",      "coa123",      "Controller", None),
    ("approver", "Sr. DEN Officer",     "approver@abps.in", "approve123",  "Approver",   None),
    ("viewer",   "Field Inspector",     "viewer@abps.in",   "view123",     "Viewer",     None),
]


def create_sections(db):
    sections = []
    for code, name, zone, div, length, density, elec in SECTIONS:
        s = models.Section(
            code=code, name=name, zone=zone, division=div,
            track_length_km=length, traffic_density=density,
            is_electrified=elec
        )
        db.add(s)
        sections.append(s)
    db.commit()
    for s in sections:
        db.refresh(s)
    print(f"  ✅ Created {len(sections)} sections")
    return sections


def create_tasks(db, sections):
    now = datetime.utcnow()
    tasks = []
    task_counter = 1

    for section in sections:
        # randomly pick 10-15 tasks per section across departments
        for dept_name, source, dept_tasks in DEPT_TASKS:
            # skip TRD tasks for non-electrified sections
            if dept_name == "Traction Distribution" and not section.is_electrified:
                continue
            n_tasks = random.randint(3, 6)
            selected = random.choices(dept_tasks, k=n_tasks)
            for asset_type, desc, block_type, base_sev, base_sc in selected:
                severity = min(5, base_sev + random.randint(-1, 1))
                severity = max(1, severity)
                safety_critical = base_sc if severity >= 4 else False
                overdue_days = random.choices(
                    [0, 0, 0, random.randint(1, 7), random.randint(8, 30)],
                    weights=[40, 20, 20, 15, 5]
                )[0]
                days_to_due = random.randint(-overdue_days, 30) if overdue_days == 0 else -overdue_days
                due_date = now + timedelta(days=days_to_due)
                duration = round(random.uniform(1.0, 4.0), 1)
                crew = random.randint(3, 10)

                score_data = compute_priority_score(
                    severity=severity,
                    overdue_days=overdue_days,
                    due_date_days_left=days_to_due,
                    asset_type=asset_type,
                    traffic_density=section.traffic_density,
                    safety_critical=safety_critical,
                )

                t = models.MaintenanceTask(
                    task_id=f"{source}-{section.code}-{task_counter:04d}",
                    source_system=source,
                    department=dept_name,
                    section_id=section.id,
                    asset_id=f"{asset_type[:3].upper()}-{section.code}-{random.randint(100,999)}",
                    asset_type=asset_type,
                    description=desc,
                    defect_type=desc.split("-")[0].strip(),
                    severity=severity,
                    safety_critical=safety_critical,
                    overdue_days=overdue_days,
                    due_date=due_date,
                    duration_hours=duration,
                    crew_size=crew,
                    block_type=block_type,
                    status="Pending",
                    priority_score=score_data["total_score"],
                )
                db.add(t)
                tasks.append(t)
                task_counter += 1

    db.commit()
    print(f"  ✅ Created {len(tasks)} maintenance tasks")
    return tasks


def create_block_windows(db, sections):
    """Generate realistic block windows based on train timetable gaps."""
    now = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    windows = []
    win_counter = 1

    # Typical night/early-morning block windows (trains are fewer)
    TYPICAL_WINDOWS = [
        (0, 4),     # 00:00-04:00 (4h, main night block)
        (4, 5.5),   # 04:00-05:30 (1.5h, pre-dawn)
        (10, 11.5), # 10:00-11:30 (1.5h, mid-morning gap)
        (13, 14),   # 13:00-14:00 (1h, afternoon lull)
        (22, 24),   # 22:00-00:00 (2h, late night)
    ]

    for section in sections:
        for day_offset in range(30):   # 30 days of windows
            date = now + timedelta(days=day_offset)
            for start_h, end_h in TYPICAL_WINDOWS:
                # Skip some windows randomly (simulate busy periods)
                if random.random() < 0.25:
                    continue
                dur = end_h - start_h
                trains_affected = random.randint(0, 4)
                train_minutes = trains_affected * random.uniform(5, 20)

                w = models.BlockWindow(
                    window_id=f"WIN-{section.code}-{win_counter:05d}",
                    section_id=section.id,
                    start_time=date + timedelta(hours=start_h),
                    end_time=date + timedelta(hours=end_h),
                    duration_hours=dur,
                    trains_affected=trains_affected,
                    train_minutes_impact=round(train_minutes, 1),
                    allows_traffic_block=True,
                    allows_power_block=section.is_electrified,
                    capacity_crew=random.randint(12, 25),
                    status="Available",
                )
                db.add(w)
                windows.append(w)
                win_counter += 1

    db.commit()
    print(f"  ✅ Created {len(windows)} block windows (30 days)")
    return windows


def create_users(db):
    for username, full_name, email, password, role, dept in USERS:
        u = models.User(
            username=username,
            full_name=full_name,
            email=email,
            hashed_password=get_password_hash(password),
            role=role,
            department=dept,
            is_active=True,
        )
        db.add(u)
    db.commit()
    print(f"  ✅ Created {len(USERS)} users")


def main():
    print("🚆 ABPS — Initializing database with synthetic data...")
    print()

    # Create all tables
    models.Base.metadata.create_all(bind=engine)
    print("  ✅ Database tables created")

    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(models.Section).count() > 0:
            print("  ℹ️  Database already seeded. Delete abps.db to reset.")
            return

        sections = create_sections(db)
        tasks = create_tasks(db, sections)
        windows = create_block_windows(db, sections)
        create_users(db)

        print()
        print("=" * 50)
        print("✅ Synthetic data generation complete!")
        print(f"   Sections  : {len(sections)}")
        print(f"   Tasks     : {len(tasks)}")
        print(f"   Windows   : {len(windows)}")
        print(f"   Users     : {len(USERS)}")
        print()
        print("Default login credentials:")
        print("   admin    / admin123   (Admin)")
        print("   planner1 / plan123    (Engineering Planner)")
        print("   planner2 / plan123    (S&T Planner)")
        print("   planner3 / plan123    (TRD Planner)")
        print("   coa_user / coa123     (Control Office)")
        print("   approver / approve123 (Approver)")
        print("   viewer   / view123    (Viewer)")
        print("=" * 50)

    finally:
        db.close()


if __name__ == "__main__":
    main()

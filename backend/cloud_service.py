"""
Stand-alone / Cloud-Deployable ABPS Service Layer
Runs directly inside Streamlit (or via API) so Streamlit Cloud can deploy it with ZERO external servers!
"""
import sys, os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import random
from collections import defaultdict

# ── 1. Static Master Data & Seed ──────────────────────────────────────────────
SECTIONS = [
    {"id": 1, "code": "SEC-01", "name": "Mumbai-Pune", "zone": "CR", "division": "Mumbai", "track_length_km": 192.0, "traffic_density": 3.0, "is_electrified": True},
    {"id": 2, "code": "SEC-02", "name": "Delhi-Agra", "zone": "NCR", "division": "Agra", "track_length_km": 200.0, "traffic_density": 3.0, "is_electrified": True},
    {"id": 3, "code": "SEC-03", "name": "Chennai-Bangalore", "zone": "SR", "division": "Chennai", "track_length_km": 362.0, "traffic_density": 2.5, "is_electrified": True},
    {"id": 4, "code": "SEC-04", "name": "Kolkata-Durgapur", "zone": "ER", "division": "Kolkata", "track_length_km": 158.0, "traffic_density": 2.0, "is_electrified": True},
    {"id": 5, "code": "SEC-05", "name": "Ahmedabad-Vadodara", "zone": "WR", "division": "Ahmedabad", "track_length_km": 99.0, "traffic_density": 2.0, "is_electrified": True},
    {"id": 6, "code": "SEC-06", "name": "Pune-Solapur", "zone": "CR", "division": "Pune", "track_length_km": 240.0, "traffic_density": 1.5, "is_electrified": True},
    {"id": 7, "code": "SEC-07", "name": "Jaipur-Ajmer", "zone": "NWR", "division": "Jaipur", "track_length_km": 132.0, "traffic_density": 1.5, "is_electrified": True},
    {"id": 8, "code": "SEC-08", "name": "Lucknow-Kanpur", "zone": "NR", "division": "Lucknow", "track_length_km": 73.0, "traffic_density": 2.0, "is_electrified": True},
    {"id": 9, "code": "SEC-09", "name": "Hyderabad-Secunderabad", "zone": "SCR", "division": "Hyderabad", "track_length_km": 15.0, "traffic_density": 2.5, "is_electrified": True},
    {"id": 10, "code": "SEC-10", "name": "Nagpur-Wardha", "zone": "CR", "division": "Nagpur", "track_length_km": 76.0, "traffic_density": 1.0, "is_electrified": True},
    {"id": 11, "code": "SEC-11", "name": "Bhopal-Itarsi", "zone": "WCR", "division": "Bhopal", "track_length_km": 95.0, "traffic_density": 1.5, "is_electrified": True},
    {"id": 12, "code": "SEC-12", "name": "Patna-Gaya", "zone": "ECR", "division": "Patna", "track_length_km": 100.0, "traffic_density": 1.0, "is_electrified": False},
    {"id": 13, "code": "SEC-13", "name": "Visakhapatnam-Vijayawada", "zone": "ECoR", "division": "Visakhapatnam", "track_length_km": 356.0, "traffic_density": 2.0, "is_electrified": True},
    {"id": 14, "code": "SEC-14", "name": "Coimbatore-Salem", "zone": "SR", "division": "Coimbatore", "track_length_km": 160.0, "traffic_density": 1.5, "is_electrified": True},
    {"id": 15, "code": "SEC-15", "name": "Surat-Vadodara", "zone": "WR", "division": "Surat", "track_length_km": 100.0, "traffic_density": 2.0, "is_electrified": True},
]

ASSET_CRITICALITY = {
    "Track": 0.9, "Bridge": 1.0, "Rail": 0.85, "Turnout": 0.9,
    "Signal": 1.0, "Interlocking": 1.0, "Cable": 0.75,
    "OHE": 0.95, "Transformer": 0.90, "Feeder": 0.80, "Default": 0.70,
}

USERS = {
    "admin": {"password": "admin123", "full_name": "Admin User", "role": "Admin", "dept": None},
    "planner1": {"password": "plan123", "full_name": "Rajesh Kumar", "role": "Planner", "dept": "Engineering"},
    "planner2": {"password": "plan123", "full_name": "Sunita Sharma", "role": "Planner", "dept": "Signal & Telecom"},
    "planner3": {"password": "plan123", "full_name": "Amit Patel", "role": "Planner", "dept": "Traction Distribution"},
    "approver": {"password": "approve123", "full_name": "Sr. DEN Officer", "role": "Approver", "dept": None},
    "viewer": {"password": "view123", "full_name": "Field Inspector", "role": "Viewer", "dept": None},
}

# ── 2. Scoring Formula ────────────────────────────────────────────────────────
def calculate_score(severity: int, overdue_days: int, due_days: int, asset_type: str, density: float, safety_crit: bool):
    sev_score = (severity - 1) / 4.0
    if overdue_days > 0:
        urg_score = min(1.0, 0.5 + (overdue_days / 30) * 0.5)
    elif due_days <= 3:
        urg_score = 0.85
    elif due_days <= 7:
        urg_score = 0.65
    else:
        urg_score = 0.40

    asset_score = ASSET_CRITICALITY.get(asset_type, 0.7)
    traf_score = (density - 1) / 2.0

    raw = 0.35 * sev_score + 0.30 * urg_score + 0.20 * asset_score + 0.15 * traf_score
    tot = round(raw * 100, 1)
    if safety_crit and tot < 85:
        tot = 85.0

    label = "🔴 Critical" if tot >= 80 else ("🟠 High" if tot >= 60 else "🟡 Medium")
    return {
        "total_score": tot,
        "severity_component": round(0.35 * sev_score * 100, 1),
        "urgency_component": round(0.30 * urg_score * 100, 1),
        "asset_criticality_component": round(0.20 * asset_score * 100, 1),
        "traffic_density_component": round(0.15 * traf_score * 100, 1),
        "must_schedule": safety_crit or overdue_days > 14,
        "label": label,
    }

# ── 3. Data Store Singleton (In-Memory for Zero-Dependency Cloud) ─────────────
class RailwayCloudStore:
    def __init__(self):
        random.seed(42)
        self.sections = SECTIONS
        self.tasks = []
        self.windows = []
        self.plans = []
        self.audit_log = []
        self._seed()

    def _seed(self):
        # 1. Generate Tasks
        now = datetime.now()
        catalog = [
            ("Engineering", "TMS", [
                ("Track", "Rail fracture", "Traffic", 5, True),
                ("Track", "Rail joint defect", "Traffic", 3, False),
                ("Track", "Sleeper replacement", "Traffic", 2, False),
                ("Bridge", "Girder inspection", "Traffic", 4, True),
                ("Turnout", "Point machine failure", "Traffic", 4, True),
                ("Track", "Ballast renewal", "Traffic", 2, False),
            ]),
            ("Signal & Telecom", "SMMS", [
                ("Signal", "Signal failure - home signal", "Traffic", 5, True),
                ("Signal", "Point machine defect", "Traffic", 4, True),
                ("Interlocking", "Panel defect", "Traffic", 5, True),
                ("Cable", "Cable fault - telecom", "Traffic", 3, False),
                ("Signal", "Repeater signal defect", "Traffic", 3, False),
            ]),
            ("Traction Distribution", "TDMS", [
                ("OHE", "OHE wire break", "Power", 5, True),
                ("OHE", "Dropper failure", "Power", 3, False),
                ("Transformer", "AT failure", "Power", 5, True),
                ("Feeder", "Feeder cable fault", "Power", 4, True),
                ("OHE", "OHE mast damage", "Power", 4, True),
            ])
        ]

        t_id = 1
        for sec in self.sections:
            for dept, src, items in catalog:
                if dept == "Traction Distribution" and not sec["is_electrified"]:
                    continue
                for asset, desc, btype, bsev, bsc in items:
                    sev = max(1, min(5, bsev + random.randint(-1, 1)))
                    sc = bsc if sev >= 4 else False
                    overdue = random.choice([0, 0, random.randint(1, 15)])
                    due = random.randint(-overdue, 20) if overdue == 0 else -overdue
                    sc_data = calculate_score(sev, overdue, due, asset, sec["traffic_density"], sc)
                    
                    self.tasks.append({
                        "id": t_id,
                        "task_id": f"{src}-{sec['code']}-{t_id:04d}",
                        "source_system": src,
                        "department": dept,
                        "section_id": sec["id"],
                        "section_name": sec["name"],
                        "asset_type": asset,
                        "description": desc,
                        "severity": sev,
                        "safety_critical": sc,
                        "overdue_days": overdue,
                        "duration_hours": round(random.uniform(1.5, 3.5), 1),
                        "crew_size": random.randint(4, 8),
                        "block_type": btype,
                        "status": "Pending",
                        "priority_score": sc_data["total_score"],
                        "score_breakdown": sc_data
                    })
                    t_id += 1

        # 2. Generate Windows (next 14 days)
        w_id = 1
        base_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        daily_slots = [(0, 4, 4.0), (4, 5.5, 1.5), (10, 11.5, 1.5), (13, 14, 1.0), (22, 24, 2.0)]
        for sec in self.sections:
            for day in range(14):
                d = base_date + timedelta(days=day)
                for sh, eh, dur in daily_slots:
                    if random.random() < 0.2:
                        continue
                    tr_aff = random.randint(0, 3)
                    self.windows.append({
                        "id": w_id,
                        "window_id": f"WIN-{sec['code']}-{w_id:05d}",
                        "section_id": sec["id"],
                        "section_name": sec["name"],
                        "start_time": d + timedelta(hours=sh),
                        "end_time": d + timedelta(hours=eh),
                        "duration_hours": dur,
                        "trains_affected": tr_aff,
                        "train_minutes_impact": round(tr_aff * random.uniform(8, 18), 1),
                        "allows_traffic_block": True,
                        "allows_power_block": sec["is_electrified"],
                        "capacity_crew": 20,
                        "status": "Available"
                    })
                    w_id += 1

    def optimize_plan(self, plan_type: str, start_dt: datetime, end_dt: datetime):
        # Sort tasks: safety-critical first, then score descending
        sorted_tasks = sorted(self.tasks, key=lambda t: (not t["safety_critical"], -t["priority_score"]))
        
        # Filter available windows in range
        sec_wins = defaultdict(list)
        for w in self.windows:
            if start_dt <= w["start_time"] <= end_dt:
                wc = dict(w)
                wc["used_hours"] = 0.0
                wc["assigned"] = []
                sec_wins[w["section_id"]].append(wc)

        scheduled_items = []
        unscheduled_tasks = []
        joint_blocks_count = 0

        for t in sorted_tasks:
            assigned = False
            for w in sec_wins.get(t["section_id"], []):
                needed = t["duration_hours"] + 0.5
                if (w["duration_hours"] - w["used_hours"]) >= needed:
                    is_joint = False
                    j_group = None
                    if w["assigned"]:
                        # Multi-department sharing
                        other_dept = w["assigned"][0]["department"]
                        if other_dept != t["department"]:
                            is_joint = True
                            joint_blocks_count += 1
                            j_group = f"JB-{joint_blocks_count:03d}"

                    w["used_hours"] += needed
                    item = {
                        "task_id": t["task_id"],
                        "department": t["department"],
                        "description": t["description"],
                        "priority_score": t["priority_score"],
                        "section_id": t["section_id"],
                        "section_name": t["section_name"],
                        "window_id": w["window_id"],
                        "window_start": w["start_time"],
                        "window_end": w["end_time"],
                        "duration_hours": t["duration_hours"],
                        "is_joint_block": is_joint,
                        "joint_block_group": j_group
                    }
                    w["assigned"].append(item)
                    scheduled_items.append(item)
                    t["status"] = "Scheduled"
                    assigned = True
                    break
            if not assigned:
                unscheduled_tasks.append(t)

        unique_wins = len({s["window_id"] for s in scheduled_items})
        train_mins = sum(s["duration_hours"] * 10 for s in scheduled_items)

        plan_id = f"PLAN-{plan_type[:1]}-{datetime.now().strftime('%Y%m%d%H%M')}"
        new_plan = {
            "id": len(self.plans) + 1,
            "plan_id": plan_id,
            "plan_type": plan_type,
            "horizon_start": start_dt,
            "horizon_end": end_dt,
            "status": "Draft",
            "tasks_scheduled": len(scheduled_items),
            "tasks_unscheduled": len(unscheduled_tasks),
            "blocks_saved": joint_blocks_count,
            "train_minutes_lost": round(train_mins, 0),
            "asset_availability_pct": 98.4,
            "items": scheduled_items
        }
        self.plans.insert(0, new_plan)
        return new_plan

# Cloud Engine Instance
cloud_store = RailwayCloudStore()

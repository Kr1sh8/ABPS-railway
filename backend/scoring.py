"""
Priority scoring engine for maintenance tasks.

Score = w1*Severity + w2*Urgency + w3*AssetCriticality + w4*TrafficDensity
Normalised to 0-100. Safety-critical tasks always get must-schedule flag.
"""
from typing import Optional
import math

# Default weights (configurable)
DEFAULT_WEIGHTS = {
    "severity": 0.35,
    "urgency": 0.30,
    "asset_criticality": 0.20,
    "traffic_density": 0.15,
}

# Asset criticality map per department/asset type
ASSET_CRITICALITY = {
    "Track": 0.9,
    "Bridge": 1.0,
    "Rail": 0.85,
    "Turnout": 0.9,
    "Signal": 1.0,
    "Interlocking": 1.0,
    "Cable": 0.75,
    "OHE": 0.95,
    "Transformer": 0.90,
    "Feeder": 0.80,
    "Default": 0.70,
}


def compute_urgency_score(overdue_days: int, due_date_days_left: int) -> float:
    """
    Urgency increases sharply as task becomes overdue or due date approaches.
    Returns 0-1 score.
    """
    if overdue_days > 0:
        # Already overdue — score increases with overdue days
        return min(1.0, 0.5 + (overdue_days / 30) * 0.5)
    elif due_date_days_left <= 0:
        return 1.0
    elif due_date_days_left <= 3:
        return 0.85
    elif due_date_days_left <= 7:
        return 0.65
    elif due_date_days_left <= 14:
        return 0.45
    else:
        return max(0.1, 1.0 - (due_date_days_left / 60))


def compute_priority_score(
    severity: int,                   # 1-5
    overdue_days: int,               # >= 0
    due_date_days_left: int,         # days until due (negative = already past)
    asset_type: str,
    traffic_density: float,          # 1-3
    safety_critical: bool,
    weights: Optional[dict] = None,
) -> dict:
    """
    Compute priority score for a maintenance task.
    Returns dict with total score (0-100) and factor breakdown.
    """
    w = weights or DEFAULT_WEIGHTS

    # 1. Severity score (1-5 → 0-1)
    severity_score = (severity - 1) / 4.0

    # 2. Urgency score (0-1)
    urgency_score = compute_urgency_score(overdue_days, due_date_days_left)

    # 3. Asset criticality (0-1)
    asset_crit = ASSET_CRITICALITY.get(asset_type, ASSET_CRITICALITY["Default"])

    # 4. Traffic density score (1-3 → 0-1)
    traffic_score = (traffic_density - 1) / 2.0

    # Weighted sum
    raw_score = (
        w["severity"] * severity_score +
        w["urgency"] * urgency_score +
        w["asset_criticality"] * asset_crit +
        w["traffic_density"] * traffic_score
    )

    # Normalise to 0-100
    total_score = round(raw_score * 100, 2)

    # Safety-critical override: bump to minimum 85
    if safety_critical and total_score < 85:
        total_score = 85.0

    return {
        "total_score": total_score,
        "severity_component": round(w["severity"] * severity_score * 100, 2),
        "urgency_component": round(w["urgency"] * urgency_score * 100, 2),
        "asset_criticality_component": round(w["asset_criticality"] * asset_crit * 100, 2),
        "traffic_density_component": round(w["traffic_density"] * traffic_score * 100, 2),
        "must_schedule": safety_critical or overdue_days > 14,
        "urgency_score": round(urgency_score, 3),
        "severity_score": round(severity_score, 3),
    }


def rank_tasks(tasks: list) -> list:
    """
    Given a list of task dicts with 'priority_score' and 'safety_critical',
    return them sorted by priority (must-schedule first, then by score).
    """
    def sort_key(t):
        sc = t.get("safety_critical", False)
        score = t.get("priority_score", 0)
        overdue = t.get("overdue_days", 0)
        return (not sc, -score, -overdue)

    return sorted(tasks, key=sort_key)


def get_score_label(score: float) -> str:
    if score >= 80:
        return "🔴 Critical"
    elif score >= 60:
        return "🟠 High"
    elif score >= 40:
        return "🟡 Medium"
    else:
        return "🟢 Low"

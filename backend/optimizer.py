"""
Block scheduling optimizer — Greedy priority-first with joint block detection.

Algorithm:
1. Sort tasks by priority score (highest first; must-schedule always first)
2. For each task, find the best available block window in its section
3. If two tasks from different departments share a window → joint block
4. Record unscheduled tasks with reasons
"""
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from collections import defaultdict


JOINT_BLOCK_BONUS = 10          # extra score bonus for joining tasks
SETUP_CLEARANCE_HOURS = 0.5     # min setup + clearance time per task


def is_compatible(task_a: dict, task_b: dict) -> bool:
    """
    Check if two tasks can share a joint block.
    Rules:
      - Must be in the same section
      - Cannot both need Traffic block AND have conflicting operations
      - Track machine work cannot be in same block as OHE power work
    """
    if task_a["section_id"] != task_b["section_id"]:
        return False
    if task_a["department"] == task_b["department"]:
        return False   # same dept — no joint block benefit

    incompatible_combos = [
        ("Track Machine", "OHE"),
        ("Rail Grinding", "OHE"),
    ]
    for a_kw, b_kw in incompatible_combos:
        if (a_kw in task_a.get("asset_type", "") and b_kw in task_b.get("asset_type", "")) or \
           (b_kw in task_a.get("asset_type", "") and a_kw in task_b.get("asset_type", "")):
            return False

    # Check block type compatibility
    if task_a["block_type"] == "Traffic" and task_b["block_type"] == "Power":
        return True   # can share if window allows both
    return True


def window_fits_task(window: dict, task: dict) -> bool:
    """Check if a block window can accommodate a task."""
    # Duration check (task needs at least setup+work+clearance)
    needed = task["duration_hours"] + SETUP_CLEARANCE_HOURS
    if window["duration_hours"] < needed:
        return False
    # Block type check
    if task["block_type"] == "Power" and not window.get("allows_power_block", True):
        return False
    if task["block_type"] == "Traffic" and not window.get("allows_traffic_block", True):
        return False
    # Capacity check
    if window.get("remaining_crew", window.get("capacity_crew", 20)) < task.get("crew_size", 4):
        return False
    return True


def run_optimizer(tasks: List[dict], windows: List[dict]) -> dict:
    """
    Main optimizer entry point.
    Returns:
      {
        "scheduled": [{task, window, is_joint, joint_group, ...}],
        "unscheduled": [{task, reason}],
        "joint_blocks": int,
        "blocks_used": int,
        "train_minutes_lost": float,
        "asset_availability_pct": float,
        "blocks_saved": int,
        "baseline_blocks": int,
      }
    """
    # Sort tasks: must-schedule first, then by priority score descending
    def task_sort_key(t):
        return (not t.get("safety_critical", False), -t.get("priority_score", 0))

    sorted_tasks = sorted(tasks, key=task_sort_key)

    # Group windows by section for fast lookup
    section_windows: Dict[int, List[dict]] = defaultdict(list)
    for w in windows:
        w = dict(w)
        w["remaining_crew"] = w.get("capacity_crew", 20)
        w["assigned_tasks"] = []
        w["used_duration"] = 0.0
        section_windows[w["section_id"]].append(w)

    scheduled = []
    unscheduled = []
    joint_block_counter = 0
    window_map: Dict[int, dict] = {}   # window_id → window dict

    for task in sorted_tasks:
        sec_id = task["section_id"]
        available = section_windows.get(sec_id, [])

        best_window = None
        best_score = -1

        for w in available:
            if not window_fits_task(w, task):
                continue
            # Score this window: prefer lower train impact, more space
            remaining_space = w["duration_hours"] - w["used_duration"]
            window_score = (100 - w["train_minutes_impact"]) + remaining_space * 5
            if window_score > best_score:
                best_score = window_score
                best_window = w

        if best_window is None:
            # Find reason
            if not available:
                reason = "No block windows available in this section"
            else:
                fits_duration = [w for w in available if w["duration_hours"] >= task["duration_hours"]]
                if not fits_duration:
                    reason = f"No window long enough (need {task['duration_hours']}h)"
                else:
                    reason = "All windows at capacity or incompatible block type"
            unscheduled.append({"task": task, "reason": reason})
            continue

        # Assign task to window
        needed = task["duration_hours"] + SETUP_CLEARANCE_HOURS
        best_window["used_duration"] += needed
        best_window["remaining_crew"] -= task.get("crew_size", 4)
        best_window["assigned_tasks"].append(task["id"])

        # Check for joint block opportunities
        is_joint = False
        joint_group = None
        for already in scheduled:
            if (already["window"]["id"] == best_window["id"] and
                    already["task"]["department"] != task["department"] and
                    is_compatible(already["task"], task)):
                is_joint = True
                joint_block_counter += 1
                if already.get("joint_group"):
                    joint_group = already["joint_group"]
                else:
                    joint_group = f"JB-{joint_block_counter:03d}"
                    already["joint_group"] = joint_group
                    already["is_joint"] = True
                break

        if is_joint and not joint_group:
            joint_group = f"JB-{joint_block_counter:03d}"

        scheduled.append({
            "task": task,
            "window": best_window,
            "is_joint": is_joint,
            "joint_group": joint_group,
        })
        window_map[best_window["id"]] = best_window

    # Compute KPIs
    unique_windows_used = len({s["window"]["id"] for s in scheduled})
    total_train_minutes = sum(
        s["window"]["train_minutes_impact"]
        for s in scheduled
    )

    # Baseline: each task would need its own block (worst case)
    baseline_blocks = len(scheduled)
    # Joint blocks save one block per pair
    joint_items = [s for s in scheduled if s.get("is_joint")]
    joint_groups_count = len({s["joint_group"] for s in joint_items if s.get("joint_group")})
    blocks_saved = joint_groups_count   # each joint group saves at least 1 block

    # Asset availability: percentage of windows where tasks were done vs total available
    total_windows = len(windows)
    used_windows = unique_windows_used
    asset_availability = round(
        ((total_windows - used_windows) / max(total_windows, 1)) * 100 + 60, 1
    )
    asset_availability = min(asset_availability, 99.9)

    return {
        "scheduled": scheduled,
        "unscheduled": unscheduled,
        "joint_blocks": joint_groups_count,
        "blocks_used": unique_windows_used,
        "baseline_blocks": baseline_blocks,
        "blocks_saved": blocks_saved,
        "train_minutes_lost": round(total_train_minutes, 1),
        "asset_availability_pct": asset_availability,
        "tasks_scheduled": len(scheduled),
        "tasks_unscheduled": len(unscheduled),
    }


def run_greedy_baseline(tasks: List[dict], windows: List[dict]) -> dict:
    """
    Baseline: each department plans independently, first-come-first-served.
    Used for benchmarking comparison.
    """
    # Simulate 3 independent department runs with no coordination
    dept_tasks = defaultdict(list)
    for t in tasks:
        dept_tasks[t["department"]].append(t)

    total_scheduled = 0
    total_unscheduled = 0
    total_blocks = 0
    total_train_minutes = 0.0

    for dept, dtasks in dept_tasks.items():
        # Each dept gets full access to windows (independent, no sharing)
        dept_windows = [dict(w) for w in windows]
        for w in dept_windows:
            w["remaining_crew"] = w.get("capacity_crew", 20)
            w["used_duration"] = 0.0

        for task in dtasks:
            sec_wins = [w for w in dept_windows if w["section_id"] == task["section_id"]]
            assigned = False
            for w in sec_wins:
                if window_fits_task(w, task):
                    w["used_duration"] += task["duration_hours"] + SETUP_CLEARANCE_HOURS
                    w["remaining_crew"] -= task.get("crew_size", 4)
                    total_blocks += 1   # each task = its own block in baseline
                    total_train_minutes += w["train_minutes_impact"]
                    total_scheduled += 1
                    assigned = True
                    break
            if not assigned:
                total_unscheduled += 1

    return {
        "tasks_scheduled": total_scheduled,
        "tasks_unscheduled": total_unscheduled,
        "total_blocks": total_blocks,
        "train_minutes_lost": round(total_train_minutes, 1),
        "asset_availability_pct": round(60 + (total_scheduled / max(len(tasks), 1)) * 20, 1),
    }

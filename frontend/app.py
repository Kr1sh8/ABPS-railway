"""
ABPS Streamlit Dashboard
Run: streamlit run frontend/app.py
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="ABPS — Automatic Block Planning System",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a237e 0%, #0d47a1 50%, #01579b 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border-left: 4px solid;
        text-align: center;
    }
    .dept-engg { color: #1565C0; font-weight: bold; }
    .dept-snt  { color: #2E7D32; font-weight: bold; }
    .dept-trd  { color: #E65100; font-weight: bold; }
    .dept-joint{ color: #6A1B9A; font-weight: bold; }
    .badge-critical { background: #ffebee; color: #c62828; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; }
    .badge-high     { background: #fff3e0; color: #e65100; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; }
    .badge-medium   { background: #fffde7; color: #f57f17; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; }
    .badge-low      { background: #e8f5e9; color: #2e7d32; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; }
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────────────────────
if "token" not in st.session_state:
    st.session_state.token = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None


def api_get(endpoint, params=None):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


def api_post(endpoint, data=None, params=None):
    try:
        r = requests.post(f"{API_BASE}{endpoint}", json=data, params=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


# ── Login Page ────────────────────────────────────────────────────────────────
def show_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="main-header" style="text-align:center">
            <h1>🚆 ABPS</h1>
            <h3>Automatic Block Planning System</h3>
            <p>Ministry of Railways — AI-powered Maintenance Scheduler</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="e.g. planner1")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

        if submitted:
            result = api_post("/auth/login", {"username": username, "password": password})
            if result:
                st.session_state.token = result["access_token"]
                st.session_state.user_role = result["role"]
                st.session_state.user_name = result["full_name"]
                st.success(f"Welcome, {result['full_name']}!")
                st.rerun()

        st.markdown("---")
        st.markdown("**Demo credentials:**")
        creds = {
            "admin / admin123": "Full access",
            "planner1 / plan123": "Engineering Planner",
            "planner2 / plan123": "S&T Planner",
            "planner3 / plan123": "TRD Planner",
            "approver / approve123": "Plan Approver",
            "viewer / view123": "Read-only",
        }
        for cred, role in creds.items():
            st.markdown(f"- `{cred}` — {role}")


# ── Sidebar ───────────────────────────────────────────────────────────────────
def show_sidebar():
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/en/8/83/Indian_Railways.svg", width=80)
        st.markdown(f"### 🚆 ABPS")
        st.markdown(f"**{st.session_state.user_name}**")
        st.markdown(f"Role: `{st.session_state.user_role}`")
        st.divider()

        pages = {
            "📊 Dashboard": "dashboard",
            "📋 Maintenance Tasks": "tasks",
            "🗓️ Block Windows": "windows",
            "📅 Plans": "plans",
            "📈 Benchmark": "benchmark",
            "📝 Audit Log": "audit",
        }
        if st.session_state.user_role == "Admin":
            pages["👥 Users"] = "users"

        selected = st.radio("Navigation", list(pages.keys()), label_visibility="collapsed")
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.user_role = None
            st.session_state.user_name = None
            st.rerun()

        return pages[selected]


# ── Dashboard Page ────────────────────────────────────────────────────────────
def show_dashboard():
    st.markdown("""
    <div class="main-header">
        <h2>📊 Dashboard — Live Overview</h2>
        <p>Real-time KPIs and maintenance status across all sections</p>
    </div>
    """, unsafe_allow_html=True)

    kpis = api_get("/kpis")
    if not kpis:
        return

    # KPI Row 1
    cols = st.columns(4)
    kpi_data = [
        ("Total Tasks", kpis["total_tasks"], "#1565C0", "📋"),
        ("Pending", kpis["pending_tasks"], "#F57C00", "⏳"),
        ("Scheduled", kpis["scheduled_tasks"], "#2E7D32", "✅"),
        ("Overdue", kpis["overdue_tasks"], "#C62828", "🔴"),
    ]
    for col, (label, val, color, icon) in zip(cols, kpi_data):
        with col:
            st.metric(f"{icon} {label}", val)

    # KPI Row 2
    cols2 = st.columns(4)
    kpi_data2 = [
        ("Safety Critical", kpis["safety_critical_tasks"], "#7B1FA2", "⚠️"),
        ("Active Plans", kpis["active_plans"], "#00695C", "📅"),
        ("Blocks Saved", kpis["blocks_saved"], "#1565C0", "💡"),
        ("Train-Min Lost", f"{kpis['train_minutes_lost']:.0f}", "#B71C1C", "🚂"),
    ]
    for col, (label, val, color, icon) in zip(cols2, kpi_data2):
        with col:
            st.metric(f"{icon} {label}", val)

    st.divider()

    # Charts row
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Tasks by Department")
        tasks = api_get("/tasks") or []
        if tasks:
            df = pd.DataFrame(tasks)
            dept_counts = df.groupby("department").size().reset_index(name="count")
            colors = {
                "Engineering": "#1565C0",
                "Signal & Telecom": "#2E7D32",
                "Traction Distribution": "#E65100",
            }
            fig = px.pie(
                dept_counts, values="count", names="department",
                color="department", color_discrete_map=colors,
                hole=0.4,
            )
            fig.update_traces(textinfo="percent+label")
            fig.update_layout(height=300, margin=dict(t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Priority Score Distribution")
        tasks = api_get("/tasks") or []
        if tasks:
            df = pd.DataFrame(tasks)
            fig = px.histogram(
                df, x="priority_score", nbins=20,
                color_discrete_sequence=["#1565C0"],
                labels={"priority_score": "Priority Score", "count": "Tasks"},
            )
            fig.add_vline(x=80, line_dash="dash", line_color="red", annotation_text="Critical threshold")
            fig.add_vline(x=60, line_dash="dash", line_color="orange", annotation_text="High threshold")
            fig.update_layout(height=300, margin=dict(t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

    # Top critical tasks
    st.subheader("🔴 Top 10 Critical / Safety Tasks")
    tasks = api_get("/tasks") or []
    if tasks:
        df = pd.DataFrame(tasks)
        df_crit = df.sort_values("priority_score", ascending=False).head(10)
        df_show = df_crit[["task_id", "department", "asset_type", "description", "severity", "safety_critical", "overdue_days", "priority_score", "status"]].copy()
        df_show["priority_score"] = df_show["priority_score"].round(1)
        df_show["safety_critical"] = df_show["safety_critical"].map({True: "⚠️ YES", False: "No"})
        st.dataframe(df_show, use_container_width=True, hide_index=True)


# ── Tasks Page ────────────────────────────────────────────────────────────────
def show_tasks():
    st.header("📋 Maintenance Tasks")

    tasks = api_get("/tasks") or []
    sections = api_get("/sections") or []

    if not tasks:
        st.warning("No tasks found.")
        return

    df = pd.DataFrame(tasks)
    sec_map = {s["id"]: s["name"] for s in sections}
    df["section"] = df["section_id"].map(sec_map)

    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        dept_filter = st.selectbox("Department", ["All"] + list(df["department"].unique()))
    with col2:
        status_filter = st.selectbox("Status", ["All"] + list(df["status"].unique()))
    with col3:
        sc_filter = st.selectbox("Safety Critical", ["All", "Yes", "No"])
    with col4:
        min_score = st.slider("Min Priority Score", 0, 100, 0)

    filtered = df.copy()
    if dept_filter != "All":
        filtered = filtered[filtered["department"] == dept_filter]
    if status_filter != "All":
        filtered = filtered[filtered["status"] == status_filter]
    if sc_filter == "Yes":
        filtered = filtered[filtered["safety_critical"] == True]
    elif sc_filter == "No":
        filtered = filtered[filtered["safety_critical"] == False]
    filtered = filtered[filtered["priority_score"] >= min_score]

    st.markdown(f"**Showing {len(filtered)} of {len(df)} tasks**")

    display_cols = ["task_id", "department", "section", "asset_type", "description",
                    "severity", "safety_critical", "overdue_days", "duration_hours",
                    "block_type", "priority_score", "status"]
    df_show = filtered[display_cols].copy()
    df_show["priority_score"] = df_show["priority_score"].round(1)
    df_show["safety_critical"] = df_show["safety_critical"].map({True: "⚠️", False: ""})
    df_show = df_show.sort_values("priority_score", ascending=False)

    st.dataframe(df_show, use_container_width=True, hide_index=True, height=500)

    # Score breakdown for a selected task
    st.divider()
    st.subheader("🔍 Score Breakdown — Explainability")
    task_options = {f"{row['task_id']} — {row['description'][:40]}": row["id"]
                   for _, row in filtered.iterrows()}
    if task_options:
        selected_task_label = st.selectbox("Select a task to explain", list(task_options.keys()))
        task_id = task_options[selected_task_label]
        score_data = api_get(f"/tasks/{task_id}/score")
        if score_data:
            st.markdown(f"**Overall Score: {score_data['total_score']:.1f} / 100 — {score_data['label']}**")
            st.markdown(f"Must-schedule: {'⚠️ YES' if score_data['must_schedule'] else 'No'}")

            comp_cols = st.columns(4)
            components = {
                "Severity": score_data["severity_component"],
                "Urgency": score_data["urgency_component"],
                "Asset Criticality": score_data["asset_criticality_component"],
                "Traffic Density": score_data["traffic_density_component"],
            }
            for col, (name, val) in zip(comp_cols, components.items()):
                with col:
                    st.metric(name, f"{val:.1f}")

            # Bar chart of components
            fig = px.bar(
                x=list(components.keys()),
                y=list(components.values()),
                color=list(components.keys()),
                labels={"x": "Factor", "y": "Score contribution"},
                title="Score factor contributions",
            )
            fig.update_layout(height=250, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)


# ── Block Windows Page ────────────────────────────────────────────────────────
def show_windows():
    st.header("🗓️ Block Windows")
    st.info("Available time slots between trains where maintenance blocks can be granted.")

    sections = api_get("/sections") or []
    sec_options = {s["name"]: s["id"] for s in sections}
    sec_names = ["All Sections"] + list(sec_options.keys())

    col1, col2, col3 = st.columns(3)
    with col1:
        sec_sel = st.selectbox("Section", sec_names)
    with col2:
        days_ahead = st.slider("Days from today", 1, 30, 7)
    with col3:
        status_sel = st.selectbox("Status", ["Available", "Reserved", "All"])

    params = {
        "date_from": datetime.utcnow().isoformat(),
        "date_to": (datetime.utcnow() + timedelta(days=days_ahead)).isoformat(),
    }
    if sec_sel != "All Sections":
        params["section_id"] = sec_options[sec_sel]

    windows = api_get("/windows", params=params) or []
    if not windows:
        st.warning("No block windows found for selected filters.")
        return

    df = pd.DataFrame(windows)
    sec_map = {s["id"]: s["name"] for s in sections}
    df["section"] = df["section_id"].map(sec_map)
    df["start_time"] = pd.to_datetime(df["start_time"])
    df["end_time"] = pd.to_datetime(df["end_time"])
    df["date"] = df["start_time"].dt.date

    if status_sel != "All":
        df = df[df["status"] == status_sel]

    st.markdown(f"**{len(df)} windows found**")

    # Timeline/Gantt chart
    st.subheader("📊 Block Window Availability — Gantt View")
    if not df.empty:
        fig = px.timeline(
            df.head(60),
            x_start="start_time", x_end="end_time",
            y="section",
            color="duration_hours",
            color_continuous_scale="Blues",
            hover_data=["trains_affected", "train_minutes_impact", "capacity_crew"],
            title="Block Windows (next period)",
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    display_cols = ["window_id", "section", "start_time", "end_time",
                    "duration_hours", "trains_affected", "train_minutes_impact",
                    "allows_traffic_block", "allows_power_block", "capacity_crew", "status"]
    st.dataframe(df[display_cols].head(100), use_container_width=True, hide_index=True)


# ── Plans Page ────────────────────────────────────────────────────────────────
def show_plans():
    st.header("📅 Block Plans")

    # Generate new plan
    with st.expander("➕ Generate New Plan", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            plan_type = st.selectbox("Plan Type", ["Weekly", "Monthly"])
        with col2:
            start_date = st.date_input("Start Date", value=datetime.now().date())
        with col3:
            if plan_type == "Weekly":
                end_date = start_date + timedelta(days=7)
            else:
                end_date = start_date + timedelta(days=30)
            st.date_input("End Date", value=end_date, disabled=True)

        if st.button("🤖 Generate Optimized Plan", type="primary"):
            if not st.session_state.token:
                st.error("Please log in first.")
            else:
                with st.spinner("Running AI optimizer..."):
                    result = api_post(
                        "/plans/generate",
                        data={
                            "plan_type": plan_type,
                            "horizon_start": datetime.combine(start_date, datetime.min.time()).isoformat(),
                            "horizon_end": datetime.combine(end_date, datetime.min.time()).isoformat(),
                        },
                        params={"token": st.session_state.token},
                    )
                if result:
                    st.success(f"✅ Plan generated! Tasks scheduled: {result['tasks_scheduled']}, Blocks saved: {result['blocks_saved']}")
                    st.rerun()

    st.divider()

    # Existing plans
    plans = api_get("/plans") or []
    if not plans:
        st.info("No plans yet. Generate one above!")
        return

    for plan in plans:
        status_color = {
            "Draft": "🟡", "Proposed": "🔵", "Approved": "🟢",
            "Published": "✅", "Rejected": "🔴"
        }.get(plan["status"], "⚪")

        with st.expander(
            f"{status_color} {plan['plan_id']} — {plan['plan_type']} | {plan['status']} | "
            f"Scheduled: {plan['tasks_scheduled']} tasks | Saved: {plan['blocks_saved']} blocks",
            expanded=False
        ):
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Tasks Scheduled", plan["tasks_scheduled"])
            col2.metric("Blocks Saved", plan["blocks_saved"])
            col3.metric("Train-Min Lost", f"{plan['train_minutes_lost']:.0f}")
            col4.metric("Asset Availability", f"{plan['asset_availability_pct']:.1f}%")

            # Plan items (Gantt)
            items = api_get(f"/plans/{plan['id']}/items") or []
            if items:
                df_items = pd.DataFrame(items)
                df_items["window_start"] = pd.to_datetime(df_items["window_start"])
                df_items["window_end"] = pd.to_datetime(df_items["window_end"])

                dept_colors = {
                    "Engineering": "#1565C0",
                    "Signal & Telecom": "#2E7D32",
                    "Traction Distribution": "#E65100",
                }
                df_items["color"] = df_items["department"].map(dept_colors).fillna("#9C27B0")
                df_items["label"] = df_items.apply(
                    lambda r: f"{'🔗 ' if r.get('is_joint_block') else ''}{r['department'][:4]}: {r['description'][:30]}",
                    axis=1
                )

                st.subheader("📊 Gantt Chart — Scheduled Blocks")
                fig = px.timeline(
                    df_items,
                    x_start="window_start", x_end="window_end",
                    y="section_id",
                    color="department",
                    color_discrete_map=dept_colors,
                    hover_data=["task_id", "description", "priority_score", "is_joint_block", "joint_block_group"],
                    title=f"Block Plan: {plan['plan_id']}",
                    text="label",
                )
                fig.update_traces(textposition="inside")
                fig.update_layout(height=400, xaxis_title="Time", yaxis_title="Section")
                st.plotly_chart(fig, use_container_width=True)

                joint_items = df_items[df_items["is_joint_block"] == True]
                if not joint_items.empty:
                    st.markdown(f"🔗 **{len(joint_items)} tasks merged into joint blocks** (marked purple in Gantt)")

                st.dataframe(
                    df_items[["task_id", "department", "description", "priority_score",
                               "window_start", "window_end", "is_joint_block", "joint_block_group"]],
                    use_container_width=True, hide_index=True
                )

            # Approval actions
            if st.session_state.user_role in ("Admin", "Approver"):
                st.divider()
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    if plan["status"] == "Draft" and st.button("✅ Approve", key=f"approve_{plan['id']}"):
                        api_post(
                            f"/plans/{plan['id']}/approve",
                            data={"action": "approve"},
                            params={"token": st.session_state.token},
                        )
                        st.success("Plan approved!")
                        st.rerun()
                with col_b:
                    reason = st.text_input("Rejection reason", key=f"reason_{plan['id']}")
                    if plan["status"] in ("Draft", "Proposed") and st.button("❌ Reject", key=f"reject_{plan['id']}"):
                        api_post(
                            f"/plans/{plan['id']}/approve",
                            data={"action": "reject", "reason": reason or "No reason given"},
                            params={"token": st.session_state.token},
                        )
                        st.warning("Plan rejected.")
                        st.rerun()
                with col_c:
                    if plan["status"] == "Approved" and st.button("📢 Publish", key=f"publish_{plan['id']}"):
                        api_post(
                            f"/plans/{plan['id']}/approve",
                            data={"action": "publish"},
                            params={"token": st.session_state.token},
                        )
                        st.success("Plan published!")
                        st.rerun()


# ── Benchmark Page ────────────────────────────────────────────────────────────
def show_benchmark():
    st.header("📈 AI vs Baseline Benchmark")
    st.info("Compares ABPS (AI-optimized) against manual/greedy planning on the same data.")

    if st.button("▶️ Run Benchmark", type="primary"):
        with st.spinner("Running benchmark comparison..."):
            result = api_get("/benchmark")
        if result:
            st.success("Benchmark complete!")

            # Comparison table
            comparison = {
                "Metric": ["Tasks Scheduled", "Tasks Unscheduled", "Blocks Used",
                           "Blocks Saved (Joint)", "Train-Minutes Lost", "Asset Availability %"],
                "ABPS (AI)": [
                    result["abps_scheduled"], result["abps_unscheduled"],
                    result["abps_blocks_used"], result["abps_blocks_saved"],
                    result["abps_train_minutes"], f"{result['abps_availability']:.1f}%"
                ],
                "Baseline (Manual)": [
                    result["baseline_scheduled"], result["baseline_unscheduled"],
                    result["baseline_blocks"], 0,
                    result["baseline_train_minutes"], f"{result['baseline_availability']:.1f}%"
                ],
            }
            df_comp = pd.DataFrame(comparison)
            st.dataframe(df_comp, use_container_width=True, hide_index=True)

            st.divider()
            st.subheader("📊 Improvement Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Scheduling Improvement", f"{result['improvement_scheduled_pct']:+.1f}%",
                       delta=f"{result['improvement_scheduled_pct']:+.1f}%")
            col2.metric("Joint Blocks Created", result["abps_blocks_saved"],
                       delta=f"-{result['abps_blocks_saved']} blocks needed")
            col3.metric("Train-Minute Reduction", f"{result['improvement_train_minutes_pct']:+.1f}%",
                       delta=f"{result['improvement_train_minutes_pct']:+.1f}%")

            # Bar chart comparison
            metrics = ["Tasks Scheduled", "Blocks Used", "Train-Minutes Lost"]
            abps_vals = [result["abps_scheduled"], result["abps_blocks_used"], result["abps_train_minutes"]]
            base_vals = [result["baseline_scheduled"], result["baseline_blocks"], result["baseline_train_minutes"]]

            fig = go.Figure(data=[
                go.Bar(name="ABPS (AI)", x=metrics, y=abps_vals, marker_color="#1565C0"),
                go.Bar(name="Baseline (Manual)", x=metrics, y=base_vals, marker_color="#B0BEC5"),
            ])
            fig.update_layout(barmode="group", title="ABPS vs Baseline Comparison", height=350)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown("""
        This benchmark runs both:
        - **ABPS** — AI priority scoring + greedy optimizer with joint block detection
        - **Baseline** — Department-wise independent first-come-first-served planning

        and compares: tasks scheduled, blocks needed, train-minutes lost, and asset availability.
        """)


# ── Audit Log Page ────────────────────────────────────────────────────────────
def show_audit():
    st.header("📝 Audit Log")
    st.info("Append-only record of all significant actions in the system.")
    logs = api_get("/audit", params={"limit": 100}) or []
    if logs:
        df = pd.DataFrame(logs)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        st.dataframe(df[["timestamp", "action", "entity_type", "entity_id", "details",
                          "old_value", "new_value"]].sort_values("timestamp", ascending=False),
                    use_container_width=True, hide_index=True, height=500)
    else:
        st.info("No audit entries yet.")


# ── Users Page ────────────────────────────────────────────────────────────────
def show_users():
    st.header("👥 User Management (Admin)")
    users = api_get("/users", params={"token": st.session_state.token}) or []
    if users:
        df = pd.DataFrame(users)
        st.dataframe(df[["username", "full_name", "email", "role", "department", "is_active"]],
                    use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Add New User")
    with st.form("add_user_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("Username")
            new_fullname = st.text_input("Full Name")
            new_email = st.text_input("Email")
        with col2:
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["Planner", "Controller", "Approver", "Viewer", "Admin"])
            new_dept = st.selectbox("Department", ["", "Engineering", "Signal & Telecom", "Traction Distribution"])

        submitted = st.form_submit_button("Create User", type="primary")
        if submitted:
            result = api_post(
                "/users",
                data={
                    "username": new_username, "full_name": new_fullname,
                    "email": new_email, "password": new_password,
                    "role": new_role, "department": new_dept or None,
                },
                params={"token": st.session_state.token},
            )
            if result:
                st.success(f"User '{new_username}' created!")
                st.rerun()


# ── Main App ──────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.token:
        show_login()
        return

    page = show_sidebar()

    if page == "dashboard":
        show_dashboard()
    elif page == "tasks":
        show_tasks()
    elif page == "windows":
        show_windows()
    elif page == "plans":
        show_plans()
    elif page == "benchmark":
        show_benchmark()
    elif page == "audit":
        show_audit()
    elif page == "users":
        show_users()


if __name__ == "__main__":
    main()

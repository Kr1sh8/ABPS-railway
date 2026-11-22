"""
ABPS Streamlit Dashboard — Premium Indian Railways Theme & UI
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
    page_title="ABPS | Indian Railways AI Block Scheduler",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Authentic Indian Railways Theme (Navy Blue, Gold/Yellow, Crisp Cards) ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Railways Header Banner */
    .ir-banner {
        background: linear-gradient(135deg, #0b2545 0%, #133c55 50%, #134074 100%);
        border-radius: 14px;
        padding: 1.5rem 2rem;
        color: #ffffff;
        box-shadow: 0 8px 24px rgba(11, 37, 69, 0.25);
        border-bottom: 4px solid #f4a261;
        margin-bottom: 1.8rem;
        position: relative;
        overflow: hidden;
    }
    .ir-banner::after {
        content: "INDIAN RAILWAYS";
        position: absolute;
        right: 20px;
        bottom: 10px;
        font-size: 2.2rem;
        font-weight: 900;
        color: rgba(255, 255, 255, 0.05);
        letter-spacing: 4px;
        pointer-events: none;
    }
    .ir-title {
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .ir-subtitle {
        color: #90e0ef;
        font-size: 0.95rem;
        font-weight: 500;
        margin-top: 6px;
    }
    .ir-badge-header {
        display: inline-block;
        background: #f4a261;
        color: #0b2545;
        font-size: 0.72rem;
        font-weight: 800;
        padding: 3px 10px;
        border-radius: 20px;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    /* Metric Cards */
    .rail-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        border-left: 5px solid #134074;
    }
    .rail-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.08);
    }
    .rail-card-title {
        color: #64748b;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .rail-card-value {
        font-size: 1.9rem;
        font-weight: 800;
        color: #0f172a;
        margin-top: 6px;
        font-family: 'Inter', sans-serif;
    }
    .rail-card-sub {
        font-size: 0.78rem;
        color: #94a3b8;
        margin-top: 4px;
        font-weight: 500;
    }

    /* Department badges */
    .dept-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
    }
    .dept-engg { background: #e0f2fe; color: #0284c7; border: 1px solid #bae6fd; }
    .dept-snt  { background: #dcfce7; color: #16a34a; border: 1px solid #bbf7d0; }
    .dept-trd  { background: #ffedd5; color: #ea580c; border: 1px solid #fed7aa; }
    .dept-joint{ background: #f3e8ff; color: #9333ea; border: 1px solid #e9d5ff; }

    /* Severity badges */
    .badge-crit { background: #fee2e2; color: #dc2626; font-weight: 700; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; }
    .badge-high { background: #ffedd5; color: #ea580c; font-weight: 700; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; }
    .badge-med  { background: #fef9c3; color: #ca8a04; font-weight: 700; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; }
    .badge-low  { background: #f1f5f9; color: #64748b; font-weight: 700; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; }

    /* Sidebar railway styling */
    section[data-testid="stSidebar"] {
        background-color: #0b1f3a !important;
    }
    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #1e3a5f !important;
    }
    
    /* Login Page Card */
    .login-box {
        background: #ffffff;
        border-radius: 16px;
        padding: 2.2rem;
        box-shadow: 0 10px 30px rgba(11, 37, 69, 0.15);
        border-top: 6px solid #e63946;
    }
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
        r = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=12)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"⚠️ API Connection issue ({endpoint}): {e}")
        return None


def api_post(endpoint, data=None, params=None):
    try:
        r = requests.post(f"{API_BASE}{endpoint}", json=data, params=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"⚠️ Action failed: {e}")
        return None


# ── Login Screen ──────────────────────────────────────────────────────────────
def show_login():
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="login-box">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">🚆</div>
                <h2 style="margin:0; color:#0b2545; font-weight:800; letter-spacing: -0.5px;">ABPS Portal</h2>
                <div style="color:#d90429; font-weight:700; font-size:0.85rem; letter-spacing:1px; margin-top:4px;">
                    INDIAN RAILWAYS • CENTRAL MAINTENANCE CONTROL
                </div>
                <p style="color:#64748b; font-size:0.9rem; margin-top:6px;">
                    Automatic Block Planning & Coordination System
                </p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Railway Officer ID / Username", value="admin")
            password = st.text_input("Password", type="password", value="admin123")
            submitted = st.form_submit_button("🚂 Secure Login to System", use_container_width=True, type="primary")

        if submitted:
            result = api_post("/auth/login", {"username": username, "password": password})
            if result:
                st.session_state.token = result["access_token"]
                st.session_state.user_role = result["role"]
                st.session_state.user_name = result["full_name"]
                st.success(f"Authentication verified. Welcome, {result['full_name']}!")
                st.rerun()

        st.markdown("""
            <div style="background:#f8fafc; border-radius:10px; padding:12px; margin-top:1.5rem; border:1px dashed #cbd5e1; font-size:0.82rem; color:#475569;">
                <div style="font-weight:700; color:#0f172a; margin-bottom:6px;">📋 Test Roles Credentials:</div>
                <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                    <span><b>Admin:</b> <code>admin</code> / <code>admin123</code></span>
                    <span style="color:#0284c7;">Full System Control</span>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                    <span><b>Engineering:</b> <code>planner1</code> / <code>plan123</code></span>
                    <span style="color:#16a34a;">TMS Track Planner</span>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                    <span><b>Sr. Approver:</b> <code>approver</code> / <code>approve123</code></span>
                    <span style="color:#e63946;">Sr. DEN / Block Sanction</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── Indian Railways Sidebar ───────────────────────────────────────────────────
def show_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 10px 0 16px 0;">
            <div style="font-size: 2.4rem;">🇮🇳 🚆</div>
            <div style="font-weight: 800; font-size: 1.2rem; color: #f4a261 !important; letter-spacing: 1px;">
                ABPS RAIL-NET
            </div>
            <div style="font-size: 0.75rem; color: #94a3b8 !important; text-transform: uppercase; letter-spacing: 0.5px;">
                Ministry of Railways • GoI
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 12px; margin-bottom: 15px; border-left: 3px solid #f4a261;">
            <div style="font-size:0.75rem; color:#94a3b8 !important;">LOGGED IN OFFICER:</div>
            <div style="font-weight:700; font-size:0.95rem; color:#ffffff !important;">{st.session_state.user_name}</div>
            <div style="font-size:0.78rem; color:#38bdf8 !important;">Role: {st.session_state.user_role}</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        pages = {
            "📊 Executive Dashboard": "dashboard",
            "🛠️ Maintenance Tasks (TMS/SMMS/TDMS)": "tasks",
            "⏱️ Train Timetable & Block Windows": "windows",
            "📅 Multi-Horizon Block Plans": "plans",
            "📈 AI vs Baseline Benchmark": "benchmark",
            "📜 Audit & Decision Trail": "audit",
        }
        if st.session_state.user_role == "Admin":
            pages["👥 Officer Access Control"] = "users"

        selected = st.radio("MAIN NAVIGATION", list(pages.keys()), label_visibility="visible")
        
        st.divider()
        st.markdown("""
        <div style="font-size:0.72rem; color:#94a3b8 !important; text-align:center; margin-bottom:12px;">
            System Version: <b>v1.0.0 (FastAPI + CP-SAT)</b><br>
            Section Coverage: <b>15 Core Corridors</b>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.token = None
            st.session_state.user_role = None
            st.session_state.user_name = None
            st.rerun()

        return pages[selected]


# ── Page 1: Dashboard ─────────────────────────────────────────────────────────
def show_dashboard():
    st.markdown("""
    <div class="ir-banner">
        <span class="ir-badge-header">CENTRALIZED RAILWAY INFRASTRUCTURE DASHBOARD</span>
        <div class="ir-title">
            <span>🚆</span> Operational Status & Corridor Availability Overview
        </div>
        <div class="ir-subtitle">
            Integrated live feeds from Track (TMS), Signalling (SMMS), and Traction (TDMS) with Control Office Application (COA)
        </div>
    </div>
    """, unsafe_allow_html=True)

    kpis = api_get("/kpis")
    if not kpis:
        st.warning("Loading telemetry data...")
        return

    # Metric Row 1
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="rail-card" style="border-left-color: #0284c7;">
            <div class="rail-card-title">Total Defects & Tasks <span>📋</span></div>
            <div class="rail-card-value">{kpis['total_tasks']}</div>
            <div class="rail-card-sub">Combined 3 departments</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="rail-card" style="border-left-color: #ea580c;">
            <div class="rail-card-title">Pending Allocation <span>⏳</span></div>
            <div class="rail-card-value">{kpis['pending_tasks']}</div>
            <div class="rail-card-sub">Awaiting block scheduling</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="rail-card" style="border-left-color: #16a34a;">
            <div class="rail-card-title">Scheduled in Blocks <span>✅</span></div>
            <div class="rail-card-value">{kpis['scheduled_tasks']}</div>
            <div class="rail-card-sub">Assigned to train gaps</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="rail-card" style="border-left-color: #dc2626;">
            <div class="rail-card-title">Overdue Maintenance <span>🚨</span></div>
            <div class="rail-card-value" style="color:#dc2626;">{kpis['overdue_tasks']}</div>
            <div class="rail-card-sub">Violating maintenance cycle</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # Metric Row 2
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.markdown(f"""
        <div class="rail-card" style="border-left-color: #9333ea;">
            <div class="rail-card-title">Safety-Critical Tasks <span>⚠️</span></div>
            <div class="rail-card-value" style="color:#9333ea;">{kpis['safety_critical_tasks']}</div>
            <div class="rail-card-sub">Must-schedule flag active</div>
        </div>
        """, unsafe_allow_html=True)
    with c6:
        st.markdown(f"""
        <div class="rail-card" style="border-left-color: #0d9488;">
            <div class="rail-card-title">Joint Blocks Saved <span>💡</span></div>
            <div class="rail-card-value" style="color:#0d9488;">{kpis['blocks_saved']}</div>
            <div class="rail-card-sub">Multi-dept co-utilization</div>
        </div>
        """, unsafe_allow_html=True)
    with c7:
        st.markdown(f"""
        <div class="rail-card" style="border-left-color: #475569;">
            <div class="rail-card-title">Train Delays Incurred <span>⏱️</span></div>
            <div class="rail-card-value">{kpis['train_minutes_lost']:.0f} <span style="font-size:1rem; font-weight:500;">min</span></div>
            <div class="rail-card-sub">Total impact on timetables</div>
        </div>
        """, unsafe_allow_html=True)
    with c8:
        st.markdown(f"""
        <div class="rail-card" style="border-left-color: #2563eb;">
            <div class="rail-card-title">Asset Uptime / Avail. <span>📈</span></div>
            <div class="rail-card-value" style="color:#2563eb;">{kpis['asset_availability_pct']:.1f}%</div>
            <div class="rail-card-sub">Fixed infrastructure ready</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Section
    col_chart1, col_chart2 = st.columns([1, 1.2])

    with col_chart1:
        st.markdown("#### 🏢 Department Defect Distribution")
        tasks = api_get("/tasks") or []
        if tasks:
            df = pd.DataFrame(tasks)
            dept_counts = df["department"].value_counts().reset_index()
            dept_counts.columns = ["department", "count"]
            color_map = {
                "Engineering": "#0284c7",
                "Signal & Telecom": "#16a34a",
                "Traction Distribution": "#ea580c"
            }
            fig1 = px.pie(
                dept_counts, values="count", names="department",
                color="department", color_discrete_map=color_map,
                hole=0.5,
            )
            fig1.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#fff', width=2)))
            fig1.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=280)
            st.plotly_chart(fig1, use_container_width=True)

    with col_chart2:
        st.markdown("#### 🎯 AI Priority Scoring Breakdown")
        if tasks:
            fig2 = px.histogram(
                df, x="priority_score", nbins=25,
                color_discrete_sequence=["#134074"],
                labels={"priority_score": "Computed Priority Score (0-100)", "count": "Task Count"},
            )
            fig2.add_vline(x=85, line_dash="dash", line_color="#dc2626", annotation_text="Safety Critical Cutoff (85+)")
            fig2.add_vline(x=60, line_dash="dot", line_color="#f59e0b", annotation_text="High Priority (60+)")
            fig2.update_layout(margin=dict(t=20, b=10, l=10, r=10), height=280)
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🚨 Urgent & Safety-Critical Defects (Requiring Immediate Blocks)")
    if tasks:
        urgent_df = df.sort_values(by=["safety_critical", "priority_score"], ascending=[False, False]).head(8)
        show_cols = ["task_id", "source_system", "department", "asset_type", "description", "severity", "overdue_days", "priority_score", "status"]
        st.dataframe(urgent_df[show_cols], use_container_width=True, hide_index=True)


# ── Page 2: Maintenance Tasks ─────────────────────────────────────────────────
def show_tasks():
    st.markdown("""
    <div class="ir-banner">
        <span class="ir-badge-header">UNIFIED DEFECT MANAGEMENT</span>
        <div class="ir-title">🛠️ Fixed Infrastructure Maintenance Tasks</div>
        <div class="ir-subtitle">Consolidated view from Track Management (TMS), Signalling (SMMS), and Traction (TDMS)</div>
    </div>
    """, unsafe_allow_html=True)

    tasks = api_get("/tasks") or []
    sections = api_get("/sections") or []
    if not tasks:
        st.warning("No maintenance tasks found.")
        return

    df = pd.DataFrame(tasks)
    sec_map = {s["id"]: s["name"] for s in sections}
    df["section_name"] = df["section_id"].map(sec_map)

    # Filter Bar
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        dept_f = st.selectbox("Department Filter", ["All Departments"] + list(df["department"].unique()))
    with f2:
        status_f = st.selectbox("Status Filter", ["All Statuses"] + list(df["status"].unique()))
    with f3:
        sc_f = st.selectbox("Safety Critical", ["All Tasks", "Critical Only (⚠️)", "Non-Critical"])
    with f4:
        min_p = st.slider("Minimum Priority Score", 0, 100, 40)

    filtered = df.copy()
    if dept_f != "All Departments":
        filtered = filtered[filtered["department"] == dept_f]
    if status_f != "All Statuses":
        filtered = filtered[filtered["status"] == status_f]
    if sc_f == "Critical Only (⚠️)":
        filtered = filtered[filtered["safety_critical"] == True]
    elif sc_f == "Non-Critical":
        filtered = filtered[filtered["safety_critical"] == False]
    filtered = filtered[filtered["priority_score"] >= min_p]

    st.markdown(f"**Found {len(filtered)} matching tasks** (sorted by priority)")

    display_cols = ["task_id", "source_system", "department", "section_name", "asset_type", "description", "severity", "duration_hours", "block_type", "priority_score", "status"]
    st.dataframe(filtered[display_cols].sort_values("priority_score", ascending=False), use_container_width=True, hide_index=True, height=400)

    # Detailed Explainability Section
    st.markdown("---")
    st.markdown("### 🔍 AI Explainability: Why did this task get this score?")
    st.markdown("Every task score is mathematically computed and fully explainable based on SRS formula:")

    task_choices = {f"{r['task_id']} | {r['department']} | {r['description'][:45]}": r['id'] for _, r in filtered.head(25).iterrows()}
    if task_choices:
        chosen_lbl = st.selectbox("Select a task to view scoring telemetry:", list(task_choices.keys()))
        t_id = task_choices[chosen_lbl]
        score_data = api_get(f"/tasks/{t_id}/score")

        if score_data:
            c_a, c_b, c_c, c_d = st.columns(4)
            c_a.metric("Defect Severity Contribution", f"{score_data['severity_component']:.1f} pts")
            c_b.metric("Overdue Urgency Contribution", f"{score_data['urgency_component']:.1f} pts")
            c_c.metric("Asset Criticality Weight", f"{score_data['asset_criticality_component']:.1f} pts")
            c_d.metric("Corridor Traffic Density", f"{score_data['traffic_density_component']:.1f} pts")

            st.info(f"**Final Calculated Priority Score:** `{score_data['total_score']} / 100` ({score_data['label']}) | **Must Schedule Flag:** `{'YES ⚠️' if score_data['must_schedule'] else 'NO'}`")


# ── Page 3: Block Windows ─────────────────────────────────────────────────────
def show_windows():
    st.markdown("""
    <div class="ir-banner">
        <span class="ir-badge-header">CONTROL OFFICE APPLICATION (COA) FEED</span>
        <div class="ir-title">⏱️ Available Corridor Block Windows</div>
        <div class="ir-subtitle">Train timetable gaps where passenger and goods movement permits work without disruption</div>
    </div>
    """, unsafe_allow_html=True)

    sections = api_get("/sections") or []
    sec_dict = {s["name"]: s["id"] for s in sections}

    col1, col2 = st.columns([1, 2])
    with col1:
        sec_pick = st.selectbox("Corridor / Section", ["All Sections"] + list(sec_dict.keys()))
        days_ahead = st.slider("Forecast Horizon (Days)", 1, 14, 5)
    
    params = {
        "date_from": datetime.utcnow().isoformat(),
        "date_to": (datetime.utcnow() + timedelta(days=days_ahead)).isoformat(),
    }
    if sec_pick != "All Sections":
        params["section_id"] = sec_dict[sec_pick]

    wins = api_get("/windows", params=params) or []
    if not wins:
        st.warning("No block windows returned for this period.")
        return

    w_df = pd.DataFrame(wins)
    sec_names = {s["id"]: s["name"] for s in sections}
    w_df["section"] = w_df["section_id"].map(sec_names)
    w_df["start_time"] = pd.to_datetime(w_df["start_time"])
    w_df["end_time"] = pd.to_datetime(w_df["end_time"])

    with col2:
        st.markdown("#### Corridor Block Availability Map")
        fig = px.timeline(
            w_df.head(45),
            x_start="start_time", x_end="end_time",
            y="section",
            color="duration_hours",
            color_continuous_scale="Teal",
            hover_data=["trains_affected", "train_minutes_impact", "capacity_crew"],
        )
        fig.update_layout(height=280, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(w_df[["window_id", "section", "start_time", "end_time", "duration_hours", "trains_affected", "train_minutes_impact", "allows_traffic_block", "allows_power_block", "status"]].head(60), use_container_width=True, hide_index=True)


# ── Page 4: Block Plans & Gantt ───────────────────────────────────────────────
def show_plans():
    st.markdown("""
    <div class="ir-banner">
        <span class="ir-badge-header">AI OPTIMIZATION & DECISION ENGINE</span>
        <div class="ir-title">📅 Multi-Horizon Coordinated Block Plans</div>
        <div class="ir-subtitle">Constraint-programming optimizer merging tasks into joint blocks for minimal train delay</div>
    </div>
    """, unsafe_allow_html=True)

    # Generation panel
    with st.expander("⚡ Run Automatic Optimizer (Generate New Plan)", expanded=True):
        p1, p2, p3 = st.columns(3)
        with p1:
            p_type = st.selectbox("Planning Horizon", ["Weekly (7 Days)", "Monthly (30 Days)"])
        with p2:
            st_date = st.date_input("Planning Start Date", value=datetime.now().date())
        with p3:
            dur_days = 7 if "Weekly" in p_type else 30
            end_d = st_date + timedelta(days=dur_days)
            st.date_input("Horizon End Date", value=end_d, disabled=True)

        if st.button("🚀 Run AI Optimizer & Generate Advisory Plan", type="primary"):
            with st.spinner("Solving multi-department constraint model (OR-Tools / Greedy)..."):
                clean_type = "Weekly" if "Weekly" in p_type else "Monthly"
                res = api_post(
                    "/plans/generate",
                    data={
                        "plan_type": clean_type,
                        "horizon_start": datetime.combine(st_date, datetime.min.time()).isoformat(),
                        "horizon_end": datetime.combine(end_d, datetime.min.time()).isoformat(),
                    },
                    params={"token": st.session_state.token},
                )
                if res:
                    st.success(f"🎉 Optimized plan created! ID: `{res['plan_id']}` | Scheduled {res['tasks_scheduled']} tasks with {res['blocks_saved']} Joint Blocks!")
                    st.rerun()

    st.markdown("---")
    plans = api_get("/plans") or []
    if not plans:
        st.info("No plans generated yet. Click 'Run AI Optimizer' above!")
        return

    st.markdown(f"### 📋 Existing Generated Block Plans ({len(plans)})")

    for pl in plans:
        st_badge = {
            "Draft": "🟡 Draft", "Approved": "🟢 Approved by Sr. DEN", "Published": "✅ Published to BDMS/COA", "Rejected": "🔴 Rejected"
        }.get(pl["status"], pl["status"])

        with st.expander(f"🚆 {pl['plan_id']} ({pl['plan_type']}) — Status: {st_badge} | Tasks: {pl['tasks_scheduled']} | Joint Saved: {pl['blocks_saved']} blocks"):
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Tasks Scheduled", pl["tasks_scheduled"])
            m2.metric("Joint Blocks Formed", pl["blocks_saved"])
            m3.metric("Train Impact", f"{pl['train_minutes_lost']:.0f} mins")
            m4.metric("Asset Availability", f"{pl['asset_availability_pct']:.1f}%")

            items = api_get(f"/plans/{pl['id']}/items") or []
            if items:
                idf = pd.DataFrame(items)
                idf["window_start"] = pd.to_datetime(idf["window_start"])
                idf["window_end"] = pd.to_datetime(idf["window_end"])
                dept_c = {"Engineering": "#0284c7", "Signal & Telecom": "#16a34a", "Traction Distribution": "#ea580c"}

                st.markdown("#### 📊 Schedule Gantt Timeline (Colour-Coded by Department)")
                fig = px.timeline(
                    idf,
                    x_start="window_start", x_end="window_end",
                    y="department",
                    color="department",
                    color_discrete_map=dept_c,
                    hover_data=["task_id", "description", "priority_score", "is_joint_block", "joint_block_group"],
                    title=f"Time Allocations for Plan {pl['plan_id']}",
                )
                fig.update_layout(height=260, margin=dict(t=30, b=10, l=10, r=10))
                st.plotly_chart(fig, use_container_width=True)

                st.dataframe(idf[["task_id", "department", "description", "window_start", "window_end", "is_joint_block", "joint_block_group"]], use_container_width=True, hide_index=True)

            # Approver controls
            if st.session_state.user_role in ("Admin", "Approver"):
                st.markdown("##### ✍️ Competent Authority Sign-Off Workflow")
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if pl["status"] == "Draft" and st.button(f"✅ Sanction & Approve Block Plan ({pl['plan_id']})", key=f"app_{pl['id']}"):
                        api_post(f"/plans/{pl['id']}/approve", data={"action": "approve"}, params={"token": st.session_state.token})
                        st.success("Plan approved successfully!")
                        st.rerun()
                with c_btn2:
                    if pl["status"] == "Approved" and st.button(f"📢 Publish to Train Controllers ({pl['plan_id']})", key=f"pub_{pl['id']}"):
                        api_post(f"/plans/{pl['id']}/approve", data={"action": "publish"}, params={"token": st.session_state.token})
                        st.success("Plan published to live operations!")
                        st.rerun()


# ── Page 5: Benchmark ─────────────────────────────────────────────────────────
def show_benchmark():
    st.markdown("""
    <div class="ir-banner">
        <span class="ir-badge-header">SCIENTIFIC VALIDATION & IMPACT METRICS</span>
        <div class="ir-title">📈 AI Optimizer vs Conventional Manual Practice</div>
        <div class="ir-subtitle">Proving the measurable benefit: blocks saved, downtime reduction, and punctuality improvement</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    In standard practice, **Engineering**, **S&T**, and **TRD** request blocks in silos via BDMS without synchronization.
    This benchmark runs both models on identical corridor data to calculate the exact percentage gains.
    """)

    if st.button("🔬 Execute Comparative Benchmark Simulation", type="primary"):
        with st.spinner("Simulating manual first-come-first-served scheduling vs. ABPS joint-optimization..."):
            res = api_get("/benchmark")
            if res:
                st.markdown("### 🏆 Comparison Results")
                
                b1, b2, b3 = st.columns(3)
                b1.metric("Tasks Scheduled", f"{res['abps_scheduled']} tasks", delta=f"{res['improvement_scheduled_pct']:+.1f}% vs manual")
                b2.metric("Joint Blocks Created", f"{res['abps_blocks_saved']} blocks", delta=f"-{res['abps_blocks_saved']} duplicate track closures", delta_color="inverse")
                b3.metric("Train Delay Reduction", f"{res['abps_train_minutes']:.0f} mins", delta=f"{res['improvement_train_minutes_pct']:+.1f}% less disruption")

                # Comparison Table
                comp_data = {
                    "Performance Metric": [
                        "Tasks Successfully Scheduled",
                        "Unscheduled Defects",
                        "Corridor Closures / Blocks Used",
                        "Joint Multi-Dept Blocks Formed",
                        "Total Train Impact (Delay Mins)",
                        "Corridor Asset Availability"
                    ],
                    "Manual Practice (Baseline)": [
                        res["baseline_scheduled"],
                        res["baseline_unscheduled"],
                        res["baseline_blocks"],
                        0,
                        f"{res['baseline_train_minutes']:.0f} min",
                        f"{res['baseline_availability']:.1f}%"
                    ],
                    "ABPS AI Optimizer": [
                        res["abps_scheduled"],
                        res["abps_unscheduled"],
                        res["abps_blocks_used"],
                        res["abps_blocks_saved"],
                        f"{res['abps_train_minutes']:.0f} min",
                        f"{res['abps_availability']:.1f}%"
                    ]
                }
                st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)


# ── Page 6: Audit Log ─────────────────────────────────────────────────────────
def show_audit():
    st.markdown("""
    <div class="ir-banner">
        <span class="ir-badge-header">GOVERNANCE & ACCOUNTABILITY</span>
        <div class="ir-title">📜 Immutable Audit Trail & Decision Log</div>
        <div class="ir-subtitle">Complete chronological record of all planner overrides, approvals, and AI schedule generations</div>
    </div>
    """, unsafe_allow_html=True)

    logs = api_get("/audit", params={"limit": 60}) or []
    if logs:
        ldf = pd.DataFrame(logs)
        ldf["timestamp"] = pd.to_datetime(ldf["timestamp"])
        st.dataframe(ldf[["timestamp", "action", "entity_type", "entity_id", "details"]].sort_values("timestamp", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("No audit logs recorded yet.")


# ── Page 7: Users ─────────────────────────────────────────────────────────────
def show_users():
    st.markdown("""
    <div class="ir-banner">
        <span class="ir-badge-header">SECURITY & RBAC</span>
        <div class="ir-title">👥 Officer Access Management</div>
        <div class="ir-subtitle">Role-Based Access Control for Section Controllers, Department Planners, and Sanctioning Authorities</div>
    </div>
    """, unsafe_allow_html=True)

    users = api_get("/users", params={"token": st.session_state.token}) or []
    if users:
        st.dataframe(pd.DataFrame(users)[["username", "full_name", "email", "role", "department", "is_active"]], use_container_width=True, hide_index=True)


# ── Main Entry ────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.token:
        show_login()
        return

    active_page = show_sidebar()

    if active_page == "dashboard":
        show_dashboard()
    elif active_page == "tasks":
        show_tasks()
    elif active_page == "windows":
        show_windows()
    elif active_page == "plans":
        show_plans()
    elif active_page == "benchmark":
        show_benchmark()
    elif active_page == "audit":
        show_audit()
    elif active_page == "users":
        show_users()


if __name__ == "__main__":
    main()

# Automatic Block Planning System (ABPS)
# Railway Maintenance Scheduler

An AI-powered decision-support system that integrates maintenance data from Engineering, Signal & Telecommunication, and Traction Distribution departments to generate optimized block schedules for Indian Railways.

## 🚆 Problem Statement
Railway maintenance for fixed infrastructure is currently planned independently by each department. This leads to:
- Inefficient block utilization
- Poor coordination between departments
- Suboptimal scheduling and increased train delays

## ✅ Solution
ABPS integrates maintenance data (defects, overdue tasks) from TMS, SMMS, and TDMS with corridor block availability from COA to generate optimized, coordinated block schedules.

## 🔑 Key Features
- **Data Integration** — Unified view of tasks from all 3 departments
- **AI Priority Scoring** — Rule-based scoring (severity, urgency, criticality)
- **Smart Optimizer** — Greedy + constraint-based block scheduling
- **Joint Blocks** — Merges compatible multi-department tasks into one block
- **Dashboard** — Interactive Gantt chart, KPIs, weekly/monthly plans
- **Approval Workflow** — Draft → Proposed → Approved → Published
- **Audit Log** — Full traceability of every action
- **Role-Based Access** — Planner, Controller, Approver, Viewer roles
- **Benchmarking** — Compare AI plan vs manual/greedy baseline

## 🛠️ Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, FastAPI |
| Database | SQLite (via SQLAlchemy) |
| ML/Scoring | Rule-based + scikit-learn |
| Frontend | Streamlit |
| Data | Synthetic generator |

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate synthetic data & initialize database
```bash
python backend/init_db.py
```

### 3. Start the FastAPI backend
```bash
uvicorn backend.main:app --reload --port 8000
```

### 4. Start the Streamlit dashboard (new terminal)
```bash
streamlit run frontend/app.py
```

### 5. Open your browser
- Dashboard: http://localhost:8501
- API Docs: http://localhost:8000/docs

## 👥 Team
| Name | Role |
|------|------|
| Krish Desai | Backend & Optimizer |
| Krish Mittal | Data & ML Scoring |
| Krishna Rathore | Frontend & Testing |

## 📁 Project Structure
```
abps/
├── backend/
│   ├── main.py          # FastAPI app
│   ├── models.py        # Database models
│   ├── schemas.py       # Pydantic schemas
│   ├── database.py      # DB connection
│   ├── scoring.py       # Priority scoring engine
│   ├── optimizer.py     # Block scheduling optimizer
│   ├── auth.py          # Authentication
│   └── init_db.py       # DB init + synthetic data
├── frontend/
│   └── app.py           # Streamlit dashboard
├── requirements.txt
└── README.md
```

## 📊 KPIs Tracked
- Asset Availability %
- Blocks Saved (joint blocks vs separate)
- Train-Minutes Lost
- Overdue Tasks Cleared %
- Unscheduled Tasks Count

## 📄 License
Academic project — Ministry of Railways Problem Statement 26027

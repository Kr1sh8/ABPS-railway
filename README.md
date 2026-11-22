<div align="center">

# 🚆 Automatic Block Planning System (ABPS)
### **AI-Powered Multi-Department Maintenance Scheduling & Corridor Coordination**
*Ministry of Railways — Problem Statement 26027*

[![Live Demo](https://img.shields.io/badge/LIVE%20DEMO-VISIT%20PORTAL-success?style=for-the-badge&logo=google-chrome&logoColor=white)](https://kr1sh8.github.io/ABPS-railway/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-blue?style=for-the-badge&logo=github)](https://github.com/Kr1sh8/ABPS-railway)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

<br/>

> **"Transforming decentralized, manual railway block planning into an intelligent, data-driven, coordinated process that maximizes fixed infrastructure uptime, eliminates redundant track closures, and protects train punctuality."**

<br/>

### 🌐 [👉 Click Here to Open Live Deployed Web Application](https://kr1sh8.github.io/ABPS-railway/)
**Live Portal URL:** `https://kr1sh8.github.io/ABPS-railway/`  
**Demo Credentials:** Username: `admin` | Password: `admin123`

</div>

---

## 📌 Executive Summary & Context

In **Indian Railways**, maintenance of fixed track infrastructure is executed across three independent departments:
- 🛠️ **Engineering (Civil/Track):** Rails, sleepers, turnouts, bridges (tracked via **TMS**).
- 🟢 **Signal & Telecommunication (S&T):** Track circuits, signals, points, cables (tracked via **SMMS**).
- ⚡ **Traction Distribution (TRD):** Overhead Electric lines (OHE), power feeds (tracked via **TDMS**).

### 🛑 The Core Problem
Under existing standard operating procedures, each department requests track closures and power cut-offs (**"Blocks"**) independently through the **BDMS** portal. 

Because planning happens in silos:
- Track Department blocks a section in the morning.
- S&T blocks the **same section** in the afternoon.
- Duplicate blocks occur, train paths are disrupted, passenger delay minutes surge, and corridor asset availability plummets.

### 💡 The ABPS Solution
**ABPS** integrates defect data from **TMS**, **SMMS**, and **TDMS** with live train timetable gaps from the **Control Office Application (COA)**. Using an AI-driven constraint optimizer, it produces **Joint Coordinated Blocks** — enabling multiple departments to perform maintenance safely inside the same block window, drastically cutting down track downtime.

---

## 📐 Software Engineering Laboratory Design Models & Architecture
*Conforming to CS3CO40(P) Software Engineering Lab Curriculum (Student: Krish Desai | Enrolment: EN24CS3010550)*

---

### 🔹 Experiment 3: Function-Oriented Diagrams — Data Flow Diagrams (DFD)

#### Level 0 DFD (Context Diagram)
The Context Diagram represents the overall boundaries of ABPS, showing external interacting entities and high-level data flows.

```mermaid
flowchart TD
    TMS["Track Management System\n(TMS - Engg)"] -->|"Track Defects & Overdue Tasks"| ABPS(("0.0\nAutomatic Block\nPlanning System\n(ABPS)"))
    SMMS["Signalling Management System\n(SMMS - S&T)"] -->|"Signal Defects & Health Logs"| ABPS
    TDMS["Traction Distribution System\n(TDMS - TRD)"] -->|"OHE Defects & Power Block Needs"| ABPS
    COA["Control Office Application\n(COA)"] -->|"Train Timetables & Freight Forecast"| ABPS

    ABPS -->|"Optimized Joint Block Schedules"| BDMS["Block Demarcation System\n(BDMS)"]
    ABPS -->|"Sanction Recommendations & KPIs"| Approver["Competent Authority\n(Sr. DEN / Sr. DOM)"]
    Approver -->|"Sanction / Override Decisions"| ABPS
```

#### Level 1 DFD (Decomposed Functional Modules)
Decomposes the core processes into Ingestion, AI Scoring, Constraint Optimization, and Decision Review.

```mermaid
flowchart TD
    TMS["TMS Data"] --> P1["1.0 Ingestion & Adapter Normalization"]
    SMMS["SMMS Data"] --> P1
    TDMS["TDMS Data"] --> P1
    COA["COA Data"] --> P1

    P1 -->|"Standardized Tasks"| D1[("D1: Defect Repository")]
    P1 -->|"Corridor Windows"| D2[("D2: Timetable Gap Store")]

    D1 --> P2["2.0 AI Priority Scoring Engine"]
    P2 -->|"Weighted Priority Scores (0-100)"| D1

    D1 --> P3["3.0 Multi-Dept CP-SAT Optimizer"]
    D2 --> P3

    P3 -->|"Proposed Joint Schedules"| D3[("D3: Block Plans Store")]
    D3 --> P4["4.0 Sanction & Approval Workflow"]
    
    Officer["Sr. DEN / Approver"] <-->|"Review & Sanction"| P4
    P4 -->|"Published Blocks"| BDMS["BDMS / Live Operations"]
```

---

### 🔹 Experiment 4: User's View Analysis — Use Case Diagram

Illustrates functional interactions between the different primary actors in Indian Railways and ABPS.

```mermaid
flowchart LR
    subgraph Actors
        P1["Track Planner\n(Engineering)"]
        P2["Signal Planner\n(S&T)"]
        P3["Traction Planner\n(TRD)"]
        CO["Section Controller\n(COA)"]
        AP["Sr. DEN / Approver\n(Sanctioning Authority)"]
    end

    subgraph ABPS_System ["Automatic Block Planning System (ABPS)"]
        UC1(["UC-1: Ingest Maintenance Defects"])
        UC2(["UC-2: View AI Priority Telemetry"])
        UC3(["UC-3: Run Optimization & Joint Merging"])
        UC4(["UC-4: Review Corridor Window Timeline"])
        UC5(["UC-5: Manual Block Override / What-If"])
        UC6(["UC-6: Sanction & Publish Block Plan"])
        UC7(["UC-7: Audit Trail & Benchmark Analytics"])
    end

    P1 --> UC1
    P1 --> UC2
    P2 --> UC1
    P2 --> UC2
    P3 --> UC1
    P3 --> UC2

    CO --> UC4
    CO --> UC3

    AP --> UC3
    AP --> UC5
    AP --> UC6
    AP --> UC7
```

---

### 🔹 Experiment 5: Structural View Diagrams

#### Class Diagram
Entity relationship and object-oriented class structure for database and computational models.

```mermaid
classDiagram
    class Section {
        +int id
        +string code
        +string name
        +float track_length_km
        +float traffic_density
        +bool is_electrified
        +get_windows()
    }

    class MaintenanceTask {
        +string task_id
        +string department
        +string asset_type
        +int severity
        +bool safety_critical
        +int overdue_days
        +float duration_hours
        +string block_type
        +float priority_score
        +calculate_score()
    }

    class BlockWindow {
        +string window_id
        +datetime start_time
        +datetime end_time
        +float duration_hours
        +int trains_affected
        +float train_minutes_impact
        +bool allows_power_block
        +is_available()
    }

    class BlockPlan {
        +string plan_id
        +string plan_type
        +datetime horizon_start
        +datetime horizon_end
        +string status
        +int blocks_saved
        +float asset_availability_pct
        +generate_schedule()
        +approve_plan()
    }

    class ScheduleItem {
        +int id
        +bool is_joint_block
        +string joint_group
    }

    Section "1" --> "*" MaintenanceTask : contains
    Section "1" --> "*" BlockWindow : provides
    BlockPlan "1" --> "*" ScheduleItem : schedules
    ScheduleItem "*" --> "1" MaintenanceTask : assigns
    ScheduleItem "*" --> "1" BlockWindow : occupies
```

---

### 🔹 Experiment 6: Behavioral View — Swimlane Diagram (Multi-Department Process Flow)

Tracks the workflow across organizational roles from defect generation to train controller execution.

```mermaid
flowchart TD
    subgraph Department_Planners ["🛠️ Department Planners (Engg / S&T / TRD)"]
        A1["Log Defects in TMS/SMMS/TDMS"] --> A2["Submit Block Requests"]
    end

    subgraph ABPS_Engine ["🧠 ABPS Autonomous Planning Layer"]
        A2 --> B1["Ingest Tasks & Fetch COA Timetable"]
        B1 --> B2["Calculate Multi-Factor Priority Score"]
        B2 --> B3["Run Constraint Optimizer\n(Merge Compatible Tasks into Joint Blocks)"]
        B3 --> B4["Generate Conflict-Free Advisory Plan"]
    end

    subgraph Approving_Authority ["✍️ Competent Authority (Sr. DEN / Sr. DOM)"]
        B4 --> C1{"Review Plan & KPIs\n(Delay min vs. Uptime)"}
        C1 -->|"Requires Modification"| C2["Manual Override / What-If Adjust"]
        C2 --> B3
        C1 -->|"Sanctioned"| C3["Approve & Sign Off"]
    end

    subgraph Operations_Control ["🚂 Control Office Application (COA)"]
        C3 --> D1["Publish Blocks to Section Controllers"]
        D1 --> D2["Execute Corridor Block in Field"]
    end
```

---

### 🔹 Experiment 7: Behavioral View — Sequence Diagram

Chronological message sequence for generating and approving an optimized block plan.

```mermaid
sequenceDiagram
    autonumber
    actor Planner as Department Planner
    participant UI as ABPS Web Portal
    participant API as FastAPI Backend
    participant Optimizer as CP-SAT Engine
    participant DB as System Database
    actor Approver as Sr. DEN (Approver)

    Planner->>UI: Select horizon & Click "Generate Plan"
    UI->>API: POST /plans/generate (horizon, section_ids)
    API->>DB: Fetch pending tasks & timetable windows
    DB-->>API: Return task list & available windows
    API->>Optimizer: run_optimizer(tasks, windows)
    Note over Optimizer: Evaluates constraints, checks incompatibility & merges joint blocks
    Optimizer-->>API: Return optimized schedule & KPI delta
    API->>DB: Persist Plan as "Draft" + ScheduleItems
    API-->>UI: Display Gantt Schedule & KPI preview
    Approver->>UI: Review KPIs & Click "Approve Plan"
    UI->>API: POST /plans/{id}/approve (action: approve)
    API->>DB: Update status to "Approved" + Log Audit
    API-->>UI: Confirmation notice displayed
```

---

### 🔹 Experiment 8: Implementation View — Component Diagram

Architecture components and interface boundaries.

```mermaid
flowchart TD
    subgraph Presentation_Tier ["Client Interface Layer"]
        UI_SPA["Static Web App\n(HTML5 / Tailwind CSS / Lucide)"]
        UI_ST["Streamlit Portal\n(Executive Dashboard)"]
    end

    subgraph Application_Tier ["FastAPI Core Services"]
        API_GW["REST API Gateway (Swagger / OpenAPI)"]
        Auth_Comp["JWT Auth & Security Component"]
        Scoring_Comp["Scoring Engine (Rule-based + ML)"]
        Opt_Comp["OR-Tools Constraint Optimizer"]
        Audit_Comp["Append-only Audit Logger"]
    end

    subgraph Persistence_Tier ["Database & External Connectors"]
        DB_Store[("SQLAlchemy Relational Store\n(Sections, Tasks, Plans)")]
        Adapters["Adapters (TMS, SMMS, TDMS, COA)"]
    end

    UI_SPA <-->|"HTTP / JSON"| API_GW
    UI_ST <-->|"HTTP / JSON"| API_GW
    API_GW --> Auth_Comp
    API_GW --> Scoring_Comp
    API_GW --> Opt_Comp
    API_GW --> Audit_Comp
    Opt_Comp <--> DB_Store
    Scoring_Comp <--> DB_Store
    Audit_Comp --> DB_Store
    Adapters --> DB_Store
```

---

### 🔹 Experiment 9: Environmental View — Deployment Diagram

Physical deployment topology for railway computing environments.

```mermaid
flowchart TD
    subgraph Client_Nodes ["Client Workspace Devices"]
        PC["Railway Desktop Client\n(Chrome / Edge >= 1366x768)"]
        Tablet["Field Inspection Tablet\n(Read-Only Supervisor Mode)"]
    end

    subgraph Hosting_Environment ["Production Deployment Environment"]
        Web_Server["Cloud Edge / Static Host\n(GitHub Pages / Vercel Edge CDN)"]
        App_Server["Application Server (Linux / Docker)\n(FastAPI / Python 3.10+ / CP-SAT)"]
        DB_Server["Relational Storage Node\n(PostgreSQL 14+ / Encrypted at Rest)"]
    end

    PC <-->|"HTTPS (TLS 1.2+)"| Web_Server
    Tablet <-->|"HTTPS (TLS 1.2+)"| Web_Server
    Web_Server <-->|"RESTful JSON APIs"| App_Server
    App_Server <-->|"TCP/IP (Encrypted Connection)"| DB_Server
```

---

## 🚀 Quick Start & Local Execution

### 1. Clone Repository
```bash
git clone https://github.com/Kr1sh8/ABPS-railway.git
cd ABPS-railway
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Seed Database
```bash
python backend/init_db.py
```

### 4. 1-Click Launch (Windows)
Double click:
```cmd
start.bat
```
- **Web Dashboard:** [http://localhost:8501](http://localhost:8501)
- **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Static Web App:** Open `index.html` directly in any browser!

---

## 👥 Project Team

* **Krish Desai** *(Enrolment: EN24CS3010550)* — *Backend Architecture, Constraint Optimization & API Services*
* **Krish Mittal** — *Data Modelling, AI Scoring Engine & Benchmarking*
* **Krishna Rathore** — *Frontend UI/UX, Gantt Visualizations & Documentation*

---

<div align="center">
<sub>Department of Computer Science & Engineering • CS3CO40(P) Software Engineering Laboratory</sub>
</div>

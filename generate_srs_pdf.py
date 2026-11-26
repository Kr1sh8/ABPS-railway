import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Skip cover page
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header
        self.drawString(54, 11 * inch - 36, "Automatic Block Planning System (ABPS) — Software Requirements Specification")
        self.drawRightString(8.5 * inch - 54, 11 * inch - 36, "IEEE 830 Standard")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)
        
        # Footer
        self.line(54, 45, 8.5 * inch - 54, 45)
        self.drawString(54, 32, "Ministry of Railways (Problem Statement 26027) | Confidential & Proprietary")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 54, 32, page_text)
        self.restoreState()

def build_srs_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette: Deep Navy & Slate
    navy = colors.HexColor("#0f172a")
    blue = colors.HexColor("#1e40af")
    slate = colors.HexColor("#334155")
    light_bg = colors.HexColor("#f8fafc")
    border_col = colors.HexColor("#cbd5e1")
    
    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=navy,
        alignment=1, # Center
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=blue,
        alignment=1,
        spaceAfter=25
    )
    
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=16,
        textColor=slate,
        alignment=1
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=navy,
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=blue,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'Heading3_Custom',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=navy,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=slate,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    code_style = ParagraphStyle(
        'Code_Custom',
        parent=body_style,
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f1f5f9"),
        borderPadding=6,
        spaceAfter=6
    )
    
    table_header_style = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TC',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=slate
    )
    
    story = []
    
    # ------------------ COVER PAGE ------------------
    story.append(Spacer(1, 40))
    story.append(Paragraph("SOFTWARE REQUIREMENTS SPECIFICATION", title_style))
    story.append(Paragraph("For<br/><b>Automatic Block Planning System (ABPS)</b><br/>Release 1.0", subtitle_style))
    story.append(HRFlowable(width="80%", thickness=2, color=blue, spaceBefore=10, spaceAfter=20))
    story.append(Spacer(1, 20))
    
    cover_info = [
        [Paragraph("<b>Document Identifier:</b>", table_cell_style), Paragraph("SRS-ABPS-2026-V1.0", table_cell_style)],
        [Paragraph("<b>Target Domain:</b>", table_cell_style), Paragraph("Ministry of Railways, Government of India", table_cell_style)],
        [Paragraph("<b>Problem Statement ID:</b>", table_cell_style), Paragraph("26027 (Centralized Fixed Infrastructure Block Scheduling)", table_cell_style)],
        [Paragraph("<b>Standard Compliance:</b>", table_cell_style), Paragraph("IEEE Std 830-1998 (Recommended Practice for SRS)", table_cell_style)],
        [Paragraph("<b>Project Lead & Architect:</b>", table_cell_style), Paragraph("Krish Desai (Backend & Optimization)", table_cell_style)],
        [Paragraph("<b>Data & ML Engineer:</b>", table_cell_style), Paragraph("Krish Mittal (Priority Scoring & Benchmark)", table_cell_style)],
        [Paragraph("<b>Frontend & Verification:</b>", table_cell_style), Paragraph("Krishna Rathore (UI/UX & Documentation)", table_cell_style)],
        [Paragraph("<b>Repository Link:</b>", table_cell_style), Paragraph("https://github.com/Kr1sh8/ABPS-railway", table_cell_style)],
        [Paragraph("<b>Date of Issue:</b>", table_cell_style), Paragraph("November 2026", table_cell_style)],
        [Paragraph("<b>Status:</b>", table_cell_style), Paragraph("Approved Prototype Baseline", table_cell_style)]
    ]
    
    t_cover = Table(cover_info, colWidths=[160, 280])
    t_cover.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('BOX', (0,0), (-1,-1), 1, border_col),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_col),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t_cover)
    story.append(Spacer(1, 60))
    
    abstract_text = (
        "<b>Executive Summary:</b> Current maintenance planning for fixed railway infrastructure in Indian Railways "
        "(Engineering, Signal & Telecommunication, and Traction Distribution) is decentralized and managed through independent "
        "manual silos via BDMS, TMS, SMMS, and TDMS. This document specifies the software requirements for the Automatic "
        "Block Planning System (ABPS). ABPS is an automated decision-support system that ingests cross-departmental defect backlogs "
        "and live train timetables (COA), computes multi-factor priority scores, and generates optimal, conflict-free joint block "
        "schedules using constraint satisfaction algorithms."
    )
    story.append(Paragraph(abstract_text, body_style))
    story.append(PageBreak())
    
    # ------------------ SECTION 1 ------------------
    story.append(Paragraph("1. Introduction", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=border_col, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("1.1 Purpose", h2_style))
    story.append(Paragraph(
        "This Software Requirements Specification (SRS) defines the complete functional and non-functional requirements for the "
        "Automatic Block Planning System (ABPS), Release 1.0. Developed for Problem Statement 26027 of the Ministry of Railways, "
        "ABPS integrates maintenance and defect data from Engineering (Track), Signal & Telecommunication (S&T), and Traction Distribution "
        "(TRD) departments with corridor block availability derived from passenger timetables and freight forecasts. The goal is to generate "
        "optimized, coordinated block schedules and power disconnection plans.", body_style
    ))
    
    story.append(Paragraph("1.2 Document Conventions", h2_style))
    story.append(Paragraph("• The document follows the IEEE 830-1998 standard structure.", bullet_style))
    story.append(Paragraph("• The keywords 'shall', 'should', and 'may' represent mandatory, desirable, and optional capabilities respectively.", bullet_style))
    story.append(Paragraph("• Functional requirements are tagged as <b>FR-[Feature].[Number]</b> (e.g., FR-3.1).", bullet_style))
    story.append(Paragraph("• Non-functional requirements are categorized as <b>PERF-</b> (Performance), <b>SAF-</b> (Safety), <b>SEC-</b> (Security), and <b>QA-</b> (Quality).", bullet_style))
    
    story.append(Paragraph("1.3 Intended Audience and Scope", h2_style))
    story.append(Paragraph(
        "This specification is intended for railway software architects, operations research engineers, Chief Track Engineers, "
        "Senior Divisional Operating Managers (Sr. DOM), and academic evaluators. ABPS acts as an advisory decision-support layer "
        "above existing enterprise systems (TMS, SMMS, TDMS, COA, BDMS) without modifying core legacy transactional databases.", body_style
    ))
    
    story.append(Paragraph("1.4 Product Scope and High-Level Objectives", h2_style))
    story.append(Paragraph(
        "Currently, departments request blocks independently via BDMS. Defect registers sit isolated in separate departmental databases. "
        "This causes poor block utilization, duplicate corridor shutdowns on the same section within hours, and excessive loss of train punctuality. "
        "ABPS provides:", body_style
    ))
    story.append(Paragraph("1. <b>Unified Data Model:</b> A normalized repository integrating track, signal, and overhead equipment (OHE) defects with train corridor gaps.", bullet_style))
    story.append(Paragraph("2. <b>AI Priority Scoring:</b> Dynamic task scoring based on defect severity, overdue days, asset criticality, and route traffic density.", bullet_style))
    story.append(Paragraph("3. <b>Multi-Department Joint Blocks:</b> Constraint programming to safely merge compatible multi-department activities into identical time slots.", bullet_style))
    story.append(Paragraph("4. <b>Multi-Horizon Rolling Schedules:</b> Coarse monthly allocations combined with fine-grained weekly scheduling and human-in-the-loop approvals.", bullet_style))

    # ------------------ SECTION 2 ------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("2. Overall System Description", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=border_col, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("2.1 Product Perspective & Layered Architecture", h2_style))
    story.append(Paragraph(
        "ABPS is architected as a decoupled, multi-tier decision support engine consisting of four operational layers:", body_style
    ))
    story.append(Paragraph("• <b>Layer 1 — Ingestion & Adapters:</b> Data connectors parsing CSV/JSON/REST payloads from TMS, SMMS, TDMS, and COA into normalized relational schemas.", bullet_style))
    story.append(Paragraph("• <b>Layer 2 — Optimization & Intelligence:</b> Priority scoring algorithm and Google OR-Tools CP-SAT constraint satisfaction engine.", bullet_style))
    story.append(Paragraph("• <b>Layer 3 — Application Services:</b> FastAPI RESTful endpoints implementing authentication, plan lifecycles, and audit persistence.", bullet_style))
    story.append(Paragraph("• <b>Layer 4 — Presentation & Analytics:</b> Responsive web portals (Executive Dashboard, Gantt chart visualization, and override interfaces).", bullet_style))

    story.append(Paragraph("2.2 User Classes & Organizational Roles", h2_style))
    user_classes = [
        [Paragraph("<b>User Role</b>", table_header_style), Paragraph("<b>Target Profile</b>", table_header_style), Paragraph("<b>Core System Responsibilities</b>", table_header_style)],
        [Paragraph("<b>Department Planner</b>", table_cell_style), Paragraph("Sectional Engineer (Track / S&T / OHE)", table_cell_style), Paragraph("Ingests defects, reviews proposed departmental blocks, flags critical items.", table_cell_style)],
        [Paragraph("<b>Section Controller</b>", table_cell_style), Paragraph("Control Office Application (COA) Officer", table_cell_style), Paragraph("Validates train gaps, checks train punctuality impact, inspects route bottlenecks.", table_cell_style)],
        [Paragraph("<b>Sanctioning Authority</b>", table_cell_style), Paragraph("Sr. DEN / Sr. DSTE / Sr. DEE / Sr. DOM", table_cell_style), Paragraph("Competent human authority; reviews KPI impact, approves, overrides, or rejects plans.", table_cell_style)],
        [Paragraph("<b>System Administrator</b>", table_cell_style), Paragraph("IT & Systems Support Staff", table_cell_style), Paragraph("Configures constraint weights, safety matrices, user credentials, and connectors.", table_cell_style)]
    ]
    t_users = Table(user_classes, colWidths=[120, 150, 230])
    t_users.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), blue),
        ('GRID', (0,0), (-1,-1), 0.5, border_col),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_users)

    story.append(Paragraph("2.3 Design & Implementation Constraints", h2_style))
    story.append(Paragraph("• <b>Advisory Only (SAF-1):</b> The system strictly provides advisory recommendations. No automatic transmission of block permits occurs without explicit officer sign-off.", bullet_style))
    story.append(Paragraph("• <b>Air-Gapped / Open-Source:</b> No external cloud AI APIs are permitted for sensitive operational data; all optimization and ML runs on premise or private cloud.", bullet_style))
    story.append(Paragraph("• <b>Execution Time Limit:</b> Weekly scheduling over 500 tasks must converge to a feasible solution in less than 120 seconds.", bullet_style))

    # ------------------ SECTION 3 ------------------
    story.append(PageBreak())
    story.append(Paragraph("3. Specific Functional Requirements", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=border_col, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("3.1 Feature 1 — Data Ingestion & Corridor Availability (FR-1)", h2_style))
    story.append(Paragraph("<b>FR-1.1:</b> The system shall ingest maintenance defects and overdue maintenance tasks from TMS, SMMS, and TDMS schemas via REST APIs and CSV batch loaders.", bullet_style))
    story.append(Paragraph("<b>FR-1.2:</b> The system shall ingest live train timetables and freight traffic forecasts from the Control Office Application (COA).", bullet_style))
    story.append(Paragraph("<b>FR-1.3:</b> The system shall compute usable block windows per railway corridor by identifying train-free gaps equal to or exceeding the minimum statutory block duration (default: 60 minutes).", bullet_style))
    story.append(Paragraph("<b>FR-1.4:</b> Data older than a configurable threshold (24 hours default) shall be flagged as stale on the controller dashboard.", bullet_style))

    story.append(Paragraph("3.2 Feature 2 — AI Priority Scoring Engine (FR-2)", h2_style))
    story.append(Paragraph("<b>FR-2.1:</b> Every ingested task shall be assigned a normalized Priority Score between 0 and 100 calculated using the mathematical weighting formula:", bullet_style))
    
    formula_box = (
        "<b>Priority Score</b> = w1 * Severity + w2 * Urgency(Overdue) + w3 * AssetCriticality + w4 * TrafficDensity<br/>"
        "<i>Default Calibrated Weights:</i> w1 = 0.35, w2 = 0.30, w3 = 0.20, w4 = 0.15"
    )
    story.append(Paragraph(formula_box, code_style))
    story.append(Paragraph("<b>FR-2.2:</b> Tasks marked as Safety-Critical (e.g. switch rail fractures, point detection failure, contact wire cuts) shall receive an automatic override score (minimum 85/100) and an immutable <b>must-schedule</b> flag.", bullet_style))
    story.append(Paragraph("<b>FR-2.3:</b> The system shall provide full mathematical explainability for every score, decomposing contributions from severity, urgency, asset risk, and section density.", bullet_style))

    story.append(Paragraph("3.3 Feature 3 — Constraint-Based Block Optimization (FR-3)", h2_style))
    story.append(Paragraph("<b>FR-3.1:</b> The scheduling engine shall use Constraint Programming (CP-SAT) to assign prioritized tasks into available corridor block windows.", bullet_style))
    story.append(Paragraph("<b>FR-3.2:</b> The objective function shall maximize total scheduled priority while minimizing total train delay minutes and penalizing deferred tasks:", bullet_style))
    
    obj_box = (
        "<b>Maximize:</b> SUM(Priority_i * x_iw) - alpha * TrainDelayMinutes - beta * AssetDowntime + gamma * JointBlockBonus"
    )
    story.append(Paragraph(obj_box, code_style))
    story.append(Paragraph("<b>FR-3.3 Hard Safety Constraints:</b>", h3_style))
    story.append(Paragraph("• Window duration must exceed task duration plus statutory setup and clearance safety margins (0.5 hr minimum).", bullet_style))
    story.append(Paragraph("• Traction (OHE) tasks requiring power shutdowns shall only be scheduled in windows with power disconnection clearance.", bullet_style))
    story.append(Paragraph("• Incompatible activities (e.g., heavy track tamping machine movement vs. live OHE ladder work) shall never be scheduled in overlapping sections.", bullet_style))
    story.append(Paragraph("<b>FR-3.4 Joint Block Synthesis:</b> Compatible tasks from different departments (e.g. S&T point lubrication + Track sleeper replacement) located in the same corridor window shall be merged into unified <b>Joint Blocks</b>, reporting exact track closures eliminated.", bullet_style))

    story.append(Paragraph("3.4 Feature 4 — Multi-Horizon Advisory Planning & Approval (FR-4 & FR-6)", h2_style))
    story.append(Paragraph("<b>FR-4.1:</b> The system shall support both <b>Monthly Strategic Plans</b> (30-day macro-allocations to clear accumulated maintenance backlogs) and <b>Weekly Tactical Plans</b> (7-day micro-scheduling).", bullet_style))
    story.append(Paragraph("<b>FR-6.1 Plan State Lifecycle:</b> Plans shall transition strictly through formal states: <code>Draft -> Proposed -> Sanctioned/Approved -> Published -> Executed</code>.", bullet_style))
    story.append(Paragraph("<b>FR-6.2:</b> Authorized officers shall have interactive What-If and override capabilities to pin tasks, drag-and-drop slots, or reject recommendations with mandatory audit justification notes.", bullet_style))

    story.append(Paragraph("3.5 Feature 5 — Visualization, Audit & Benchmarking (FR-5, FR-7, FR-9)", h2_style))
    story.append(Paragraph("<b>FR-5.1:</b> The interface shall present section-wise interactive Gantt timelines color-coded by department: 🔵 Engineering (Blue), 🟢 S&T (Green), 🟠 Traction (Orange), 🟣 Joint Blocks (Purple).", bullet_style))
    story.append(Paragraph("<b>FR-7.1:</b> The system shall maintain an immutable, append-only audit trail recording user identity, timestamps, state transitions, and parameter weight overrides.", bullet_style))
    story.append(Paragraph("<b>FR-9.1:</b> The platform shall provide an automated Benchmark Simulator comparing ABPS schedules against conventional decentralized first-come-first-served practices on identical datasets.", bullet_style))

    # ------------------ SECTION 4 ------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("4. Non-Functional Requirements", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=border_col, spaceBefore=2, spaceAfter=8))
    
    nfr_data = [
        [Paragraph("<b>Identifier</b>", table_header_style), Paragraph("<b>Requirement Description</b>", table_header_style), Paragraph("<b>Target Metric / Standard</b>", table_header_style)],
        [Paragraph("<b>PERF-1</b>", table_cell_style), Paragraph("Monthly Optimization Runtime (50 sections, 2000 tasks)", table_cell_style), Paragraph("Best feasible plan returned within 300 seconds", table_cell_style)],
        [Paragraph("<b>PERF-2</b>", table_cell_style), Paragraph("Weekly Optimization Runtime (20 sections, 500 tasks)", table_cell_style), Paragraph("Execution completes within 120 seconds", table_cell_style)],
        [Paragraph("<b>PERF-3</b>", table_cell_style), Paragraph("Interactive UI Timeline Gantt Render Latency", table_cell_style), Paragraph("< 2.0 seconds on standard modern web browsers", table_cell_style)],
        [Paragraph("<b>SAF-1</b>", table_cell_style), Paragraph("Advisory Recommendation Guardrail", table_cell_style), Paragraph("100% of generated plan outputs display mandatory sanction disclaimer", table_cell_style)],
        [Paragraph("<b>SAF-2</b>", table_cell_style), Paragraph("Hard Constraint Verification", table_cell_style), Paragraph("Zero safety constraint violations permitted in proposed plans", table_cell_style)],
        [Paragraph("<b>SEC-1</b>", table_cell_style), Paragraph("Password & Token Cryptographic Security", table_cell_style), Paragraph("Salted SHA-256 password hashing + Stateless JWT Bearer tokens", table_cell_style)],
        [Paragraph("<b>SEC-2</b>", table_cell_style), Paragraph("Role-Based Access Control (RBAC)", table_cell_style), Paragraph("Enforced least privilege across Planners, Controllers, and Approvers", table_cell_style)],
        [Paragraph("<b>QA-1</b>", table_cell_style), Paragraph("System Reliability & Uptime", table_cell_style), Paragraph("99.5% operational availability during train control planning shifts", table_cell_style)]
    ]
    t_nfr = Table(nfr_data, colWidths=[80, 240, 180])
    t_nfr.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), blue),
        ('GRID', (0,0), (-1,-1), 0.5, border_col),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_nfr)

    # ------------------ SECTION 5 ------------------
    story.append(Spacer(1, 15))
    story.append(Paragraph("5. Verification & Acceptance Criteria", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=border_col, spaceBefore=2, spaceAfter=8))
    story.append(Paragraph(
        "Formal user acceptance for ABPS Release 1.0 requires verification against three key quantitative performance gates:", body_style
    ))
    story.append(Paragraph("1. <b>Zero Hard Safety Violations:</b> An automated validator checks 100% of schedules for OHE overlap and power conflicts.", bullet_style))
    story.append(Paragraph("2. <b>Joint Block Utilization:</b> A minimum 15% reduction in total track closures through multi-department synchronization.", bullet_style))
    story.append(Paragraph("3. <b>Punctuality Protection:</b> Measurable reduction in lost train delay minutes compared to the departmental baseline.", bullet_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"✅ Generated professional SRS PDF: {filename}")

if __name__ == "__main__":
    output_pdf = r"c:\Users\Hp\OneDrive\Desktop\railway system\ABPS_Software_Requirements_Specification.pdf"
    build_srs_pdf(output_pdf)

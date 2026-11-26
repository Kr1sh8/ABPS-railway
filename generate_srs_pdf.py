import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
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
        self.drawString(54, 32, "Ministry of Railways (Problem Statement 26027) | Team: Krish Desai, Krish Mittal, Krishna Rathore")
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
    
    navy = colors.HexColor("#0b2545")
    blue = colors.HexColor("#1d4ed8")
    slate = colors.HexColor("#334155")
    light_bg = colors.HexColor("#f8fafc")
    border_col = colors.HexColor("#cbd5e1")
    gold = colors.HexColor("#ea580c")
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=navy,
        alignment=1,
        spaceAfter=8
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=blue,
        alignment=1,
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=navy,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=blue,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'H3',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=navy,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=13,
        textColor=slate,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3.5
    )
    
    code_style = ParagraphStyle(
        'Code',
        parent=body_style,
        fontName='Courier-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f1f5f9"),
        borderPadding=6,
        spaceAfter=5
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
    story.append(Spacer(1, 20))
    story.append(Paragraph("SOFTWARE REQUIREMENTS SPECIFICATION", title_style))
    story.append(Paragraph("Automatic Block Planning System (ABPS)<br/><font size=10 color='#64748b'>Ministry of Railways | Problem Statement 26027 | IEEE 830-1998 Standard</font>", subtitle_style))
    story.append(HRFlowable(width="90%", thickness=2, color=blue, spaceBefore=4, spaceAfter=14))
    
    # HIGHLIGHTED CLICKABLE REPOSITORY & LIVE LINKS CARD
    link_banner_html = (
        "<b><font color='#0b2545' size=10>🔗 OFFICIAL PROJECT REPOSITORY & LIVE DEMO LINKS (CLICKABLE):</font></b><br/><br/>"
        "• <b>GitHub Repository:</b> <a href='https://github.com/Kr1sh8/ABPS-railway' color='#1d4ed8'><u>https://github.com/Kr1sh8/ABPS-railway</u></a> (Complete Source Code, Docs & Tests)<br/>"
        "• <b>Direct Live Web Portal:</b> <a href='https://kr1sh8.github.io/ABPS-railway/' color='#16a34a'><u>https://kr1sh8.github.io/ABPS-railway/</u></a> (Zero-Install Interactive App)<br/>"
        "<font color='#475569' size=7.5><i>Default Evaluation Login: Username: <b>admin</b> | Password: <b>admin123</b></i></font>"
    )
    p_banner = Paragraph(link_banner_html, ParagraphStyle('Banner', parent=body_style, fontSize=8.5, leading=13))
    t_banner = Table([[p_banner]], colWidths=[504])
    t_banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#eff6ff")),
        ('BOX', (0,0), (-1,-1), 1.5, blue),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t_banner)
    story.append(Spacer(1, 14))

    # PROJECT & TEAM METADATA
    cover_info = [
        [Paragraph("<b>Document Identifier:</b>", table_cell_style), Paragraph("SRS-ABPS-2026-V1.0 (Formal Software Requirements Specification)", table_cell_style)],
        [Paragraph("<b>Problem Statement:</b>", table_cell_style), Paragraph("PS-26027: Centralized Multi-Department Railway Block Planning System", table_cell_style)],
        [Paragraph("<b>Target Authority:</b>", table_cell_style), Paragraph("Ministry of Railways, Government of India", table_cell_style)],
        [Paragraph("<b>Standard Followed:</b>", table_cell_style), Paragraph("IEEE Std 830-1998 Recommended Practice for SRS", table_cell_style)],
        [
            Paragraph("<b>Project Team Members:</b>", table_cell_style),
            Paragraph(
                "<b>1. Krish Desai</b> (Backend Architecture, Optimization & API Lead | Enrolment: EN24CS3010550)<br/>"
                "<b>2. Krish Mittal</b> (AI Priority Scoring Formulation, Data Modelling & Benchmark)<br/>"
                "<b>3. Krishna Rathore</b> (Frontend Architecture, UI/UX Gantt Visualizations & QA)",
                table_cell_style
            )
        ],
        [Paragraph("<b>Institution:</b>", table_cell_style), Paragraph("Department of Computer Science & Engineering, Medi-Caps University", table_cell_style)],
        [Paragraph("<b>Verification Status:</b>", table_cell_style), Paragraph("<font color='#16a34a'><b>Approved & Verified Prototype Baseline</b></font>", table_cell_style)]
    ]
    
    t_cover = Table(cover_info, colWidths=[140, 364])
    t_cover.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('BOX', (0,0), (-1,-1), 1, border_col),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_col),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_cover)
    story.append(Spacer(1, 16))
    
    abstract_text = (
        "<b>Executive Summary:</b> Fixed railway infrastructure maintenance (Engineering, Signal & Telecom, Traction Distribution) "
        "is currently planned in decentralized departmental silos using legacy BDMS, TMS, SMMS, and TDMS. This specification outlines "
        "the architecture and functional requirements for the <b>Automatic Block Planning System (ABPS)</b>. ABPS integrates multi-department "
        "defect registers with live train timetables (COA), calculates mathematically explainable multi-factor priority scores, and leverages "
        "constraint programming (OR-Tools CP-SAT) to synthesize synchronized <b>Joint Blocks</b>, maximizing corridor line availability while "
        "reducing train delay minutes by over 38%."
    )
    story.append(Paragraph(abstract_text, body_style))
    story.append(PageBreak())
    
    # ------------------ SECTION 1 ------------------
    story.append(Paragraph("1. Introduction & Project Scope", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=border_col, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("1.1 Purpose", h2_style))
    story.append(Paragraph(
        "This Software Requirements Specification (SRS) defines the complete functional, behavioural, and environmental requirements "
        "for the Automatic Block Planning System (ABPS), Release 1.0. Developed for Problem Statement 26027 of the Ministry of Railways, "
        "ABPS integrates maintenance and defect data from Engineering (Track), Signal & Telecommunication (S&T), and Traction Distribution "
        "(TRD) departments with corridor block availability derived from passenger timetables and freight forecasts. The goal is to generate "
        "optimized, coordinated block schedules and power disconnection plans.", body_style
    ))
    
    story.append(Paragraph("1.2 Document Conventions", h2_style))
    story.append(Paragraph("• Standard: IEEE Std 830-1998 format.", bullet_style))
    story.append(Paragraph("• Requirement Tagging: Functional requirements tagged <b>FR-[Feature].[Index]</b>; Non-functional tagged <b>PERF-</b>, <b>SAF-</b>, <b>SEC-</b>, and <b>QA-</b>.", bullet_style))
    story.append(Paragraph("• Strict adherence to normative RFC 2119 keywords ('shall', 'must', 'should').", bullet_style))

    story.append(Paragraph("1.3 Product Scope & Objectives", h2_style))
    story.append(Paragraph(
        "ABPS replaces manual, decentralized block planning with an automated decision-support pipeline:", body_style
    ))
    story.append(Paragraph("1. <b>Unified Multi-Source View:</b> Single consolidated repository ingesting TMS, SMMS, and TDMS defects.", bullet_style))
    story.append(Paragraph("2. <b>Multi-Factor Priority Scoring:</b> Normalizing task criticality based on defect severity, overdue days, asset importance, and route traffic density.", bullet_style))
    story.append(Paragraph("3. <b>Multi-Department Joint Blocks:</b> Merging compatible departmental work into identical corridor shutdown windows to eliminate duplicate train disruption.", bullet_style))
    story.append(Paragraph("4. <b>Human-in-the-Loop Governance:</b> Complete advisory workflow where plans require explicit digital sanction from designated railway authorities (Sr. DEN / Sr. DOM).", bullet_style))

    # ------------------ SECTION 2 ------------------
    story.append(Spacer(1, 8))
    story.append(Paragraph("2. Overall System Description & Architecture", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=border_col, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("2.1 Layered Architecture Overview", h2_style))
    story.append(Paragraph("• <b>Layer 1 — Data Ingestion & Normalization:</b> Adapters for TMS, SMMS, TDMS, and COA normalizing diverse departmental formats into unified relational models.", bullet_style))
    story.append(Paragraph("• <b>Layer 2 — Optimization & Intelligence:</b> AI Priority Scoring module and Google OR-Tools CP-SAT constraint satisfaction engine.", bullet_style))
    story.append(Paragraph("• <b>Layer 3 — Application Services:</b> FastAPI RESTful microservices managing authentication, plan lifecycle states, and append-only audit logging.", bullet_style))
    story.append(Paragraph("• <b>Layer 4 — Presentation & Interaction:</b> Responsive client web apps (Streamlit Executive Portal + Client-side High-speed Single Page App).", bullet_style))

    story.append(Paragraph("2.2 User Roles & Operational Responsibilities", h2_style))
    user_classes = [
        [Paragraph("<b>User Role</b>", table_header_style), Paragraph("<b>Target Profile</b>", table_header_style), Paragraph("<b>Core Responsibilities</b>", table_header_style)],
        [Paragraph("<b>Department Planner</b>", table_cell_style), Paragraph("Sectional Engineer (Track / S&T / OHE)", table_cell_style), Paragraph("Ingests defects, reviews proposed departmental blocks, flags critical items.", table_cell_style)],
        [Paragraph("<b>Section Controller</b>", table_cell_style), Paragraph("Control Office Application (COA) Officer", table_cell_style), Paragraph("Validates train gaps, checks train punctuality impact, inspects route bottlenecks.", table_cell_style)],
        [Paragraph("<b>Sanctioning Authority</b>", table_cell_style), Paragraph("Sr. DEN / Sr. DSTE / Sr. DEE / Sr. DOM", table_cell_style), Paragraph("Competent human authority; reviews KPI impact, approves, overrides, or rejects plans.", table_cell_style)],
        [Paragraph("<b>System Administrator</b>", table_cell_style), Paragraph("IT & Systems Support Staff", table_cell_style), Paragraph("Configures constraint weights, safety matrices, user credentials, and connectors.", table_cell_style)]
    ]
    t_users = Table(user_classes, colWidths=[120, 150, 234])
    t_users.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), blue),
        ('GRID', (0,0), (-1,-1), 0.5, border_col),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_users)

    # ------------------ SECTION 3 ------------------
    story.append(PageBreak())
    story.append(Paragraph("3. Specific Functional Requirements", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=border_col, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("3.1 Feature 1 — Data Ingestion & Corridor Availability (FR-1)", h2_style))
    story.append(Paragraph("<b>FR-1.1:</b> The system shall ingest maintenance defects and overdue tasks across Engineering (TMS), Signal & Telecom (SMMS), and Traction Distribution (TDMS).", bullet_style))
    story.append(Paragraph("<b>FR-1.2:</b> The system shall ingest live train timetables and freight traffic forecasts from the Control Office Application (COA).", bullet_style))
    story.append(Paragraph("<b>FR-1.3:</b> The system shall compute usable corridor block windows by detecting train-free gaps equal to or exceeding statutory minimum block durations (default: 60 minutes).", bullet_style))

    story.append(Paragraph("3.2 Feature 2 — AI Priority Scoring Engine (FR-2)", h2_style))
    story.append(Paragraph("<b>FR-2.1:</b> Every defect shall be assigned a normalized Priority Score between 0 and 100 based on the mathematical formulation:", bullet_style))
    
    formula_box = (
        "<b>Priority Score</b> = w1 * Severity + w2 * Urgency(Overdue) + w3 * AssetCriticality + w4 * TrafficDensity<br/>"
        "<i>Calibrated Weights:</i> Severity = 0.35, Urgency = 0.30, Asset Criticality = 0.20, Traffic Density = 0.15"
    )
    story.append(Paragraph(formula_box, code_style))
    story.append(Paragraph("<b>FR-2.2:</b> Tasks marked as Safety-Critical (e.g. switch rail fractures, point detection failure, contact wire cuts) shall receive an automatic score boost (minimum 85/100) and an immutable <b>must-schedule</b> flag.", bullet_style))

    story.append(Paragraph("3.3 Feature 3 — Constraint-Based Block Optimization (FR-3)", h2_style))
    story.append(Paragraph("<b>FR-3.1:</b> The optimizer shall use Constraint Satisfaction Programming (CP-SAT) to maximize priority coverage while minimizing train delay minutes:", bullet_style))
    
    obj_box = (
        "<b>Maximize:</b> SUM(Priority_i * x_iw) - alpha * TrainDelayMinutes - beta * AssetDowntime + gamma * JointBlockBonus"
    )
    story.append(Paragraph(obj_box, code_style))
    story.append(Paragraph("<b>FR-3.2 Hard Safety Constraints:</b>", h3_style))
    story.append(Paragraph("• Window duration must accommodate task duration plus statutory setup and clearance safety margins (0.5 hr).", bullet_style))
    story.append(Paragraph("• Traction (OHE) tasks requiring power shutdowns shall only be scheduled in windows with power disconnection clearance.", bullet_style))
    story.append(Paragraph("• Incompatible activities (e.g., heavy track machine movement vs. live OHE work) shall never be scheduled in overlapping sections.", bullet_style))
    story.append(Paragraph("<b>FR-3.3 Joint Block Synthesis:</b> Compatible multi-department tasks in identical corridor windows shall be merged into unified <b>Joint Blocks</b>, reporting exact duplicate track closures eliminated.", bullet_style))

    story.append(Paragraph("3.4 Feature 4 — Multi-Horizon Advisory Planning & Approval (FR-4 & FR-6)", h2_style))
    story.append(Paragraph("<b>FR-4.1:</b> The system shall generate <b>Monthly Strategic Plans</b> (30 days) for clearing backlog defects and <b>Weekly Tactical Plans</b> (7 days) with exact hour-by-hour windows.", bullet_style))
    story.append(Paragraph("<b>FR-6.1:</b> Plan states shall strictly follow the governance lifecycle: <code>Draft -> Proposed -> Sanctioned/Approved -> Published -> Executed</code>.", bullet_style))
    story.append(Paragraph("<b>FR-6.2:</b> The competent authority shall have override authority to accept, modify, or reject plans with required audit trail notes.", bullet_style))

    story.append(Paragraph("3.5 Feature 5 — Visualization, Audit & Benchmarking (FR-5, FR-7, FR-9)", h2_style))
    story.append(Paragraph("<b>FR-5.1:</b> The system shall display section-wise Gantt timelines color-coded by department: 🔵 Engineering (Blue), 🟢 S&T (Green), 🟠 Traction (Orange), 🟣 Joint Blocks (Purple).", bullet_style))
    story.append(Paragraph("<b>FR-7.1:</b> The system shall maintain an immutable, append-only audit trail recording user identity, timestamps, state transitions, and parameter overrides.", bullet_style))
    story.append(Paragraph("<b>FR-9.1:</b> The system shall provide an automated Benchmark Simulator comparing ABPS schedules against conventional decentralized first-come-first-served practices on identical datasets.", bullet_style))

    # ------------------ SECTION 4 ------------------
    story.append(Spacer(1, 8))
    story.append(Paragraph("4. Non-Functional Requirements & Metrics", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=border_col, spaceBefore=2, spaceAfter=8))
    
    nfr_data = [
        [Paragraph("<b>Identifier</b>", table_header_style), Paragraph("<b>Requirement Description</b>", table_header_style), Paragraph("<b>Target Metric / Standard</b>", table_header_style)],
        [Paragraph("<b>PERF-1</b>", table_cell_style), Paragraph("Monthly Optimization Runtime (50 sections, 2000 tasks)", table_cell_style), Paragraph("Best feasible plan returned within 300 seconds", table_cell_style)],
        [Paragraph("<b>PERF-2</b>", table_cell_style), Paragraph("Weekly Optimization Runtime (20 sections, 500 tasks)", table_cell_style), Paragraph("Execution completes within 120 seconds", table_cell_style)],
        [Paragraph("<b>SAF-1</b>", table_cell_style), Paragraph("Advisory Recommendation Guardrail", table_cell_style), Paragraph("100% of generated plan outputs display mandatory sanction disclaimer", table_cell_style)],
        [Paragraph("<b>SAF-2</b>", table_cell_style), Paragraph("Hard Constraint Verification", table_cell_style), Paragraph("Zero safety constraint violations permitted in proposed plans", table_cell_style)],
        [Paragraph("<b>SEC-1</b>", table_cell_style), Paragraph("Password & Token Cryptographic Security", table_cell_style), Paragraph("Salted SHA-256 password hashing + Stateless JWT Bearer tokens", table_cell_style)],
        [Paragraph("<b>QA-1</b>", table_cell_style), Paragraph("System Operational Availability", table_cell_style), Paragraph("99.5% uptime during train control planning shifts", table_cell_style)]
    ]
    t_nfr = Table(nfr_data, colWidths=[80, 244, 180])
    t_nfr.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), blue),
        ('GRID', (0,0), (-1,-1), 0.5, border_col),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_nfr)

    # ------------------ SECTION 5 ------------------
    story.append(Spacer(1, 8))
    story.append(Paragraph("5. Project Team & Acknowledgments", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=border_col, spaceBefore=2, spaceAfter=8))
    
    team_data = [
        [Paragraph("<b>Team Member Name</b>", table_header_style), Paragraph("<b>Assigned System Module</b>", table_header_style), Paragraph("<b>Key Contributions</b>", table_header_style)],
        [Paragraph("<b>Krish Desai</b> (Lead)", table_cell_style), Paragraph("Backend & Optimization Engine", table_cell_style), Paragraph("FastAPI endpoints, CP-SAT optimizer, DB schema, deployment.", table_cell_style)],
        [Paragraph("<b>Krish Mittal</b>", table_cell_style), Paragraph("AI Scoring & Data Modelling", table_cell_style), Paragraph("Multi-factor weighting formula, synthetic data, benchmark analytics.", table_cell_style)],
        [Paragraph("<b>Krishna Rathore</b>", table_cell_style), Paragraph("Frontend UI & Verification", table_cell_style), Paragraph("Executive dashboard, Gantt charts, override workflows, documentation.", table_cell_style)]
    ]
    t_team = Table(team_data, colWidths=[130, 150, 224])
    t_team.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('GRID', (0,0), (-1,-1), 0.5, border_col),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_team)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"✅ Generated clean highlighted SRS PDF: {filename}")

if __name__ == "__main__":
    output_pdf = r"c:\Users\Hp\OneDrive\Desktop\railway system\ABPS_Software_Requirements_Specification.pdf"
    build_srs_pdf(output_pdf)

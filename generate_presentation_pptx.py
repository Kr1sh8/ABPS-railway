import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck(filename):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # Elegant Color Palette
    c_navy = RGBColor(11, 37, 69)      # #0b2545
    c_blue = RGBColor(19, 64, 116)     # #134074
    c_btn_blue = RGBColor(29, 78, 216) # #1d4ed8
    c_btn_green = RGBColor(21, 128, 61)# #15803d
    c_gold = RGBColor(244, 162, 97)    # #f4a261
    c_dark = RGBColor(15, 23, 42)      # #0f172a
    c_slate = RGBColor(71, 85, 105)    # #475569
    c_light = RGBColor(248, 250, 252)  # #f8fafc
    c_white = RGBColor(255, 255, 255)
    c_purple = RGBColor(147, 51, 234)  # #9333ea
    c_card_bg = RGBColor(241, 245, 249)# #f1f5f9

    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, category_text="INDIAN RAILWAYS • CENTRAL MAINTENANCE CONTROL"):
        h_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15))
        h_shape.fill.solid()
        h_shape.fill.fore_color.rgb = c_navy
        h_shape.line.fill.background()

        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.15), Inches(13.333), Inches(0.06))
        line.fill.solid()
        line.fill.fore_color.rgb = c_gold
        line.line.fill.background()

        tf = h_shape.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.8)
        tf.margin_top = Inches(0.18)
        
        p1 = tf.paragraphs[0]
        p1.text = category_text.upper()
        p1.font.name = "Arial"
        p1.font.size = Pt(9.5)
        p1.font.bold = True
        p1.font.color.rgb = c_gold

        p2 = tf.add_paragraph()
        p2.text = title_text
        p2.font.name = "Arial"
        p2.font.size = Pt(20)
        p2.font.bold = True
        p2.font.color.rgb = c_white

    def add_card(slide, left, top, width, height, title, body_bullets, border_color=None, bg_color=None):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color or c_white
        if border_color:
            shape.line.color.rgb = border_color
            shape.line.width = Pt(1.5)
        else:
            shape.line.color.rgb = RGBColor(226, 232, 240)
            shape.line.width = Pt(1)

        tf = shape.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.22)
        tf.margin_bottom = Inches(0.2)

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = border_color or c_navy

        for bullet in body_bullets:
            p_b = tf.add_paragraph()
            p_b.text = "• " + bullet
            p_b.font.name = "Calibri"
            p_b.font.size = Pt(10.5)
            p_b.font.color.rgb = c_slate
            p_b.space_before = Pt(4)

        return shape

    # ==============================================================
    # SLIDE 1: TITLE SLIDE (WITH CRISP WHITE CARDS & STANDOUT BUTTONS)
    # ==============================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = c_navy
    bg1.line.fill.background()

    # Title header text
    tbox = s1.shapes.add_textbox(Inches(0.9), Inches(0.4), Inches(11.5), Inches(1.8))
    tf1 = tbox.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "MINISTRY OF RAILWAYS | PROBLEM STATEMENT 26027"
    p0.font.name = "Arial"
    p0.font.size = Pt(10.5)
    p0.font.bold = True
    p0.font.color.rgb = c_gold

    p1 = tf1.add_paragraph()
    p1.text = "Automatic Block Planning System (ABPS)"
    p1.font.name = "Arial"
    p1.font.size = Pt(28)
    p1.font.bold = True
    p1.font.color.rgb = c_white
    p1.space_before = Pt(3)

    p2 = tf1.add_paragraph()
    p2.text = "AI-Driven Multi-Department Maintenance Scheduling & Corridor Coordination"
    p2.font.name = "Calibri"
    p2.font.size = Pt(14)
    p2.font.color.rgb = RGBColor(144, 224, 239)
    p2.space_before = Pt(3)

    # CRISP WHITE HIGH-CONTRAST CARD FOR LINKS
    link_container = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(2.35), Inches(11.5), Inches(2.7))
    link_container.fill.solid()
    link_container.fill.fore_color.rgb = c_white
    link_container.line.color.rgb = c_gold
    link_container.line.width = Pt(2)

    lctf = link_container.text_frame
    lctf.margin_left = Inches(0.4)
    lctf.margin_top = Inches(0.2)
    lcp0 = lctf.paragraphs[0]
    lcp0.text = "🔗 OFFICIAL PROJECT REPOSITORY & LIVE DEPLOYMENT (CLICKABLE BUTTONS):"
    lcp0.font.name = "Arial"
    lcp0.font.size = Pt(12)
    lcp0.font.bold = True
    lcp0.font.color.rgb = c_navy

    # BUTTON 1: GITHUB REPO (HIGH CONTRAST BLUE BUTTON)
    btn_gh = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.3), Inches(2.95), Inches(10.7), Inches(0.85))
    btn_gh.fill.solid()
    btn_gh.fill.fore_color.rgb = c_btn_blue
    btn_gh.line.color.rgb = RGBColor(30, 58, 138)
    btn_gh.line.width = Pt(1.5)
    btn_gh.click_action.hyperlink.address = "https://github.com/Kr1sh8/ABPS-railway"

    tf_gh = btn_gh.text_frame
    tf_gh.word_wrap = True
    tf_gh.margin_left = Inches(0.3)
    tf_gh.margin_top = Inches(0.12)
    
    p_gh1 = tf_gh.paragraphs[0]
    p_gh1.text = "📂 CLICK HERE TO OPEN GITHUB REPOSITORY:"
    p_gh1.font.name = "Arial"
    p_gh1.font.size = Pt(10.5)
    p_gh1.font.bold = True
    p_gh1.font.color.rgb = c_gold

    p_gh2 = tf_gh.add_paragraph()
    p_gh2.space_before = Pt(2)
    run_gh = p_gh2.add_run()
    run_gh.text = "https://github.com/Kr1sh8/ABPS-railway"
    run_gh.font.name = "Arial"
    run_gh.font.size = Pt(14)
    run_gh.font.bold = True
    run_gh.font.underline = True
    run_gh.font.color.rgb = c_white
    run_gh.hyperlink.address = "https://github.com/Kr1sh8/ABPS-railway"

    # BUTTON 2: DIRECT LIVE WEB PORTAL (HIGH CONTRAST EMERALD GREEN BUTTON)
    btn_app = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.3), Inches(3.95), Inches(10.7), Inches(0.85))
    btn_app.fill.solid()
    btn_app.fill.fore_color.rgb = c_btn_green
    btn_app.line.color.rgb = RGBColor(20, 83, 45)
    btn_app.line.width = Pt(1.5)
    btn_app.click_action.hyperlink.address = "https://kr1sh8.github.io/ABPS-railway/"

    tf_app = btn_app.text_frame
    tf_app.word_wrap = True
    tf_app.margin_left = Inches(0.3)
    tf_app.margin_top = Inches(0.12)
    
    p_app1 = tf_app.paragraphs[0]
    p_app1.text = "🌐 CLICK HERE TO OPEN LIVE WORKING WEB APP (ZERO INSTALL):"
    p_app1.font.name = "Arial"
    p_app1.font.size = Pt(10.5)
    p_app1.font.bold = True
    p_app1.font.color.rgb = RGBColor(254, 240, 138)

    p_app2 = tf_app.add_paragraph()
    p_app2.space_before = Pt(2)
    run_app = p_app2.add_run()
    run_app.text = "https://kr1sh8.github.io/ABPS-railway/   (Credentials: admin / admin123)"
    run_app.font.name = "Arial"
    run_app.font.size = Pt(13)
    run_app.font.bold = True
    run_app.font.underline = True
    run_app.font.color.rgb = c_white
    run_app.hyperlink.address = "https://kr1sh8.github.io/ABPS-railway/"

    # CRISP WHITE HIGH-CONTRAST CARD FOR TEAM MEMBERS
    team_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(5.25), Inches(11.5), Inches(1.9))
    team_card.fill.solid()
    team_card.fill.fore_color.rgb = c_white
    team_card.line.color.rgb = RGBColor(203, 213, 225)
    team_card.line.width = Pt(1.5)

    ttf = team_card.text_frame
    ttf.word_wrap = True
    ttf.margin_left = Inches(0.4)
    ttf.margin_top = Inches(0.18)

    tp0 = ttf.paragraphs[0]
    tp0.text = "👥 PROJECT DEVELOPMENT TEAM (COMPUTER SCIENCE & ENGINEERING):"
    tp0.font.name = "Arial"
    tp0.font.size = Pt(11)
    tp0.font.bold = True
    tp0.font.color.rgb = c_navy

    tp1 = ttf.add_paragraph()
    tp1.text = "1. Krish Desai (Project Lead) — Backend Architecture, CP-SAT Optimization Engine & API Services"
    tp1.font.name = "Calibri"
    tp1.font.size = Pt(11.5)
    tp1.font.bold = True
    tp1.font.color.rgb = c_dark
    tp1.space_before = Pt(3)

    tp2 = ttf.add_paragraph()
    tp2.text = "2. Krish Mittal — AI Priority Scoring Formulation, Data Pipelines & Comparative Benchmark Engine"
    tp2.font.name = "Calibri"
    tp2.font.size = Pt(11.5)
    tp2.font.bold = True
    tp2.font.color.rgb = c_dark
    tp2.space_before = Pt(2)

    tp3 = ttf.add_paragraph()
    tp3.text = "3. Krishna Rathore — Frontend Portal UI/UX, Interactive Gantt Timeline Visualizations & Quality Assurance"
    tp3.font.name = "Calibri"
    tp3.font.size = Pt(11.5)
    tp3.font.bold = True
    tp3.font.color.rgb = c_dark
    tp3.space_before = Pt(2)

    # ==============================================================
    # SLIDE 2: THE PROBLEM STATEMENT
    # ==============================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Executive Background: Problem Statement 26027")

    add_card(s2, Inches(0.8), Inches(1.6), Inches(3.6), Inches(5.2),
             "1. Disconnected Silos", [
                 "Track (Civil/Engg) tracks defects in TMS (Track Mgmt System).",
                 "Signalling (S&T) tracks faults in SMMS (Signals).",
                 "Overhead Equipment (TRD) tracks power in TDMS (Traction).",
                 "Each department operates isolated databases without communication."
             ], c_blue)

    add_card(s2, Inches(4.8), Inches(1.6), Inches(3.6), Inches(5.2),
             "2. The BDMS Bottleneck", [
                 "Every department applies for track closures ('Blocks') independently via BDMS portal.",
                 "Result: Track Dept halts trains at 10:00 AM.",
                 "Signal Dept halts trains at 4:00 PM on the same line.",
                 "Duplicate track closures lead to heavy delays for express and goods trains."
             ], c_gold)

    add_card(s2, Inches(8.8), Inches(1.6), Inches(3.7), Inches(5.2),
             "3. Impact on Operations", [
                 "Reduced Fixed Asset Uptime: High downtime of tracks.",
                 "Severe Train Punctuality Loss: Hundreds of lost train minutes.",
                 "Safety Vulnerability: Delayed overdue safety-critical defects.",
                 "Suboptimal Scheduling: No unified optimization layer."
             ], RGBColor(220, 38, 38))

    # ==============================================================
    # SLIDE 3: THE PROPOSED SOLUTION (ABPS)
    # ==============================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "The ABPS Solution: Intelligent Block Scheduling")

    add_card(s3, Inches(0.8), Inches(1.6), Inches(5.6), Inches(2.5),
             "📥 Multi-Source Ingestion", [
                 "Aggregates maintenance tasks across TMS, SMMS, and TDMS.",
                 "Integrates live train timetables & goods forecast from COA (Control Office).",
                 "Normalizes all data into a standardized corridor schema."
             ], c_blue)

    add_card(s3, Inches(6.8), Inches(1.6), Inches(5.7), Inches(2.5),
             "🎯 AI Priority Scoring Engine", [
                 "Applies mathematical formula (Severity, Urgency, Asset, Traffic).",
                 "Safety-Critical tasks receive an automated 'Must-Schedule' flag.",
                 "Provides 100% transparent explainability for every score."
             ], c_gold)

    add_card(s3, Inches(0.8), Inches(4.4), Inches(5.6), Inches(2.5),
             "⚙️ Joint-Block Optimization", [
                 "Uses Constraint Programming (Google OR-Tools CP-SAT).",
                 "Merges compatible multi-department tasks into unified Joint Blocks.",
                 "Enforces safety separation (e.g. OHE power off vs heavy track machine)."
             ], c_purple)

    add_card(s3, Inches(6.8), Inches(4.4), Inches(5.7), Inches(2.5),
             "📅 Multi-Horizon Advisory Schedulers", [
                 "Generates 30-day macro plans and 7-day exact corridor schedules.",
                 "Keeps Human-in-the-Loop: Sr. DEN / Sr. DOM review & sanction.",
                 "Real-time Benchmark Simulator showing quantitative improvement."
             ], c_btn_green)

    # ==============================================================
    # SLIDE 4: SYSTEM ARCHITECTURE
    # ==============================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Multi-Tiered Technical Architecture")

    add_card(s4, Inches(0.8), Inches(1.6), Inches(2.7), Inches(5.2),
             "Layer 1: Ingestion", [
                 "Connectors for legacy Indian Railways systems:",
                 "• TMS (Track Defects)",
                 "• SMMS (Signal Faults)",
                 "• TDMS (OHE Power)",
                 "• COA (Train Timetable)",
                 "CSV/JSON/REST Ingestion.",
                 "Master section registry matching assets across departments."
             ], c_blue)

    add_card(s4, Inches(3.8), Inches(1.6), Inches(2.7), Inches(5.2),
             "Layer 2: Intelligence", [
                 "Mathematical Priority Formulation (0 to 100).",
                 "Constraint Programming (OR-Tools CP-SAT).",
                 "Joint Block Merger: Detects overlapping department requests.",
                 "Hard constraint validator ensuring zero safety violations."
             ], c_gold)

    add_card(s4, Inches(6.8), Inches(1.6), Inches(2.7), Inches(5.2),
             "Layer 3: Services", [
                 "FastAPI Application Server.",
                 "JWT Authentication with salted SHA-256 hashes.",
                 "Stateful Plan Lifecycle (Draft, Sanctioned, Published).",
                 "Immutable append-only Audit Trail logging every action."
             ], c_purple)

    add_card(s4, Inches(9.8), Inches(1.6), Inches(2.7), Inches(5.2),
             "Layer 4: Presentation", [
                 "Responsive Web Dashboard.",
                 "Interactive Plotly & Chart.js Gantt charts.",
                 "Color-Coded Tracks:",
                 "🔵 Engg | 🟢 S&T | 🟠 TRD",
                 "🟣 Coordinated Joint Blocks",
                 "Live GitHub Pages + Streamlit interfaces."
             ], c_btn_green)

    # ==============================================================
    # SLIDE 5: AI SCORING & OPTIMIZATION FORMULATION
    # ==============================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Mathematical Formulations: Scoring & Optimization")

    f_box1 = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(11.7), Inches(2.4))
    f_box1.fill.solid()
    f_box1.fill.fore_color.rgb = c_light
    f_box1.line.color.rgb = c_blue
    f_box1.line.width = Pt(1.5)

    ftf1 = f_box1.text_frame
    ftf1.margin_left = Inches(0.4)
    ftf1.margin_top = Inches(0.2)
    
    fp1 = ftf1.paragraphs[0]
    fp1.text = "1. AI Priority Scoring Formula (IEEE SRS Feature 4.2)"
    fp1.font.bold = True
    fp1.font.size = Pt(13)
    fp1.font.color.rgb = c_navy

    fp2 = ftf1.add_paragraph()
    fp2.text = "Score = w1*Severity + w2*Urgency(Overdue) + w3*AssetCriticality + w4*TrafficDensity"
    fp2.font.name = "Courier"
    fp2.font.bold = True
    fp2.font.size = Pt(13)
    fp2.font.color.rgb = c_blue
    fp2.space_before = Pt(4)

    fp3 = ftf1.add_paragraph()
    fp3.text = "• Weights: Severity = 35%, Urgency = 30%, Asset Risk = 20%, Corridor Density = 15%\n" \
               "• Safety-Critical Flag: Defects causing derailment or collision risks receive automatic priority ≥ 85."
    fp3.font.size = Pt(11)
    fp3.font.color.rgb = c_slate
    fp3.space_before = Pt(4)

    f_box2 = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.3), Inches(11.7), Inches(2.5))
    f_box2.fill.solid()
    f_box2.fill.fore_color.rgb = c_light
    f_box2.line.color.rgb = c_purple
    f_box2.line.width = Pt(1.5)

    ftf2 = f_box2.text_frame
    ftf2.margin_left = Inches(0.4)
    ftf2.margin_top = Inches(0.2)

    f2p1 = ftf2.paragraphs[0]
    f2p1.text = "2. Optimization Objective & Constraints (IEEE SRS Feature 4.3)"
    f2p1.font.bold = True
    f2p1.font.size = Pt(13)
    f2p1.font.color.rgb = c_navy

    f2p2 = ftf2.add_paragraph()
    f2p2.text = "Maximize: SUM(Priority_i * x_iw) - alpha*TrainDelayMinutes - beta*AssetDowntime + gamma*JointBlockBonus"
    f2p2.font.name = "Courier"
    f2p2.font.bold = True
    f2p2.font.size = Pt(13)
    f2p2.font.color.rgb = c_purple
    f2p2.space_before = Pt(4)

    f2p3 = ftf2.add_paragraph()
    f2p3.text = "• Capacity & Duration: Window duration ≥ Task duration + 30 min safety setup/clearance margin.\n" \
               "• Power Block Constraint: Overhead traction tasks only scheduled when power disconnect is authorized.\n" \
               "• Incompatibility Matrix: Prevents conflicting machinery (e.g. rail grinding vs OHE ladder car) on same track."
    f2p3.font.size = Pt(11)
    f2p3.font.color.rgb = c_slate
    f2p3.space_before = Pt(4)

    # ==============================================================
    # SLIDE 6: BENCHMARK & EVALUATION RESULTS
    # ==============================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Quantitative Validation: AI vs. Manual Practice")

    m1 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(3.6), Inches(1.8))
    m1.fill.solid()
    m1.fill.fore_color.rgb = RGBColor(240, 253, 244)
    m1.line.color.rgb = c_btn_green
    m1.line.width = Pt(2)
    m1.text_frame.margin_left = Inches(0.3)
    m1.text_frame.margin_top = Inches(0.25)
    p = m1.text_frame.paragraphs[0]
    p.text = "TASKS SCHEDULED"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = c_btn_green
    p2 = m1.text_frame.add_paragraph()
    p2.text = "184 Tasks (+24.3%)"
    p2.font.size = Pt(22)
    p2.font.bold = True
    p2.font.color.rgb = c_dark
    p3 = m1.text_frame.add_paragraph()
    p3.text = "vs 148 tasks in manual planning"
    p3.font.size = Pt(10)
    p3.font.color.rgb = c_slate

    m2 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.8), Inches(1.6), Inches(3.6), Inches(1.8))
    m2.fill.solid()
    m2.fill.fore_color.rgb = RGBColor(250, 245, 255)
    m2.line.color.rgb = c_purple
    m2.line.width = Pt(2)
    m2.text_frame.margin_left = Inches(0.3)
    m2.text_frame.margin_top = Inches(0.25)
    p = m2.text_frame.paragraphs[0]
    p.text = "JOINT BLOCKS FORMED"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = c_purple
    p2 = m2.text_frame.add_paragraph()
    p2.text = "26 Blocks Saved"
    p2.font.size = Pt(22)
    p2.font.bold = True
    p2.font.color.rgb = c_dark
    p3 = m2.text_frame.add_paragraph()
    p3.text = "26 duplicate track shutdowns avoided"
    p3.font.size = Pt(10)
    p3.font.color.rgb = c_slate

    m3 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.8), Inches(1.6), Inches(3.7), Inches(1.8))
    m3.fill.solid()
    m3.fill.fore_color.rgb = RGBColor(239, 246, 255)
    m3.line.color.rgb = c_blue
    m3.line.width = Pt(2)
    m3.text_frame.margin_left = Inches(0.3)
    m3.text_frame.margin_top = Inches(0.25)
    p = m3.text_frame.paragraphs[0]
    p.text = "TRAIN DELAY REDUCTION"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = c_blue
    p2 = m3.text_frame.add_paragraph()
    p2.text = "-38.5% Delays"
    p2.font.size = Pt(22)
    p2.font.bold = True
    p2.font.color.rgb = c_dark
    p3 = m3.text_frame.add_paragraph()
    p3.text = "212 lost train minutes saved per section"
    p3.font.size = Pt(10)
    p3.font.color.rgb = c_slate

    # Comparison Table
    t_shape = s6.shapes.add_table(5, 4, Inches(0.8), Inches(3.8), Inches(11.7), Inches(3.0))
    table = t_shape.table
    table.columns[0].width = Inches(3.5)
    table.columns[1].width = Inches(2.7)
    table.columns[2].width = Inches(2.7)
    table.columns[3].width = Inches(2.8)

    headers = ["Key Evaluation Metric", "Manual Departmental Planning", "ABPS Coordinated AI", "Operational Improvement"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = c_navy
        for p in cell.text_frame.paragraphs:
            p.font.bold = True
            p.font.size = Pt(10)
            p.font.color.rgb = c_white

    rows = [
        ["Tasks Successfully Scheduled", "148 Tasks", "184 Tasks", "+24.3% More Defects Cleared"],
        ["Corridor Blocks (Track Closures)", "148 Closures", "122 Closures", "26 Closures Avoided (-17.5%)"],
        ["Train Minutes Lost to Delays", "552 Minutes", "340 Minutes", "212 Minutes Saved (-38.5%)"],
        ["Fixed Infrastructure Availability", "84.2%", "98.4%", "+14.2% Track Operational Uptime"]
    ]

    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx + 1, c_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = c_white if r_idx % 2 == 0 else c_light
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(9.5)
                p.font.color.rgb = c_btn_green if c_idx == 3 else c_dark
                if c_idx in (2, 3):
                    p.font.bold = True

    # ==============================================================
    # SLIDE 7: LIVE SYSTEM DEMO WALKTHROUGH
    # ==============================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Step-by-Step System Operation Workflow")

    add_card(s7, Inches(0.8), Inches(1.6), Inches(2.7), Inches(5.2),
             "Step 1: Ingestion", [
                 "Log in as Central Controller (admin / admin123).",
                 "Dashboard loads 201 maintenance tasks across 15 corridors.",
                 "Filter by department (Track, Signals, OHE).",
                 "Click 'Report New Defect' to test manual user entry."
             ], c_blue)

    add_card(s7, Inches(3.8), Inches(1.6), Inches(2.7), Inches(5.2),
             "Step 2: Timetable Check", [
                 "Open 'Corridor Windows' tab.",
                 "Inspect gaps between scheduled express and freight trains.",
                 "Identifies safe night blocks (00:00-04:00) and midday lulls.",
                 "Ensures traffic and power disconnection permits."
             ], c_gold)

    add_card(s7, Inches(6.8), Inches(1.6), Inches(2.7), Inches(5.2),
             "Step 3: Run AI Optimizer", [
                 "Navigate to 'Block Plans (AI)'.",
                 "Select 7-Day or 30-Day horizon.",
                 "Click '🚀 Run Optimizer & Generate Plan'.",
                 "Constraint solver outputs multi-department joint blocks.",
                 "Interactive color-coded Gantt timeline rendered instantly."
             ], c_purple)

    add_card(s7, Inches(9.8), Inches(1.6), Inches(2.7), Inches(5.2),
             "Step 4: Sanction & Audit", [
                 "Sr. DEN clicks '✅ Sanction & Approve Plan'.",
                 "Click '📢 Publish' to transmit to station controllers.",
                 "Inspect 'Audit Trail' tab for tamper-evident logging.",
                 "Run 'AI Benchmark' to verify measurable KPI gains."
             ], c_btn_green)

    # ==============================================================
    # SLIDE 8: SUMMARY & CONCLUSION (CLEAR WHITE CARD WITH BUTTONS)
    # ==============================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Project Summary & Submission Details")

    add_card(s8, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2),
             "🌟 Key Technical Contributions", [
                 "1. Solved Problem Statement 26027 by integrating decentralized maintenance data (TMS, SMMS, TDMS) with train movement (COA).",
                 "2. Replaced manual guesswork with mathematical priority scoring and constraint satisfaction (CP-SAT).",
                 "3. Introduced Joint Block co-utilization, significantly slashing train punctuality loss.",
                 "4. Built full-stack dual deployment: Streamlit Python engine + High-speed Web App on GitHub Pages.",
                 "5. Complete IEEE 830 documentation, test suites, and SE lab architecture diagrams (DFD 0/1, Use Case, Class, Swimlane, Sequence)."
             ], c_blue)

    # Clean White Card on Slide 8
    link_card_end = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2))
    link_card_end.fill.solid()
    link_card_end.fill.fore_color.rgb = c_white
    link_card_end.line.color.rgb = c_gold
    link_card_end.line.width = Pt(1.5)

    etf = link_card_end.text_frame
    etf.word_wrap = True
    etf.margin_left = Inches(0.3)
    etf.margin_top = Inches(0.2)

    ep0 = etf.paragraphs[0]
    ep0.text = "📦 Evaluation Resources & Verification (Clickable Buttons):"
    ep0.font.name = "Arial"
    ep0.font.size = Pt(12)
    ep0.font.bold = True
    ep0.font.color.rgb = c_navy

    # Slide 8 Button 1 (GitHub)
    btn_end_gh = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.1), Inches(2.2), Inches(5.1), Inches(0.75))
    btn_end_gh.fill.solid()
    btn_end_gh.fill.fore_color.rgb = c_btn_blue
    btn_end_gh.line.color.rgb = RGBColor(30, 58, 138)
    btn_end_gh.click_action.hyperlink.address = "https://github.com/Kr1sh8/ABPS-railway"

    tf_egh = btn_end_gh.text_frame
    tf_egh.margin_left = Inches(0.2)
    tf_egh.margin_top = Inches(0.12)
    p_e1 = tf_egh.paragraphs[0]
    p_e1.text = "📂 Open GitHub Repository (Click Here)"
    p_e1.font.name = "Arial"
    p_e1.font.size = Pt(11.5)
    p_e1.font.bold = True
    p_e1.font.color.rgb = c_white
    p_e2 = tf_egh.add_paragraph()
    p_e2.text = "https://github.com/Kr1sh8/ABPS-railway"
    p_e2.font.size = Pt(9.5)
    p_e2.font.color.rgb = c_gold
    p_e2.font.underline = True

    # Slide 8 Button 2 (Live App)
    btn_end_app = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.1), Inches(3.05), Inches(5.1), Inches(0.75))
    btn_end_app.fill.solid()
    btn_end_app.fill.fore_color.rgb = c_btn_green
    btn_end_app.line.color.rgb = RGBColor(20, 83, 45)
    btn_end_app.click_action.hyperlink.address = "https://kr1sh8.github.io/ABPS-railway/"

    tf_eapp = btn_end_app.text_frame
    tf_eapp.margin_left = Inches(0.2)
    tf_eapp.margin_top = Inches(0.12)
    p_ea1 = tf_eapp.paragraphs[0]
    p_ea1.text = "🌐 Open Live Working Web App (Click Here)"
    p_ea1.font.name = "Arial"
    p_ea1.font.size = Pt(11.5)
    p_ea1.font.bold = True
    p_ea1.font.color.rgb = c_white
    p_ea2 = tf_eapp.add_paragraph()
    p_ea2.text = "https://kr1sh8.github.io/ABPS-railway/"
    p_ea2.font.size = Pt(9.5)
    p_ea2.font.color.rgb = RGBColor(254, 240, 138)
    p_ea2.font.underline = True

    # Slide 8 Team Members Details
    s8_team_box = s8.shapes.add_textbox(Inches(7.1), Inches(3.9), Inches(5.1), Inches(2.6))
    sttf = s8_team_box.text_frame
    sttf.word_wrap = True
    stp1 = sttf.paragraphs[0]
    stp1.text = "👥 Team Members (CSE Department):"
    stp1.font.bold = True
    stp1.font.size = Pt(11)
    stp1.font.color.rgb = c_navy
    
    members = [
        "1. Krish Desai (Project Lead) - Backend & Optimizer",
        "2. Krish Mittal - AI Priority Scoring & Benchmarks",
        "3. Krishna Rathore - Frontend UI/UX & Quality Assurance"
    ]
    for m in members:
        pm = sttf.add_paragraph()
        pm.text = "• " + m
        pm.font.size = Pt(10)
        pm.font.color.rgb = c_dark
        pm.font.bold = True
        pm.space_before = Pt(3)

    prs.save(filename)
    print(f"✅ Generated high-contrast clickable presentation PPTX: {filename}")

if __name__ == "__main__":
    output_pptx = r"c:\Users\Hp\OneDrive\Desktop\railway system\ABPS_Project_Presentation.pptx"
    create_deck(output_pptx)

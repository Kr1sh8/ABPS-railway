import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def create_github_links_pdf(output_path="ABPS_Project_GitHub_Links.pdf"):
    margin = 40
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Premium color palette matching Medi-Caps & Railway theme
    primary_color = colors.HexColor("#0f2744")    # Deep Navy
    text_dark = colors.HexColor("#1e293b")        # Slate 800
    text_muted = colors.HexColor("#475569")       # Slate 600
    border_color = colors.HexColor("#cbd5e1")     # Slate 300
    bg_light = colors.HexColor("#f8fafc")         # Slate 50
    bg_header = colors.HexColor("#f1f5f9")        # Slate 100
    link_blue = colors.HexColor("#0366d6")        # GitHub link blue

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color,
        alignment=TA_LEFT,
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_muted,
        alignment=TA_LEFT,
        spaceAfter=12
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=8
    )

    th_style = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=text_dark
    )

    td_style = ParagraphStyle(
        'TD',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_dark
    )

    link_style = ParagraphStyle(
        'LinkStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=link_blue
    )

    content_item_title = ParagraphStyle(
        'ItemTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=primary_color
    )

    content_item_desc = ParagraphStyle(
        'ItemDesc',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=text_muted
    )

    story = []

    # Title & Subtitle Header
    story.append(Paragraph("ABPS Project — GitHub Links", title_style))
    story.append(Paragraph("Software Engineering Laboratory (CS3CO40-P) &nbsp;|&nbsp; Project Submission", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceBefore=0, spaceAfter=14))

    # Metadata Table
    # Requirement: All 3 members listed, Krish Desai in first place, NO ONE labeled as leader
    meta_data = [
        [Paragraph("<b>Students / Team</b>", th_style), 
         Paragraph("<b>Krish Desai</b> &nbsp;•&nbsp; <b>Krish Mittal</b> &nbsp;•&nbsp; <b>Krishna Rathore</b>", td_style)],
        [Paragraph("<b>Program</b>", th_style), 
         Paragraph("B.Tech CSE, Medi-Caps University", td_style)],
        [Paragraph("<b>Cohort</b>", th_style), 
         Paragraph("CS3CO40 (P) — Software Engineering (P) — 5CSE-J1", td_style)],
        [Paragraph("<b>Problem Domain</b>", th_style), 
         Paragraph("Ministry of Railways — PS 26027: Automatic Block Planning System (ABPS)", td_style)]
    ]

    col_widths_meta = [125, 390]
    meta_table = Table(meta_data, colWidths=col_widths_meta)
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), bg_header),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), text_dark),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.75, border_color),
    ]))
    story.append(meta_table)

    story.append(Spacer(1, 12))

    # Project Links Section
    story.append(Paragraph("Project Links (click to open)", section_heading))

    # Usable width is 515.28 pt: colWidths = [140, 245, 130]
    links_data = [
        [
            Paragraph("<b>GitHub Repository</b>", th_style),
            Paragraph('<a href="https://github.com/Kr1sh8/ABPS-railway" color="#0366d6"><u>https://github.com/Kr1sh8/ABPS-railway</u></a>', link_style),
            Paragraph("Full source, lab diagrams & commits", content_item_desc)
        ],
        [
            Paragraph("<b>Live Web Application</b>", th_style),
            Paragraph('<a href="https://kr1sh8.github.io/ABPS-railway/" color="#0366d6"><u>https://kr1sh8.github.io/ABPS-railway/</u></a>', link_style),
            Paragraph("Direct working site (no install needed)", content_item_desc)
        ],
        [
            Paragraph("<b>README (setup and run steps)</b>", th_style),
            Paragraph('<a href="https://github.com/Kr1sh8/ABPS-railway#readme" color="#0366d6"><u>https://github.com/Kr1sh8/ABPS-railway#readme</u></a>', link_style),
            Paragraph("System setup, architecture & run guide", content_item_desc)
        ],
        [
            Paragraph("<b>Download full source as ZIP</b>", th_style),
            Paragraph('<a href="https://github.com/Kr1sh8/ABPS-railway/archive/HEAD.zip" color="#0366d6"><u>https://github.com/Kr1sh8/ABPS-railway/archive/HEAD.zip</u></a>', link_style),
            Paragraph("Instant repo source archive download", content_item_desc)
        ]
    ]

    links_col_widths = [140, 245, 130]
    links_table = Table(links_data, colWidths=links_col_widths)
    links_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), bg_header),
        ('BACKGROUND', (1, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 9),
        ('RIGHTPADDING', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.75, border_color),
    ]))
    story.append(links_table)

    story.append(Spacer(1, 12))

    # Contents of this ZIP Section
    story.append(Paragraph("Contents of this ZIP", section_heading))

    zip_items_data = [
        [
            Paragraph("•", th_style),
            Paragraph("<b>ABPS_Project_Presentation.pptx</b>", content_item_title),
            Paragraph("— project presentation (16:9 widescreen, 8 slides covering architecture, formulation, & dual deployment)", content_item_desc)
        ],
        [
            Paragraph("•", th_style),
            Paragraph("<b>ABPS_Software_Requirements_Specification.pdf</b>", content_item_title),
            Paragraph("— Software Requirements Specification (complete IEEE 830 compliant SRS document)", content_item_desc)
        ],
        [
            Paragraph("•", th_style),
            Paragraph("<b>ABPS_Project_GitHub_Links.pdf</b>", content_item_title),
            Paragraph("— project links & evaluation access guide (clickable URLs for evaluator quick-access)", content_item_desc)
        ],
        [
            Paragraph("•", th_style),
            Paragraph("<b>Source_Code/</b>", content_item_title),
            Paragraph("— complete working project (FastAPI backend, Streamlit frontend, public web, SQLite DB; run <code>start.bat</code> to launch)", content_item_desc)
        ]
    ]

    zip_table = Table(zip_items_data, colWidths=[18, 232, 265])
    zip_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_light),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.75, border_color),
    ]))
    story.append(zip_table)

    story.append(Spacer(1, 14))

    # Evaluation Quick-Start Callout Box
    note_para = Paragraph(
        "<b>Evaluation Quick-Start:</b> The live web application is actively deployed and ready for immediate testing at "
        "<a href=\"https://kr1sh8.github.io/ABPS-railway/\" color=\"#0366d6\"><u>https://kr1sh8.github.io/ABPS-railway/</u></a>. "
        "To run the complete full-stack environment locally, extract <code>Source_Code/</code> and double-click <code>start.bat</code>.",
        ParagraphStyle(
            'NoteText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=12.5,
            textColor=colors.HexColor("#0f3d64")
        )
    )

    note_table = Table([[note_para]], colWidths=[515])
    note_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#f0f9ff")),
        ('BOX', (0, 0), (0, 0), 1, colors.HexColor("#38bdf8")),
        ('TOPPADDING', (0, 0), (0, 0), 7),
        ('BOTTOMPADDING', (0, 0), (0, 0), 7),
        ('LEFTPADDING', (0, 0), (0, 0), 10),
        ('RIGHTPADDING', (0, 0), (0, 0), 10),
    ]))
    story.append(note_table)

    doc.build(story)
    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    create_github_links_pdf()

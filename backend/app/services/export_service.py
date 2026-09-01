"""
export_service.py
─────────────────
Generates a highly detailed, professional Blueprint PDF document containing
the full SDLC plan: Requirements, Architecture, Database, and Documentation.
"""

import io
from datetime import datetime
from typing import List

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, HRFlowable, NextPageTemplate,
    PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether,
)
from reportlab.platypus.flowables import Flowable

from app.models.requirements import ProjectContext

PAGE_W, PAGE_H = A4
LM = 2.0 * cm
RM = 2.0 * cm
TM = 3.5 * cm
BM = 3.0 * cm
BODY_W = PAGE_W - LM - RM

# Professional Corporate Palette
PRIMARY = HexColor("#003366")
SECONDARY = HexColor("#00509E")
BLUE_L = HexColor("#F0F4F8")
BORDER = HexColor("#BDC3C7")
ROW_A = HexColor("#FFFFFF")
ROW_B = HexColor("#F8F9FA")


def _safe(text: str) -> str:
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(_safe(text), style)

def _cover_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, PAGE_H - 8.0 * cm, PAGE_W, 8.0 * cm, fill=1, stroke=0)
    canvas.restoreState()

def _body_page(canvas, doc):
    canvas.saveState()
    proj = getattr(doc, "_project_name", "PROJECT")
    canvas.setStrokeColor(PRIMARY)
    canvas.setLineWidth(1.5)
    canvas.line(LM, PAGE_H - 2.0 * cm, PAGE_W - RM, PAGE_H - 2.0 * cm)
    canvas.setFont("Times-Bold", 8)
    canvas.setFillColor(PRIMARY)
    canvas.drawString(LM, PAGE_H - 1.8 * cm, "COMPREHENSIVE PROJECT BLUEPRINT")
    canvas.setFont("Times-Roman", 8)
    canvas.setFillColor(colors.HexColor("#444444"))
    canvas.drawRightString(PAGE_W - RM, PAGE_H - 1.8 * cm, proj.upper())

    canvas.setStrokeColor(PRIMARY)
    canvas.setLineWidth(1.0)
    canvas.line(LM, 1.5 * cm, PAGE_W - RM, 1.5 * cm)
    canvas.drawString(LM, 1.1 * cm, "BluePrint AI — SDLC Planner")
    canvas.drawCentredString(PAGE_W / 2, 1.1 * cm, str(doc.page))
    canvas.drawRightString(PAGE_W - RM, 1.1 * cm, datetime.now().strftime("%B %Y"))
    canvas.restoreState()

def _styles() -> dict:
    s = {}
    s["cover_title"] = ParagraphStyle("cover_title", fontName="Times-Bold", fontSize=28, textColor=colors.white, alignment=TA_CENTER, spaceAfter=12, leading=34)
    s["cover_sub"] = ParagraphStyle("cover_sub", fontName="Times-Roman", fontSize=14, textColor=colors.white, alignment=TA_CENTER, spaceAfter=6, leading=20)
    
    s["sec_head"] = ParagraphStyle("sec_head", fontName="Times-Bold", fontSize=18, textColor=PRIMARY, alignment=TA_LEFT, spaceBefore=24, spaceAfter=10, leading=22, keepWithNext=True)
    s["sub_head"] = ParagraphStyle("sub_head", fontName="Times-BoldItalic", fontSize=14, textColor=SECONDARY, alignment=TA_LEFT, spaceBefore=16, spaceAfter=8, leading=18, keepWithNext=True)
    
    s["body"] = ParagraphStyle("body", fontName="Times-Roman", fontSize=11, textColor=colors.black, alignment=TA_JUSTIFY, spaceAfter=8, leading=16)
    s["bullet"] = ParagraphStyle("bullet", fontName="Times-Roman", fontSize=11, textColor=colors.black, alignment=TA_JUSTIFY, spaceAfter=6, leading=16, leftIndent=16, firstLineIndent=-10)
    s["caption"] = ParagraphStyle("caption", fontName="Times-Bold", fontSize=10, textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=6, leading=14, keepWithNext=True)
    s["code"] = ParagraphStyle("code", fontName="Courier", fontSize=9, textColor=HexColor("#1A2744"), alignment=TA_LEFT, spaceAfter=4, leading=13, leftIndent=10, backColor=HexColor("#F8F9FA"), borderPad=6)
    return s

def _sec(roman: str, title: str, s: dict) -> List[Flowable]:
    return [
        Spacer(1, 6 * mm),
        _p(f"{roman}.\u2002{title.upper()}", s["sec_head"]),
        HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10),
    ]

def _sub(letter: str, title: str, s: dict) -> Flowable:
    return _p(f"{letter}.\u2002{title}", s["sub_head"])

def _callout(text: str) -> Table:
    p = Paragraph(_safe(text), ParagraphStyle("callout", fontName="Times-Italic", fontSize=11, textColor=PRIMARY, alignment=TA_JUSTIFY, leading=16))
    t = Table([[p]], colWidths=[BODY_W - 1 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLUE_L),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("BOX", (0, 0), (-1, -1), 1, PRIMARY),
        ("LEFTBORDER", (0, 0), (0, -1), 4, PRIMARY),
    ]))
    return t

def _std_table(rows, col_widths, s, caption: str = "") -> List[Flowable]:
    out = []
    if caption:
        out.append(_p(caption, s["caption"]))
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),
        ("FONTSIZE", (0, 1), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]
    for i in range(1, len(rows)):
        style.append(("BACKGROUND", (0, i), (-1, i), ROW_A if i % 2 == 1 else ROW_B))
    t.setStyle(TableStyle(style))
    out.append(t)
    out.append(Spacer(1, 6 * mm))
    return out


class ExportService:
    def generate_pdf(self, context: ProjectContext) -> bytes:
        buffer = io.BytesIO()
        s = _styles()
        
        req = context.requirements
        arch = context.architecture
        db = context.database
        docs = context.documentation

        project_name = (req.project_name if req else "UNTITLED").upper()

        doc = BaseDocTemplate(
            buffer, pagesize=A4, leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM,
            title=f"Blueprint: {project_name}"
        )
        doc._project_name = project_name

        frame = Frame(LM, BM, BODY_W, PAGE_H - TM - BM, id="body")
        doc.addPageTemplates([
            PageTemplate(id="Cover", frames=[frame], onPage=_cover_page),
            PageTemplate(id="Body", frames=[frame], onPage=_body_page)
        ])

        story: List[Flowable] = []

        # Cover
        story.append(Spacer(1, 2 * cm))
        story.append(_p(project_name, s["cover_title"]))
        story.append(Spacer(1, 5 * mm))
        story.append(_p("Comprehensive Master Project Blueprint", s["cover_sub"]))
        story.append(_p("End-to-End System Specifications & Documentation", s["cover_sub"]))
        story.append(Spacer(1, 25 * mm))

        meta_rows = [
            ["Document Type", "Master Blueprint / Technical Specification"],
            ["Project Name", project_name],
            ["Generated", datetime.now().strftime("%d %B %Y")],
            ["Framework", "BluePrint AI System Generator"],
        ]
        mt = Table(meta_rows, colWidths=[5 * cm, BODY_W - 5 * cm - 1 * cm])
        mt.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Times-Bold"),
            ("FONTNAME", (1, 0), (1, -1), "Times-Roman"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
            ("TEXTCOLOR", (1, 0), (1, -1), HexColor("#EEEEEE")),
            ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#1A4066")),
            ("PADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(mt)
        story.append(NextPageTemplate("Body"))
        story.append(PageBreak())

        # I. Executive Summary
        if docs or req:
            story.extend(_sec("I", "Executive Summary", s))
            story.append(_sub("A", "Problem Statement & Overview", s))
            overview_text = docs.project_overview if (docs and getattr(docs, "project_overview", None)) else (req.project_overview if req else "No overview provided.")
            story.append(_callout(overview_text))
            
            if req and req.objectives:
                story.append(_sub("B", "Core Objectives", s))
                for item in req.objectives:
                    story.append(Paragraph(f"\u2022\u2002{_safe(item)}", s["bullet"]))
            story.append(PageBreak())

        # II. Requirements
        if req:
            story.extend(_sec("II", "System Requirements", s))
            
            if req.functional_requirements:
                story.append(_sub("A", "Functional Requirements", s))
                for item in req.functional_requirements:
                    story.append(Paragraph(f"\u2022\u2002{_safe(item)}", s["bullet"]))
            
            if req.non_functional_requirements:
                story.append(_sub("B", "Non-Functional Requirements", s))
                for item in req.non_functional_requirements:
                    story.append(Paragraph(f"\u2022\u2002{_safe(item)}", s["bullet"]))
            
            if req.user_stories:
                story.append(_sub("C", "Key User Stories", s))
                for item in req.user_stories:
                    story.append(Paragraph(f"\u2022\u2002As a {item.role}, I want to {item.desire} so that {item.benefit}", s["bullet"]))
            
            story.append(_sub("D", "Technology Stack", s))
            ts = req.recommended_tech_stack
            ts_rows = [
                ["Layer", "Technology"],
                ["Frontend UI", _safe(ts.frontend if ts else "—")],
                ["Backend API", _safe(ts.backend if ts else "—")],
                ["Database", _safe(ts.database if ts else "—")],
                ["AI Framework", _safe(ts.ai_framework if ts else "—")],
            ]
            story.extend(_std_table(ts_rows, [5 * cm, BODY_W - 5 * cm - 1 * cm], s, "TABLE I. TECHNOLOGY STACK"))
            story.append(PageBreak())

        # III. Architecture
        if arch:
            story.extend(_sec("III", "System Architecture", s))
            story.append(_sub("A", "High Level Architecture", s))
            story.append(_p(arch.high_level_architecture or "No architecture overview.", s["body"]))
            
            story.append(_sub("B", "Component Modules Diagram", s))
            if arch.component_breakdown:
                c_rows = [["Module Name", "Dependencies", "Responsibilities"]]
                for comp in arch.component_breakdown:
                    deps = ", ".join(comp.dependencies) if getattr(comp, "dependencies", None) else "None"
                    c_rows.append([comp.name, deps, comp.description])
                story.extend(_std_table(c_rows, [3.5 * cm, 3.5 * cm, BODY_W - 7 * cm - 1 * cm], s, "TABLE II. COMPONENT MODULES"))

            story.append(_sub("C", "Data Flow & Processing", s))
            story.append(_p(arch.data_flow or "Data flow not defined.", s["body"]))
            story.append(PageBreak())

        # IV. Database
        if db:
            story.extend(_sec("IV", "Database Design", s))
            story.append(_sub("A", "Entity Relationship Schema", s))
            if db.entities:
                for idx, ent in enumerate(db.entities, 1):
                    ent_rows = [["Attribute", "Data Type / Definition"]]
                    for attr in ent.attributes:
                        if isinstance(attr, str):
                            parts = attr.split(" ", 1)
                            name = parts[0]
                            defn = parts[1] if len(parts) > 1 else "TEXT"
                        else:
                            name = attr.get('name', '')
                            defn = attr.get('type', 'TEXT')
                        ent_rows.append([name, defn])
                    story.extend(_std_table(ent_rows, [5 * cm, BODY_W - 5 * cm - 1 * cm], s, f"TABLE III-{idx}. ENTITY: {ent.name.upper()}"))
            else:
                story.append(_p("No entities defined.", s["body"]))
                
            story.append(_sub("B", "SQL DDL Schema", s))
            if db.sql_schema:
                story.append(Paragraph(_safe(db.sql_schema).replace("\n", "<br/>"), s["code"]))
            story.append(PageBreak())

        # V. Implementation & Setup
        if docs:
            story.extend(_sec("V", "Implementation & Setup", s))
            
            if getattr(docs, "installation_guide", None):
                story.append(_sub("A", "Installation Guide", s))
                story.append(_p(docs.installation_guide, s["body"]))
            
            if getattr(docs, "deployment_notes", None):
                story.append(_sub("B", "Deployment & Production Notes", s))
                story.append(_p(docs.deployment_notes, s["body"]))

            if getattr(docs, "developer_notes", None):
                story.append(_sub("C", "Developer Guidelines", s))
                story.append(_p(docs.developer_notes, s["body"]))
                
            if getattr(docs, "api_documentation", None):
                story.append(_sub("D", "API Endpoints Documentation", s))
                for line in docs.api_documentation.split("\n"):
                    if line.startswith("#"):
                        story.append(_p(line.lstrip("#").strip(), s["body"]))
                    else:
                        story.append(Paragraph(_safe(line), s["code"]))
                        
        # VI. Glossary
        story.extend(_sec("VI", "System Glossary", s))
        terms = [
            ("API", "Application Programming Interface."),
            ("Backend", "Server-side logic and database interactions."),
            ("Frontend", "Client-side user interface."),
            ("JWT", "JSON Web Token for authentication."),
            ("REST", "Representational State Transfer architecture."),
            ("SDLC", "Software Development Life Cycle."),
            ("UAT", "User Acceptance Testing."),
        ]
        gl_rows = [["Term", "Definition"]] + [[t, d] for t, d in terms]
        story.extend(_std_table(gl_rows, [4 * cm, BODY_W - 4 * cm - 1 * cm], s, "TABLE IV. GLOSSARY OF TERMS"))

        doc.build(story)
        return buffer.getvalue()

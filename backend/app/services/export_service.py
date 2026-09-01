"""
export_service.py
─────────────────
Generates a full Blueprint (Requirements + Architecture + Database + Documentation)
as a rich, colored IEEE PDF document.
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
TM = 3.0 * cm
BM = 2.5 * cm
BODY_W = PAGE_W - LM - RM

NAVY = HexColor("#1A2744")
GREEN = HexColor("#155724")
BLUE_L = HexColor("#EAF0FB")
BORDER = HexColor("#CACFD2")
ROW_A = HexColor("#FFFFFF")
ROW_B = HexColor("#F8F9FA")


def _safe(text: str) -> str:
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(_safe(text), style)


def _cover_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, PAGE_H - 3.5 * cm, PAGE_W, 3.5 * cm, fill=1, stroke=0)
    canvas.restoreState()


def _body_page(canvas, doc):
    canvas.saveState()
    proj = getattr(doc, "_project_name", "PROJECT")
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(1.2)
    canvas.line(LM, PAGE_H - TM + 6 * mm, PAGE_W - RM, PAGE_H - TM + 6 * mm)
    canvas.setFont("Times-Bold", 8)
    canvas.setFillColor(NAVY)
    canvas.drawString(LM, PAGE_H - TM + 2 * mm, "BLUEPRINT: COMPREHENSIVE SOFTWARE ARCHITECTURE DOCUMENT")
    canvas.setFont("Times-Roman", 8)
    canvas.setFillColor(colors.HexColor("#444444"))
    canvas.drawRightString(PAGE_W - RM, PAGE_H - TM + 2 * mm, proj.upper())

    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(0.8)
    canvas.line(LM, BM - 5 * mm, PAGE_W - RM, BM - 5 * mm)
    canvas.drawString(LM, BM - 9 * mm, "BluePrint AI — Automated SDLC Planner")
    canvas.drawCentredString(PAGE_W / 2, BM - 9 * mm, str(doc.page))
    canvas.drawRightString(PAGE_W - RM, BM - 9 * mm, datetime.now().strftime("%B %Y"))
    canvas.restoreState()


def _styles() -> dict:
    s = {}
    s["cover_title"] = ParagraphStyle("cover_title", fontName="Times-Bold", fontSize=26, textColor=colors.white, alignment=TA_CENTER, spaceAfter=8, leading=32)
    s["cover_sub"] = ParagraphStyle("cover_sub", fontName="Times-Roman", fontSize=13, textColor=colors.white, alignment=TA_CENTER, spaceAfter=4, leading=18)
    s["sec_head"] = ParagraphStyle("sec_head", fontName="Times-Bold", fontSize=14, textColor=NAVY, alignment=TA_LEFT, spaceBefore=20, spaceAfter=8, leading=18, borderPad=4)
    s["sub_head"] = ParagraphStyle("sub_head", fontName="Times-BoldItalic", fontSize=12, textColor=GREEN, alignment=TA_LEFT, spaceBefore=14, spaceAfter=5, leading=16)
    s["body"] = ParagraphStyle("body", fontName="Times-Roman", fontSize=10, textColor=colors.black, alignment=TA_JUSTIFY, spaceAfter=7, leading=15)
    s["bullet"] = ParagraphStyle("bullet", fontName="Times-Roman", fontSize=10, textColor=colors.black, alignment=TA_JUSTIFY, spaceAfter=4, leading=14, leftIndent=16, firstLineIndent=-10)
    s["caption"] = ParagraphStyle("caption", fontName="Times-Bold", fontSize=9, textColor=HexColor("#333333"), alignment=TA_CENTER, spaceAfter=4, leading=13)
    s["code"] = ParagraphStyle("code", fontName="Courier", fontSize=9, textColor=HexColor("#1A2744"), alignment=TA_LEFT, spaceAfter=2, leading=12, leftIndent=10, backColor=HexColor("#F0F4FF"), borderPad=4)
    return s


def _sec(roman: str, title: str, s: dict) -> List[Flowable]:
    return [
        Spacer(1, 4 * mm),
        _p(f"{roman}.\u2002{title.upper()}", s["sec_head"]),
        HRFlowable(width="100%", thickness=1.5, color=NAVY, spaceAfter=8),
    ]


def _sub(letter: str, title: str, s: dict) -> Flowable:
    return _p(f"{letter}.\u2002{title}", s["sub_head"])


def _callout(text: str) -> Table:
    p = Paragraph(_safe(text), ParagraphStyle("callout", fontName="Times-Italic", fontSize=10, textColor=NAVY, alignment=TA_JUSTIFY, leading=15))
    t = Table([[p]], colWidths=[BODY_W - 1 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLUE_L),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 1, NAVY),
        ("LEFTBORDER", (0, 0), (0, -1), 4, NAVY),
    ]))
    return t


def _std_table(rows, col_widths, s, caption: str = "") -> List[Flowable]:
    out = []
    if caption:
        out.append(_p(caption, s["caption"]))
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]
    for i in range(1, len(rows)):
        style.append(("BACKGROUND", (0, i), (-1, i), ROW_A if i % 2 == 1 else ROW_B))
    t.setStyle(TableStyle(style))
    out.append(t)
    out.append(Spacer(1, 5 * mm))
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
        story.append(Spacer(1, 1 * cm))
        story.append(_p(project_name, s["cover_title"]))
        story.append(Spacer(1, 3 * mm))
        story.append(_p("Comprehensive System Architecture Blueprint", s["cover_sub"]))
        story.append(Spacer(1, 18 * mm))

        meta_rows = [
            ["Document Type", "System Architecture & Design Document"],
            ["Project Name", project_name],
            ["Generated", datetime.now().strftime("%d %B %Y")],
            ["Framework", "BluePrint AI"],
        ]
        mt = Table(meta_rows, colWidths=[4 * cm, BODY_W - 4 * cm - 1 * cm])
        mt.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Times-Bold"),
            ("FONTNAME", (1, 0), (1, -1), "Times-Roman"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
            ("TEXTCOLOR", (1, 0), (1, -1), HexColor("#EEEEEE")),
            ("BACKGROUND", (0, 0), (-1, -1), NAVY),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#3A4D7A")),
            ("PADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(mt)
        story.append(PageBreak())

        # I. Requirements
        if req:
            story.extend(_sec("I", "System Requirements", s))
            story.append(_sub("A", "Project Overview", s))
            story.append(_callout(req.project_overview or "No overview provided."))
            story.append(Spacer(1, 4 * mm))

            story.append(_sub("B", "Functional Requirements", s))
            for item in (req.functional_requirements or []):
                story.append(Paragraph(f"\u2022\u2002{_safe(item)}", s["bullet"]))
            
            story.append(_sub("C", "Technology Stack", s))
            ts = req.recommended_tech_stack
            ts_rows = [
                ["Layer", "Technology"],
                ["Frontend", _safe(ts.frontend if ts else "—")],
                ["Backend", _safe(ts.backend if ts else "—")],
                ["Database", _safe(ts.database if ts else "—")],
                ["AI Framework", _safe(ts.ai_framework if ts else "—")],
            ]
            story.extend(_std_table(ts_rows, [4 * cm, BODY_W - 4 * cm - 1 * cm], s, "TABLE I. TECHNOLOGY STACK"))
            story.append(PageBreak())

        # II. Architecture
        if arch:
            story.extend(_sec("II", "System Architecture", s))
            story.append(_sub("A", "High Level Design", s))
            story.append(_callout(arch.high_level_architecture or "No architecture overview."))
            story.append(Spacer(1, 4 * mm))
            
            story.append(_sub("B", "Component Breakdown", s))
            if arch.component_breakdown:
                c_rows = [["Component", "Type", "Description"]]
                for comp in arch.component_breakdown:
                    c_rows.append([comp.name, comp.type, comp.description])
                story.extend(_std_table(c_rows, [4 * cm, 3 * cm, BODY_W - 7 * cm - 1 * cm], s, "TABLE II. COMPONENT BREAKDOWN"))

            story.append(_sub("C", "Data Flow", s))
            story.append(_p(arch.data_flow or "Data flow not defined.", s["body"]))
            story.append(PageBreak())

        # III. Database
        if db:
            story.extend(_sec("III", "Database Design", s))
            story.append(_sub("A", "Entity Relationship Schema", s))
            if db.entities:
                for idx, ent in enumerate(db.entities, 1):
                    ent_rows = [["Attribute", "Definition"]]
                    for attr in ent.attributes:
                        parts = attr.split(" ", 1)
                        name = parts[0]
                        defn = parts[1] if len(parts) > 1 else "TEXT"
                        ent_rows.append([name, defn])
                    story.extend(_std_table(ent_rows, [4 * cm, BODY_W - 4 * cm - 1 * cm], s, f"TABLE III-{idx}. ENTITY: {ent.name.upper()}"))
            else:
                story.append(_p("No entities defined.", s["body"]))
            story.append(PageBreak())

        # IV. Documentation
        if docs:
            story.extend(_sec("IV", "Documentation", s))
            story.append(_sub("A", "README Content", s))
            lines = (docs.readme_md or "No README generated.").split("\n")
            for line in lines:
                if line.startswith("#"):
                    story.append(_p(line.lstrip("#").strip(), s["body"]))
                else:
                    story.append(Paragraph(_safe(line), s["code"]))
            
            if docs.api_docs_md:
                story.append(Spacer(1, 8 * mm))
                story.append(_sub("B", "API Documentation", s))
                lines = docs.api_docs_md.split("\n")
                for line in lines:
                    if line.startswith("#"):
                        story.append(_p(line.lstrip("#").strip(), s["body"]))
                    else:
                        story.append(Paragraph(_safe(line), s["code"]))

        doc.build(story)
        return buffer.getvalue()

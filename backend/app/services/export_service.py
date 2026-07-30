"""
export_service.py
─────────────────
Compiles the ProjectContext produced by the planning agents into a
professionally-styled PDF document using ReportLab.

Sections generated
──────────────────
  1. Cover page
  2. Software Requirements Specification (SRS)
  3. System Architecture
  4. Database Schema & Normalization
  5. User Documentation
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import List, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)
from reportlab.platypus.flowables import Flowable

from app.models.requirements import ProjectContext

# ─── Colour palette ──────────────────────────────────────────────────────────
PRIMARY   = colors.HexColor("#4F46E5")   # indigo-600
SECONDARY = colors.HexColor("#7C3AED")   # violet-600
ACCENT    = colors.HexColor("#06B6D4")   # cyan-500
DARK      = colors.HexColor("#0F172A")   # slate-900
MUTED     = colors.HexColor("#64748B")   # slate-500
LIGHT_BG  = colors.HexColor("#F1F5F9")   # slate-100
WHITE     = colors.white
BLACK     = colors.black

PAGE_W, PAGE_H = A4
MARGIN = 2 * cm


# ─── Custom Flowables ─────────────────────────────────────────────────────────

class ColoredRect(Flowable):
    """A filled rounded rectangle used as a decorative section header."""

    def __init__(self, width: float, height: float, fill_color, radius: float = 4):
        super().__init__()
        self.width  = width
        self.height = height
        self.fill_color = fill_color
        self.radius = radius

    def draw(self):
        self.canv.setFillColor(self.fill_color)
        self.canv.roundRect(0, 0, self.width, self.height, self.radius, fill=1, stroke=0)


# ─── Style builder ────────────────────────────────────────────────────────────

def _build_styles() -> dict:
    base = getSampleStyleSheet()

    styles: dict = {}

    styles["cover_title"] = ParagraphStyle(
        "cover_title",
        fontName="Helvetica-Bold",
        fontSize=36,
        textColor=WHITE,
        alignment=TA_CENTER,
        spaceAfter=12,
        leading=44,
    )
    styles["cover_subtitle"] = ParagraphStyle(
        "cover_subtitle",
        fontName="Helvetica",
        fontSize=16,
        textColor=colors.HexColor("#CBD5E1"),
        alignment=TA_CENTER,
        spaceAfter=8,
    )
    styles["cover_meta"] = ParagraphStyle(
        "cover_meta",
        fontName="Helvetica-Oblique",
        fontSize=11,
        textColor=colors.HexColor("#94A3B8"),
        alignment=TA_CENTER,
    )
    styles["section_heading"] = ParagraphStyle(
        "section_heading",
        fontName="Helvetica-Bold",
        fontSize=18,
        textColor=PRIMARY,
        spaceBefore=20,
        spaceAfter=8,
        leading=24,
    )
    styles["sub_heading"] = ParagraphStyle(
        "sub_heading",
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=SECONDARY,
        spaceBefore=14,
        spaceAfter=6,
        leading=18,
    )
    styles["body"] = ParagraphStyle(
        "body",
        fontName="Helvetica",
        fontSize=10,
        textColor=DARK,
        spaceAfter=6,
        leading=15,
    )
    styles["body_muted"] = ParagraphStyle(
        "body_muted",
        fontName="Helvetica",
        fontSize=10,
        textColor=MUTED,
        spaceAfter=4,
        leading=14,
    )
    styles["code"] = ParagraphStyle(
        "code",
        fontName="Courier",
        fontSize=8,
        textColor=DARK,
        backColor=LIGHT_BG,
        spaceAfter=4,
        leading=12,
        leftIndent=8,
        rightIndent=8,
        borderPad=4,
    )
    styles["bullet"] = ParagraphStyle(
        "bullet",
        fontName="Helvetica",
        fontSize=10,
        textColor=DARK,
        spaceAfter=4,
        leading=14,
        leftIndent=18,
        bulletIndent=6,
    )
    styles["toc_item"] = ParagraphStyle(
        "toc_item",
        fontName="Helvetica",
        fontSize=11,
        textColor=DARK,
        spaceAfter=6,
        leading=16,
    )
    styles["footer_text"] = ParagraphStyle(
        "footer_text",
        fontName="Helvetica",
        fontSize=8,
        textColor=MUTED,
        alignment=TA_CENTER,
    )

    return styles


# ─── Page templates ───────────────────────────────────────────────────────────

def _on_cover_page(canvas, doc):
    """Draws the full-bleed gradient cover background."""
    canvas.saveState()
    # Deep navy background
    canvas.setFillColor(DARK)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    # Gradient accent band at top
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, PAGE_H - 5 * cm, PAGE_W, 5 * cm, fill=1, stroke=0)
    # Bottom accent strip
    canvas.setFillColor(SECONDARY)
    canvas.rect(0, 0, PAGE_W, 1.2 * cm, fill=1, stroke=0)
    canvas.restoreState()


def _on_body_page(canvas, doc):
    """Draws a subtle header line + page footer on every body page."""
    canvas.saveState()
    # Top rule
    canvas.setStrokeColor(PRIMARY)
    canvas.setLineWidth(2)
    canvas.line(MARGIN, PAGE_H - MARGIN + 4, PAGE_W - MARGIN, PAGE_H - MARGIN + 4)
    # Footer
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    project = getattr(doc, "_project_name", "BluePrint")
    canvas.drawString(MARGIN, 1 * cm, f"{project} — Generated by BluePrint AI")
    canvas.drawRightString(PAGE_W - MARGIN, 1 * cm, f"Page {doc.page}")
    # Footer left rule
    canvas.setStrokeColor(LIGHT_BG)
    canvas.setLineWidth(1)
    canvas.line(MARGIN, 1.4 * cm, PAGE_W - MARGIN, 1.4 * cm)
    canvas.restoreState()


# ─── Content builders ─────────────────────────────────────────────────────────

def _p(text: str, style: dict, key: str = "body") -> Paragraph:
    safe = (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(safe, style[key])


def _bullet_list(items: List[str], styles: dict) -> List[Flowable]:
    out: List[Flowable] = []
    for item in items:
        safe = (item or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        out.append(Paragraph(f"• {safe}", styles["bullet"]))
    return out


def _section_header(title: str, styles: dict) -> List[Flowable]:
    return [
        Spacer(1, 0.3 * cm),
        _p(title, styles, "section_heading"),
        HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10),
    ]


def _sub_header(title: str, styles: dict) -> Flowable:
    return _p(title, styles, "sub_heading")


def _code_block(sql: str, styles: dict) -> List[Flowable]:
    lines = (sql or "").split("\n")
    out = []
    for line in lines:
        safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        out.append(Paragraph(safe or "&nbsp;", styles["code"]))
    return out


def _build_cover(context: ProjectContext, styles: dict) -> List[Flowable]:
    project_name = "Untitled Project"
    overview     = ""
    if context.requirements:
        project_name = context.requirements.project_name or project_name
        overview     = context.requirements.project_overview or ""

    now = datetime.now().strftime("%B %d, %Y — %H:%M")

    flowables: List[Flowable] = [
        Spacer(1, 6 * cm),
        _p("📐", styles["cover_title"]),
        _p("BluePrint AI", styles["cover_subtitle"]),
        Spacer(1, 0.6 * cm),
        _p(project_name, styles["cover_title"]),
        Spacer(1, 0.4 * cm),
        _p("Software Blueprint Report", styles["cover_subtitle"]),
        Spacer(1, 1 * cm),
        _p(overview[:300] + ("…" if len(overview) > 300 else ""), styles["cover_meta"]),
        Spacer(1, 2 * cm),
        _p(f"Generated on {now}", styles["cover_meta"]),
        PageBreak(),
    ]
    return flowables


def _build_toc(context: ProjectContext, styles: dict) -> List[Flowable]:
    sections = []
    if context.requirements:  sections.append("1. Software Requirements Specification")
    if context.architecture:  sections.append("2. System Architecture")
    if context.database:      sections.append("3. Database Schema & Normalization")
    if context.documentation: sections.append("4. User & Developer Documentation")

    out: List[Flowable] = _section_header("Table of Contents", styles)
    for s in sections:
        out.append(_p(s, styles, "toc_item"))
        out.append(Spacer(1, 0.1 * cm))
    out.append(PageBreak())
    return out


def _build_requirements_section(req, styles: dict) -> List[Flowable]:
    out: List[Flowable] = _section_header("1. Software Requirements Specification", styles)

    # Project overview
    out.append(_sub_header("Project Overview", styles))
    out.append(_p(req.project_overview, styles))
    out.append(Spacer(1, 0.4 * cm))

    # Objectives
    if req.objectives:
        out.append(_sub_header("Objectives", styles))
        out.extend(_bullet_list(req.objectives, styles))
        out.append(Spacer(1, 0.3 * cm))

    # Functional Requirements
    if req.functional_requirements:
        out.append(_sub_header("Functional Requirements", styles))
        out.extend(_bullet_list(req.functional_requirements, styles))
        out.append(Spacer(1, 0.3 * cm))

    # Non-Functional Requirements
    if req.non_functional_requirements:
        out.append(_sub_header("Non-Functional Requirements", styles))
        out.extend(_bullet_list(req.non_functional_requirements, styles))
        out.append(Spacer(1, 0.3 * cm))

    # User Roles
    if req.user_roles:
        out.append(_sub_header("User Roles", styles))
        out.extend(_bullet_list(req.user_roles, styles))
        out.append(Spacer(1, 0.3 * cm))

    # User Stories table
    if req.user_stories:
        out.append(_sub_header("User Stories", styles))
        table_data = [["Role", "Desire", "Benefit"]]
        for story in req.user_stories:
            table_data.append([
                Paragraph(story.role or "", styles["body"]),
                Paragraph(story.desire or "", styles["body"]),
                Paragraph(story.benefit or "", styles["body"]),
            ])
        col_widths = [3 * cm, 7.5 * cm, 6 * cm]
        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR",   (0, 0), (-1, 0), WHITE),
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, 0), 10),
            ("ALIGN",       (0, 0), (-1, 0), "CENTER"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
            ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("TOPPADDING",  (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        out.append(t)
        out.append(Spacer(1, 0.4 * cm))

    # Tech Stack
    if req.recommended_tech_stack:
        out.append(_sub_header("Recommended Tech Stack", styles))
        ts = req.recommended_tech_stack
        stack_data = [
            ["Layer", "Technology"],
            ["Frontend",   ts.frontend   or "—"],
            ["Backend",    ts.backend    or "—"],
            ["Database",   ts.database   or "—"],
            ["AI / LLM",   ts.ai_framework or "—"],
        ]
        t2 = Table(stack_data, colWidths=[5 * cm, 11.5 * cm], repeatRows=1)
        t2.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0), SECONDARY),
            ("TEXTCOLOR",   (0, 0), (-1, 0), WHITE),
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
            ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("TOPPADDING",  (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        out.append(t2)
        out.append(Spacer(1, 0.3 * cm))

    # Assumptions & Constraints
    if req.assumptions:
        out.append(_sub_header("Assumptions", styles))
        out.extend(_bullet_list(req.assumptions, styles))

    if req.constraints:
        out.append(_sub_header("Constraints", styles))
        out.extend(_bullet_list(req.constraints, styles))

    if req.future_scope:
        out.append(_sub_header("Future Scope", styles))
        out.extend(_bullet_list(req.future_scope, styles))

    out.append(PageBreak())
    return out


def _build_architecture_section(arch, styles: dict) -> List[Flowable]:
    out: List[Flowable] = _section_header("2. System Architecture", styles)

    out.append(_sub_header("High-Level Architecture", styles))
    out.append(_p(arch.high_level_architecture, styles))
    out.append(Spacer(1, 0.4 * cm))

    if arch.data_flow:
        out.append(_sub_header("Data Flow", styles))
        out.append(_p(arch.data_flow, styles))
        out.append(Spacer(1, 0.4 * cm))

    if arch.folder_structure:
        out.append(_sub_header("Recommended Folder Structure", styles))
        out.extend(_code_block("\n".join(arch.folder_structure), styles))
        out.append(Spacer(1, 0.4 * cm))

    if arch.component_breakdown:
        out.append(_sub_header("Component Breakdown", styles))
        for comp in arch.component_breakdown:
            block: List[Flowable] = [
                _p(f"<b>{comp.name}</b>", styles),
                _p(comp.description or "", styles, "body_muted"),
            ]
            if comp.dependencies:
                block.append(_p("Dependencies: " + ", ".join(comp.dependencies), styles, "body_muted"))
            block.append(Spacer(1, 0.2 * cm))
            out.extend(block)

    out.append(PageBreak())
    return out


def _build_database_section(db, styles: dict) -> List[Flowable]:
    out: List[Flowable] = _section_header("3. Database Schema & Normalization", styles)

    if db.database_overview:
        out.append(_sub_header("Overview", styles))
        out.append(_p(db.database_overview, styles))
        out.append(Spacer(1, 0.3 * cm))

    if db.normalization_notes:
        out.append(_sub_header("Normalization Notes", styles))
        out.append(_p(db.normalization_notes, styles))
        out.append(Spacer(1, 0.3 * cm))

    if db.relationships:
        out.append(_sub_header("Entity Relationships", styles))
        out.extend(_bullet_list(db.relationships, styles))
        out.append(Spacer(1, 0.3 * cm))

    if db.entities:
        out.append(_sub_header("Entities / Tables", styles))
        for entity in db.entities:
            entity_block: List[Flowable] = [
                _p(f"<b>{entity.name}</b>", styles),
                _p(entity.description or "", styles, "body_muted"),
            ]
            # Attributes table
            if entity.attributes:
                attr_data = [["Column / Attribute"]]
                for attr in entity.attributes:
                    attr_data.append([Paragraph(attr or "", styles["body"])])
                t = Table(attr_data, colWidths=[PAGE_W - 2 * MARGIN - 1 * cm], repeatRows=1)
                t.setStyle(TableStyle([
                    ("BACKGROUND",  (0, 0), (-1, 0), ACCENT),
                    ("TEXTCOLOR",   (0, 0), (-1, 0), WHITE),
                    ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
                    ("GRID",        (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                    ("TOPPADDING",  (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ]))
                entity_block.append(t)
            if entity.primary_key:
                entity_block.append(_p(f"PK: {entity.primary_key}", styles, "body_muted"))
            if entity.foreign_keys:
                entity_block.append(_p("FK: " + ", ".join(entity.foreign_keys), styles, "body_muted"))
            entity_block.append(Spacer(1, 0.4 * cm))
            out.extend(entity_block)

    if db.sql_schema:
        out.append(_sub_header("SQL DDL Schema", styles))
        out.extend(_code_block(db.sql_schema, styles))

    out.append(PageBreak())
    return out


def _build_documentation_section(doc, styles: dict) -> List[Flowable]:
    out: List[Flowable] = _section_header("4. User & Developer Documentation", styles)

    if doc.project_overview:
        out.append(_sub_header("Project Overview", styles))
        out.append(_p(doc.project_overview, styles))
        out.append(Spacer(1, 0.3 * cm))

    if doc.installation_guide:
        out.append(_sub_header("Installation Guide", styles))
        out.extend(_code_block(doc.installation_guide, styles))
        out.append(Spacer(1, 0.3 * cm))

    if doc.api_documentation:
        out.append(_sub_header("API Documentation", styles))
        out.append(_p(doc.api_documentation, styles))
        out.append(Spacer(1, 0.3 * cm))

    if doc.folder_structure_description:
        out.append(_sub_header("Folder Structure", styles))
        out.append(_p(doc.folder_structure_description, styles))
        out.append(Spacer(1, 0.3 * cm))

    if doc.deployment_notes:
        out.append(_sub_header("Deployment Notes", styles))
        out.append(_p(doc.deployment_notes, styles))
        out.append(Spacer(1, 0.3 * cm))

    if doc.developer_notes:
        out.append(_sub_header("Developer Notes", styles))
        out.append(_p(doc.developer_notes, styles))

    if doc.readme_md:
        out.append(PageBreak())
        out.append(_sub_header("README.md", styles))
        out.extend(_code_block(doc.readme_md, styles))

    return out


# ─── Public API ───────────────────────────────────────────────────────────────

class ExportService:
    """Converts a :class:`ProjectContext` into a PDF byte stream."""

    def generate_pdf(self, context: ProjectContext) -> bytes:
        buffer = io.BytesIO()
        styles = _build_styles()

        project_name = "BluePrint Project"
        if context.requirements and context.requirements.project_name:
            project_name = context.requirements.project_name

        # ── Document setup ──────────────────────────────────────────────────
        doc = BaseDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=MARGIN + 0.5 * cm,
            title=f"{project_name} — BluePrint Report",
            author="BluePrint AI",
        )
        doc._project_name = project_name  # passed to page callback

        # Cover page frame (full-bleed — no margins for background drawing)
        cover_frame = Frame(0, 0, PAGE_W, PAGE_H, leftPadding=MARGIN,
                            rightPadding=MARGIN, topPadding=0, bottomPadding=0)
        body_frame  = Frame(MARGIN, MARGIN + 0.8 * cm, PAGE_W - 2 * MARGIN,
                            PAGE_H - 2 * MARGIN - 0.4 * cm)

        cover_tpl = PageTemplate(id="Cover", frames=[cover_frame], onPage=_on_cover_page)
        body_tpl  = PageTemplate(id="Body",  frames=[body_frame],  onPage=_on_body_page)
        doc.addPageTemplates([cover_tpl, body_tpl])

        # ── Collect all flowables ────────────────────────────────────────────
        story: List[Flowable] = []

        # Switch to cover page template for first page
        story.append(NextPageTemplate("Cover"))
        story.extend(_build_cover(context, styles))

        # Switch to body template for remaining pages
        story.append(NextPageTemplate("Body"))
        story.extend(_build_toc(context, styles))

        if context.requirements:
            story.extend(_build_requirements_section(context.requirements, styles))

        if context.architecture:
            story.extend(_build_architecture_section(context.architecture, styles))

        if context.database:
            story.extend(_build_database_section(context.database, styles))

        if context.documentation:
            story.extend(_build_documentation_section(context.documentation, styles))

        doc.build(story)
        return buffer.getvalue()

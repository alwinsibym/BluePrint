"""
srs_service.py
──────────────
Generates a full IEEE Std 830-1998 Software Requirements Specification (SRS)
PDF document. Single-column A4 layout, professional styling, complete content.
"""
from __future__ import annotations
import io
from datetime import datetime
from typing import List, Optional
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, HRFlowable, NextPageTemplate,
    PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether,
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib.colors import HexColor
from app.models.requirements import RequirementsResponse

# ── Page geometry ──────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A4
LM = 2.5 * cm   # left margin
RM = 2.5 * cm   # right margin
TM = 3.5 * cm   # top margin (space for header)
BM = 3.0 * cm   # bottom margin (space for footer)
BODY_W = PAGE_W - LM - RM

# ── Brand colours ──────────────────────────────────────────────────────────
PRIMARY = HexColor("#003366")  # Professional Dark Blue for all headings
SECONDARY = HexColor("#004080")
GREY   = HexColor("#F2F4F6")   
BLUE_L = HexColor("#F0F4F8")   
BORDER = HexColor("#BDC3C7")   
ROW_A  = HexColor("#FFFFFF")
ROW_B  = HexColor("#F8F9FA")


# ── Canvas callbacks ───────────────────────────────────────────────────────
def _cover_canvas(canvas, doc):
    canvas.saveState()
    # Dark Blue top banner
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, PAGE_H - 8.0 * cm, PAGE_W, 8.0 * cm, fill=1, stroke=0)
    canvas.restoreState()


def _body_canvas(canvas, doc):
    canvas.saveState()
    proj = getattr(doc, "_project_name", "PROJECT")
    # Header line
    canvas.setStrokeColor(PRIMARY)
    canvas.setLineWidth(1.5)
    canvas.line(LM, PAGE_H - 2.0 * cm, PAGE_W - RM, PAGE_H - 2.0 * cm)
    canvas.setFont("Times-Bold", 8)
    canvas.setFillColor(PRIMARY)
    canvas.drawString(LM, PAGE_H - 1.8 * cm, "IEEE Std 830-1998 — SOFTWARE REQUIREMENTS SPECIFICATION")
    canvas.setFont("Times-Roman", 8)
    canvas.setFillColor(colors.HexColor("#444444"))
    canvas.drawRightString(PAGE_W - RM, PAGE_H - 1.8 * cm, proj.upper())
    
    # Footer
    canvas.setStrokeColor(PRIMARY)
    canvas.setLineWidth(1.0)
    canvas.line(LM, 1.5 * cm, PAGE_W - RM, 1.5 * cm)
    canvas.setFont("Times-Roman", 8)
    canvas.setFillColor(colors.HexColor("#444444"))
    canvas.drawString(LM, 1.1 * cm, "BluePrint AI — Automated SDLC Planner")
    canvas.drawCentredString(PAGE_W / 2, 1.1 * cm, f"Page {doc.page}")
    canvas.drawRightString(PAGE_W - RM, 1.1 * cm, datetime.now().strftime("%B %Y"))
    canvas.restoreState()


# ── Styles ─────────────────────────────────────────────────────────────────
def _styles() -> dict:
    s = {}
    s["cover_title"] = ParagraphStyle("cover_title", fontName="Times-Bold", fontSize=28,
        textColor=colors.white, alignment=TA_CENTER, spaceAfter=12, leading=34)
    s["cover_sub"] = ParagraphStyle("cover_sub", fontName="Times-Roman", fontSize=14,
        textColor=colors.white, alignment=TA_CENTER, spaceAfter=6, leading=20)
    
    # Headings with keepWithNext to prevent orphaned headings
    s["sec_head"] = ParagraphStyle("sec_head", fontName="Times-Bold", fontSize=16,
        textColor=PRIMARY, alignment=TA_LEFT, spaceBefore=24, spaceAfter=8, leading=20,
        keepWithNext=True)
    s["sub_head"] = ParagraphStyle("sub_head", fontName="Times-BoldItalic", fontSize=13,
        textColor=SECONDARY, alignment=TA_LEFT, spaceBefore=16, spaceAfter=6, leading=16,
        keepWithNext=True)
    s["sub_sub_head"] = ParagraphStyle("sub_sub_head", fontName="Times-Bold", fontSize=11,
        textColor=colors.black, alignment=TA_LEFT, spaceBefore=10, spaceAfter=4, leading=14,
        keepWithNext=True)
        
    s["body"] = ParagraphStyle("body", fontName="Times-Roman", fontSize=11,
        textColor=colors.black, alignment=TA_JUSTIFY, spaceAfter=8, leading=16)
    s["body_bold"] = ParagraphStyle("body_bold", fontName="Times-Bold", fontSize=11,
        textColor=colors.black, alignment=TA_LEFT, spaceAfter=6, leading=16)
    s["bullet"] = ParagraphStyle("bullet", fontName="Times-Roman", fontSize=11,
        textColor=colors.black, alignment=TA_JUSTIFY, spaceAfter=6, leading=16,
        leftIndent=20, firstLineIndent=-12)
    s["req_id"] = ParagraphStyle("req_id", fontName="Courier-Bold", fontSize=10,
        textColor=PRIMARY, alignment=TA_LEFT, spaceAfter=2, leading=14,
        leftIndent=4, keepWithNext=True)
    s["req_body"] = ParagraphStyle("req_body", fontName="Times-Roman", fontSize=11,
        textColor=colors.black, alignment=TA_JUSTIFY, spaceAfter=8, leading=16,
        leftIndent=20, firstLineIndent=-10)
    s["caption"] = ParagraphStyle("caption", fontName="Times-Bold", fontSize=10,
        textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=6, leading=14, keepWithNext=True)
    s["toc"] = ParagraphStyle("toc", fontName="Times-Roman", fontSize=11,
        textColor=colors.black, alignment=TA_LEFT, spaceAfter=6, leading=16)
    s["toc_bold"] = ParagraphStyle("toc_bold", fontName="Times-Bold", fontSize=11,
        textColor=PRIMARY, alignment=TA_LEFT, spaceAfter=6, leading=16)
    return s


# ── Helpers ────────────────────────────────────────────────────────────────
def _safe(text: str) -> str:
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(_safe(text), style)

def _sec(roman: str, title: str, s: dict) -> List[Flowable]:
    return [
        Spacer(1, 6 * mm),
        _p(f"{roman}.\u2002{title.upper()}", s["sec_head"]),
        HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10),
    ]

def _sub(letter: str, title: str, s: dict) -> Flowable:
    return _p(f"{letter}.\u2002{title}", s["sub_head"])

def _bullets(items: List[str], s: dict) -> List[Flowable]:
    return [Paragraph(f"\u2022\u2002{_safe(item)}", s["bullet"]) for item in items if item]

def _numbered_req(items: List[str], prefix: str, s: dict) -> List[Flowable]:
    out = []
    for i, item in enumerate(items, 1):
        out.append(KeepTogether([
            _p(f"{prefix}-{i:03d}", s["req_id"]),
            Paragraph(f"\u2022\u2002{_safe(item)}", s["req_body"]),
        ]))
    return out

def _callout(text: str, s: dict) -> Table:
    p = Paragraph(_safe(text), ParagraphStyle("callout", fontName="Times-Italic", fontSize=11,
        textColor=PRIMARY, alignment=TA_JUSTIFY, leading=16))
    t = Table([[p]], colWidths=[BODY_W - 1 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BLUE_L),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("BOX", (0,0), (-1,-1), 1, PRIMARY),
        ("LEFTBORDER", (0,0), (0,-1), 4, PRIMARY),
    ]))
    return t

def _std_table(rows, col_widths, s, caption: str = "") -> List[Flowable]:
    out = []
    if caption:
        out.append(_p(caption, s["caption"]))
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0,0), (-1,0), PRIMARY),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Times-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 10),
        ("FONTNAME", (0,1), (-1,-1), "Times-Roman"),
        ("FONTSIZE", (0,1), (-1,-1), 10),
        ("GRID", (0,0), (-1,-1), 0.5, BORDER),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]
    for i in range(1, len(rows)):
        style.append(("BACKGROUND", (0,i), (-1,i), ROW_A if i % 2 == 1 else ROW_B))
    t.setStyle(TableStyle(style))
    out.append(t)
    out.append(Spacer(1, 6 * mm))
    return out


# ── Section builders ───────────────────────────────────────────────────────
def _build_cover(req: RequirementsResponse, s: dict) -> List[Flowable]:
    now = datetime.now()
    project_name = (req.project_name or "UNTITLED SYSTEM").upper()
    out: List[Flowable] = [
        Spacer(1, 2 * cm),
        _p(project_name, s["cover_title"]),
        Spacer(1, 5 * mm),
        _p("Software Requirements Specification", s["cover_sub"]),
        _p("IEEE Std 830-1998 Conforming Document", s["cover_sub"]),
        Spacer(1, 25 * mm),
    ]
    
    meta_rows = [
        ["Document Type",    "Software Requirements Specification (SRS)"],
        ["Project Name",     req.project_name or "—"],
        ["Version",          "1.0 (Release)"],
        ["Status",           "Approved"],
        ["Prepared By",      "BluePrint AI — SDLC Agent"],
        ["Standard",         "IEEE Std 830-1998 / ISO/IEC 12207:2008"],
        ["Date",             now.strftime("%d %B %Y")],
    ]
    mt = Table(meta_rows, colWidths=[5 * cm, BODY_W - 5 * cm - 1 * cm])
    mt.setStyle(TableStyle([
        ("FONTNAME",      (0,0), (0,-1), "Times-Bold"),
        ("FONTNAME",      (1,0), (1,-1), "Times-Roman"),
        ("FONTSIZE",      (0,0), (-1,-1), 10),
        ("TEXTCOLOR",     (0,0), (0,-1), colors.white),
        ("TEXTCOLOR",     (1,0), (1,-1), HexColor("#EEEEEE")),
        ("BACKGROUND",    (0,0), (-1,-1), PRIMARY),
        ("GRID",          (0,0), (-1,-1), 0.5, HexColor("#1A4066")),
        ("PADDING",       (0,0), (-1,-1), 8),
    ]))
    out.append(mt)
    out.append(Spacer(1, 15 * mm))

    rev_rows = [
        ["Version", "Date", "Author", "Description"],
        ["1.0", now.strftime("%d %b %Y"), "BluePrint AI", "Initial approved requirements baseline"],
    ]
    out.extend(_std_table(rev_rows, [2*cm, 3.5*cm, 4*cm, BODY_W - 9.5*cm - 1*cm], s, "TABLE I. REVISION HISTORY"))
    return out


def _build_toc(req: RequirementsResponse, s: dict) -> List[Flowable]:
    out = _sec("—", "Table of Contents", s)
    sections = [
        ("I",   "Introduction"),
        ("II",  "Overall Description"),
        ("III", "Specific Requirements"),
        ("IV",  "External Interface Requirements"),
        ("V",   "System Features and Functional Requirements"),
        ("VI",  "Non-Functional Requirements (Quality Attributes)"),
        ("VII", "Use Case Specification"),
        ("VIII","Technology Stack Specification"),
        ("IX",  "Verification and Validation"),
        ("X",   "Appendix A — Requirements Traceability Matrix"),
        ("XI",  "Appendix B — Glossary"),
    ]
    for roman, title in sections:
        out.append(_p(f"{roman}.\u2002{title}", s["toc_bold"] if roman in ("I", "II", "III") else s["toc"]))
    out.append(PageBreak())
    return out


def _build_sec1(req: RequirementsResponse, s: dict) -> List[Flowable]:
    out = _sec("I", "Introduction", s)

    out.append(_sub("A", "Purpose of this Document", s))
    out.append(_p(
        f"This Software Requirements Specification (SRS) document defines the complete set "
        f"of functional requirements, non-functional quality attributes, external interface "
        f"requirements, and constraints for the <b>{_safe(req.project_name or 'proposed system')}</b>. "
        f"It is prepared in conformance with IEEE Std 830-1998 (IEEE Recommended Practice for "
        f"Software Requirements Specifications). "
        f"This document serves as the primary contractual reference between stakeholders, developers, "
        f"and quality assurance teams.", s["body"]
    ))

    out.append(_sub("B", "Scope of the Product", s))
    out.append(_p(f"The <b>{_safe(req.project_name or 'system')}</b> is designed to provide:", s["body"]))
    out.append(_callout(req.project_overview or "System scope not yet defined.", s))
    if req.objectives:
        out.append(Spacer(1, 4*mm))
        out.append(_p("The primary objectives include:", s["body"]))
        out.extend(_bullets(req.objectives, s))

    out.append(_sub("C", "Definitions, Acronyms, and Abbreviations", s))
    out.append(_p("See Appendix B for a complete glossary of terms used in this document.", s["body"]))

    out.append(_sub("D", "References", s))
    refs = [
        "[1] IEEE Std 830-1998, IEEE Recommended Practice for Software Requirements Specifications.",
        "[2] ISO/IEC 12207:2008, Systems and Software Engineering — Software Life Cycle Processes.",
        "[3] Project Charter and Initial Stakeholder Interviews.",
    ]
    out.extend(_bullets(refs, s))
    return out


def _build_sec2(req: RequirementsResponse, s: dict) -> List[Flowable]:
    out = _sec("II", "Overall Description", s)

    out.append(_sub("A", "Product Perspective", s))
    out.append(_p(
        "The system operates as an independent, standalone software product deployed in a modern "
        "client-server architecture. It provides a robust API layer for communication between "
        "the frontend presentation tier and backend application logic.", s["body"]
    ))

    out.append(_sub("B", "User Classes and Characteristics", s))
    if req.user_roles:
        role_rows = [["User Class", "Description", "Access Level"]]
        for role in req.user_roles:
            role_rows.append([role, f"Interacts with {_safe(req.project_name or 'system')} modules", "Role-based"])
        out.extend(_std_table(role_rows, [4*cm, BODY_W - 7*cm - 1*cm, 3*cm], s, "TABLE II. USER CLASSES"))
    else:
        out.append(_p("User classes will be defined during detailed design.", s["body"]))

    out.append(_sub("C", "Operating Environment", s))
    ts = req.recommended_tech_stack
    env_rows = [
        ["Layer", "Technology", "Environment"],
        ["Presentation", ts.frontend if ts else "TBD", "Web Browser / Mobile"],
        ["Application", ts.backend if ts else "TBD", "Cloud / Server"],
        ["Persistence", ts.database if ts else "TBD", "Database Server"],
        ["Intelligence", ts.ai_framework if ts else "None", "Inference Service"],
    ]
    out.extend(_std_table(env_rows, [4*cm, 5*cm, BODY_W - 9*cm - 1*cm], s, "TABLE III. OPERATING ENVIRONMENT"))
    return out


def _build_sec3(req: RequirementsResponse, s: dict) -> List[Flowable]:
    out = _sec("III", "Specific Requirements", s)
    out.append(_p(
        "Sections IV through VI constitute the complete specification of requirements. "
        "Requirements marked [M] are Mandatory; [O] are Optional.", s["body"]
    ))
    return out


def _build_sec4(req: RequirementsResponse, s: dict) -> List[Flowable]:
    out = _sec("IV", "External Interface Requirements", s)

    out.append(_sub("A", "User Interfaces", s))
    out.append(_p(
        "The system shall provide a responsive user interface conforming to WCAG 2.1 Level AA. "
        "It shall adapt to desktop, tablet, and mobile viewports.", s["body"]
    ))

    out.append(_sub("B", "Software Interfaces", s))
    ts = req.recommended_tech_stack
    si_rows = [
        ["Interface", "Protocol", "Data Format", "Purpose"],
        ["Client ↔ Server", "HTTPS", "JSON", "API Communication"],
        ["Server ↔ Database", "TCP/SQL", "Binary", "Data persistence"],
    ]
    out.extend(_std_table(si_rows, [4*cm, 2.5*cm, 2.5*cm, BODY_W - 9*cm - 1*cm], s, "TABLE IV. SOFTWARE INTERFACES"))
    return out


def _build_sec5(req: RequirementsResponse, s: dict) -> List[Flowable]:
    out = _sec("V", "System Features and Functional Requirements", s)
    if not req.functional_requirements:
        out.append(_p("Functional requirements to be defined.", s["body"]))
        return out
    out.extend(_numbered_req(req.functional_requirements, "FR", s))
    return out


def _build_sec6(req: RequirementsResponse, s: dict) -> List[Flowable]:
    out = _sec("VI", "Non-Functional Requirements (Quality Attributes)", s)
    if req.non_functional_requirements:
        out.extend(_numbered_req(req.non_functional_requirements, "NFR", s))
    else:
        out.append(_p("Non-functional requirements to be defined.", s["body"]))
    return out


def _build_sec7(req: RequirementsResponse, s: dict) -> List[Flowable]:
    out = _sec("VII", "Use Case Specification", s)
    if not req.user_stories:
        out.append(_p("No use cases specified.", s["body"]))
        return out

    for i, story in enumerate(req.user_stories, 1):
        uc_rows = [
            ["Field",             "Description"],
            ["Use Case ID",       f"UC-{i:03d}"],
            ["Name",              f"{_safe(story.role or 'User')} — {_safe((story.desire or '')[:50])}"],
            ["Actor",             _safe(story.role or "User")],
            ["Goal",              _safe(story.desire or "—")],
            ["Post-conditions",   _safe(story.benefit or "—")],
        ]
        uc_tbl = Table(uc_rows, colWidths=[4*cm, BODY_W - 4*cm - 1*cm])
        uc_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), PRIMARY),
            ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
            ("FONTNAME",      (0,0), (-1,0), "Times-Bold"),
            ("FONTNAME",      (0,1), (0,-1), "Times-Bold"),
            ("FONTNAME",      (1,1), (1,-1), "Times-Roman"),
            ("FONTSIZE",      (0,0), (-1,-1), 10),
            ("BACKGROUND",    (0,1), (0,-1), GREY),
            ("GRID",          (0,0), (-1,-1), 0.5, BORDER),
            ("PADDING",       (0,0), (-1,-1), 6),
        ]))
        out.append(KeepTogether([
            _p(f"TABLE V-{i}. USE CASE UC-{i:03d}", s["caption"]),
            uc_tbl,
            Spacer(1, 5 * mm),
        ]))
    return out


def _build_sec8(req: RequirementsResponse, s: dict) -> List[Flowable]:
    out = _sec("VIII", "Technology Stack Specification", s)
    ts = req.recommended_tech_stack
    stack_rows = [
        ["Layer", "Technology", "Category", "Justification"],
        ["Frontend",  _safe(ts.frontend if ts else "TBD"), "UI", "Component-based"],
        ["Backend",   _safe(ts.backend if ts else "TBD"), "API", "High performance"],
        ["Database",  _safe(ts.database if ts else "TBD"), "DB", "ACID compliant"],
    ]
    out.extend(_std_table(stack_rows, [2.5*cm, 4*cm, 2.5*cm, BODY_W - 9*cm - 1*cm], s, "TABLE VI. TECHNOLOGY STACK"))
    return out


def _build_sec9(req: RequirementsResponse, s: dict) -> List[Flowable]:
    out = _sec("IX", "Verification and Validation", s)
    out.append(_p("Requirements shall be verified via Inspection, Unit Testing, and UAT.", s["body"]))
    return out


def _build_traceability(req: RequirementsResponse, s: dict) -> List[Flowable]:
    out = _sec("X", "Appendix A — Requirements Traceability", s)
    out.append(_p("The system links Functional Requirements directly to User Stories.", s["body"]))
    return out


def _build_glossary(req: RequirementsResponse, s: dict) -> List[Flowable]:
    out = _sec("XI", "Appendix B — Glossary", s)
    terms = [
        ("API", "Application Programming Interface."),
        ("CRUD", "Create, Read, Update, Delete."),
        ("FR", "Functional Requirement."),
        ("NFR", "Non-Functional Requirement."),
        ("SRS", "Software Requirements Specification."),
        ("UC", "Use Case."),
    ]
    gl_rows = [["Term", "Definition"]] + [[t, d] for t, d in terms]
    out.extend(_std_table(gl_rows, [4*cm, BODY_W - 4*cm - 1*cm], s, "TABLE VII. GLOSSARY"))
    return out


class SrsService:
    def generate_srs_pdf(self, req: RequirementsResponse) -> bytes:
        buffer = io.BytesIO()
        s = _styles()
        project_name = req.project_name or "UNTITLED"

        doc = BaseDocTemplate(
            buffer, pagesize=A4,
            leftMargin=LM, rightMargin=RM,
            topMargin=TM, bottomMargin=BM,
            title=f"SRS: {project_name}",
            author="BluePrint AI",
        )
        doc._project_name = project_name

        body_frame = Frame(LM, BM, BODY_W, PAGE_H - TM - BM, id="body")
        cover_tpl = PageTemplate(id="Cover", frames=[body_frame], onPage=_cover_canvas)
        body_tpl  = PageTemplate(id="Body",  frames=[body_frame], onPage=_body_canvas)
        doc.addPageTemplates([cover_tpl, body_tpl])

        story: List[Flowable] = []
        story.extend(_build_cover(req, s))
        story.append(NextPageTemplate("Body"))
        story.extend(_build_toc(req, s))
        story.extend(_build_sec1(req, s))
        story.extend(_build_sec2(req, s))
        story.extend(_build_sec3(req, s))
        story.extend(_build_sec4(req, s))
        story.extend(_build_sec5(req, s))
        story.extend(_build_sec6(req, s))
        story.extend(_build_sec7(req, s))
        story.extend(_build_sec8(req, s))
        story.extend(_build_sec9(req, s))
        story.append(PageBreak())
        story.extend(_build_traceability(req, s))
        story.extend(_build_glossary(req, s))

        doc.build(story)
        return buffer.getvalue()

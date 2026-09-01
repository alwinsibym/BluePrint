"""
srs_service.py
──────────────
Generates a full IEEE Std 830-1998 Software Requirements Specification (SRS)
PDF document. Single-column A4 layout, color-coded headings, complete content.
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
TM = 3.0 * cm   # top margin (space for header)
BM = 2.5 * cm   # bottom margin (space for footer)
BODY_W = PAGE_W - LM - RM

# ── Brand colours ──────────────────────────────────────────────────────────
NAVY   = HexColor("#1A2744")   # section headings
GREEN  = HexColor("#155724")   # sub-headings
GREY   = HexColor("#F2F4F6")   # table header bg
BLUE_L = HexColor("#EAF0FB")   # callout bg
BORDER = HexColor("#CACFD2")   # table/rule border
ROW_A  = HexColor("#FFFFFF")
ROW_B  = HexColor("#F8F9FA")


# ── Canvas callbacks ───────────────────────────────────────────────────────
def _cover_canvas(canvas, doc):
    canvas.saveState()
    # Navy top banner
    canvas.setFillColor(NAVY)
    canvas.rect(0, PAGE_H - 3.5 * cm, PAGE_W, 3.5 * cm, fill=1, stroke=0)
    canvas.restoreState()


def _body_canvas(canvas, doc):
    canvas.saveState()
    proj = getattr(doc, "_project_name", "PROJECT")
    # Header line
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(1.2)
    canvas.line(LM, PAGE_H - TM + 6 * mm, PAGE_W - RM, PAGE_H - TM + 6 * mm)
    canvas.setFont("Times-Bold", 7.5)
    canvas.setFillColor(NAVY)
    canvas.drawString(LM, PAGE_H - TM + 2.5 * mm, "IEEE Std 830-1998 — SOFTWARE REQUIREMENTS SPECIFICATION")
    canvas.setFont("Times-Roman", 7.5)
    canvas.setFillColor(colors.HexColor("#444444"))
    canvas.drawRightString(PAGE_W - RM, PAGE_H - TM + 2.5 * mm, proj.upper())
    # Footer
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(0.8)
    canvas.line(LM, BM - 5 * mm, PAGE_W - RM, BM - 5 * mm)
    canvas.setFont("Times-Roman", 7.5)
    canvas.setFillColor(colors.HexColor("#444444"))
    canvas.drawString(LM, BM - 8 * mm, "BluePrint AI — Automated SDLC Planner")
    canvas.drawCentredString(PAGE_W / 2, BM - 8 * mm, f"Page {doc.page}")
    canvas.drawRightString(PAGE_W - RM, BM - 8 * mm, datetime.now().strftime("%B %Y"))
    canvas.restoreState()


# ── Styles ─────────────────────────────────────────────────────────────────
def _styles() -> dict:
    s = {}
    s["cover_title"] = ParagraphStyle("cover_title", fontName="Times-Bold", fontSize=26,
        textColor=colors.white, alignment=TA_CENTER, spaceAfter=8, leading=32)
    s["cover_sub"] = ParagraphStyle("cover_sub", fontName="Times-Roman", fontSize=13,
        textColor=colors.white, alignment=TA_CENTER, spaceAfter=4, leading=18)
    s["cover_meta"] = ParagraphStyle("cover_meta", fontName="Times-Roman", fontSize=10,
        textColor=HexColor("#CCCCCC"), alignment=TA_CENTER, spaceAfter=3, leading=14)
    s["abstract_hd"] = ParagraphStyle("abstract_hd", fontName="Times-BoldItalic", fontSize=10,
        textColor=NAVY, spaceAfter=3, leading=14)
    s["abstract_body"] = ParagraphStyle("abstract_body", fontName="Times-Italic", fontSize=10,
        textColor=colors.black, alignment=TA_JUSTIFY, spaceAfter=10, leading=15)
    s["index_terms"] = ParagraphStyle("index_terms", fontName="Times-Roman", fontSize=9,
        textColor=HexColor("#333333"), alignment=TA_JUSTIFY, spaceAfter=6, leading=13)
    # Section heading — navy banner feel via large bold centred text
    s["sec_head"] = ParagraphStyle("sec_head", fontName="Times-Bold", fontSize=13,
        textColor=NAVY, alignment=TA_LEFT, spaceBefore=20, spaceAfter=6, leading=18,
        borderPad=4)
    s["sub_head"] = ParagraphStyle("sub_head", fontName="Times-BoldItalic", fontSize=11,
        textColor=GREEN, alignment=TA_LEFT, spaceBefore=14, spaceAfter=5, leading=15)
    s["sub_sub_head"] = ParagraphStyle("sub_sub_head", fontName="Times-Bold", fontSize=10,
        textColor=HexColor("#333333"), alignment=TA_LEFT, spaceBefore=8, spaceAfter=3, leading=14)
    s["body"] = ParagraphStyle("body", fontName="Times-Roman", fontSize=10,
        textColor=colors.black, alignment=TA_JUSTIFY, spaceAfter=7, leading=15)
    s["body_bold"] = ParagraphStyle("body_bold", fontName="Times-Bold", fontSize=10,
        textColor=colors.black, alignment=TA_LEFT, spaceAfter=5, leading=14)
    s["bullet"] = ParagraphStyle("bullet", fontName="Times-Roman", fontSize=10,
        textColor=colors.black, alignment=TA_JUSTIFY, spaceAfter=4, leading=14,
        leftIndent=16, firstLineIndent=-10)
    s["req_id"] = ParagraphStyle("req_id", fontName="Courier-Bold", fontSize=9,
        textColor=NAVY, alignment=TA_LEFT, spaceAfter=1, leading=12,
        leftIndent=4)
    s["req_body"] = ParagraphStyle("req_body", fontName="Times-Roman", fontSize=10,
        textColor=colors.black, alignment=TA_JUSTIFY, spaceAfter=6, leading=14,
        leftIndent=20, firstLineIndent=-10)
    s["caption"] = ParagraphStyle("caption", fontName="Times-Bold", fontSize=9,
        textColor=HexColor("#333333"), alignment=TA_CENTER, spaceAfter=4, leading=13)
    s["code"] = ParagraphStyle("code", fontName="Courier", fontSize=8.5,
        textColor=HexColor("#1A2744"), alignment=TA_LEFT, spaceAfter=2, leading=12,
        leftIndent=10, backColor=HexColor("#F0F4FF"), borderPad=4)
    s["toc"] = ParagraphStyle("toc", fontName="Times-Roman", fontSize=10,
        textColor=colors.black, alignment=TA_LEFT, spaceAfter=5, leading=14)
    s["toc_bold"] = ParagraphStyle("toc_bold", fontName="Times-Bold", fontSize=10,
        textColor=NAVY, alignment=TA_LEFT, spaceAfter=3, leading=14)
    return s


# ── Helpers ────────────────────────────────────────────────────────────────
def _safe(text: str) -> str:
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(_safe(text), style)

def _sec(roman: str, title: str, s: dict) -> List[Flowable]:
    """Navy-coloured section heading with rule underneath."""
    return [
        Spacer(1, 4 * mm),
        _p(f"{roman}.\u2002{title.upper()}", s["sec_head"]),
        HRFlowable(width="100%", thickness=1.5, color=NAVY, spaceAfter=6),
    ]

def _sub(letter: str, title: str, s: dict) -> Flowable:
    return _p(f"{letter}.\u2002{title}", s["sub_head"])

def _subsub(number: str, title: str, s: dict) -> Flowable:
    return _p(f"{number}\u2002{title}", s["sub_sub_head"])

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
    """Blue-tinted callout box for overview text."""
    p = Paragraph(_safe(text), ParagraphStyle("callout", fontName="Times-Italic", fontSize=10,
        textColor=NAVY, alignment=TA_JUSTIFY, leading=15))
    t = Table([[p]], colWidths=[BODY_W - 1 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BLUE_L),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("BOX", (0,0), (-1,-1), 1, NAVY),
        ("LEFTBORDER", (0,0), (0,-1), 4, NAVY),
    ]))
    return t

def _std_table(rows, col_widths, s, caption: str = "") -> List[Flowable]:
    """Standard IEEE-styled table with navy header, alternating rows."""
    out = []
    if caption:
        out.append(_p(caption, s["caption"]))
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Times-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 9),
        ("FONTNAME", (0,1), (-1,-1), "Times-Roman"),
        ("FONTSIZE", (0,1), (-1,-1), 9),
        ("GRID", (0,0), (-1,-1), 0.5, BORDER),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]
    for i in range(1, len(rows)):
        style.append(("BACKGROUND", (0,i), (-1,i), ROW_A if i % 2 == 1 else ROW_B))
    t.setStyle(TableStyle(style))
    out.append(t)
    out.append(Spacer(1, 5 * mm))
    return out


# ── Section builders ───────────────────────────────────────────────────────
def _build_cover(req: RequirementsResponse, s: dict) -> List[Flowable]:
    now = datetime.now()
    project_name = (req.project_name or "UNTITLED SYSTEM").upper()
    out: List[Flowable] = [
        # White space for the navy banner drawn on canvas
        Spacer(1, 1 * cm),
        _p(project_name, s["cover_title"]),
        Spacer(1, 3 * mm),
        _p("Software Requirements Specification", s["cover_sub"]),
        _p("IEEE Std 830-1998 Conforming Document", s["cover_sub"]),
        Spacer(1, 18 * mm),
    ]
    # Metadata table
    meta_rows = [
        ["Document Type",    "Software Requirements Specification (SRS)"],
        ["Project Name",     req.project_name or "—"],
        ["Version",          "1.0"],
        ["Status",           "DRAFT — Pending Developer Approval"],
        ["Prepared By",      "BluePrint AI — Automated SDLC Agent"],
        ["Standard",         "IEEE Std 830-1998 / ISO/IEC 12207:2008"],
        ["Date",             now.strftime("%d %B %Y")],
    ]
    mt = Table(meta_rows, colWidths=[5 * cm, BODY_W - 5 * cm - 1 * cm])
    mt.setStyle(TableStyle([
        ("FONTNAME",      (0,0), (0,-1), "Times-Bold"),
        ("FONTNAME",      (1,0), (1,-1), "Times-Roman"),
        ("FONTSIZE",      (0,0), (-1,-1), 9.5),
        ("TEXTCOLOR",     (0,0), (0,-1), colors.white),
        ("TEXTCOLOR",     (1,0), (1,-1), HexColor("#EEEEEE")),
        ("BACKGROUND",    (0,0), (-1,-1), NAVY),
        ("GRID",          (0,0), (-1,-1), 0.5, HexColor("#3A4D7A")),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    out.append(mt)
    out.append(Spacer(1, 12 * mm))

    # Revision history
    rev_rows = [
        ["Version", "Date", "Author", "Description"],
        ["1.0", now.strftime("%d %b %Y"), "BluePrint AI", "Initial automated draft generated from project idea"],
    ]
    out.extend(_std_table(rev_rows,
        [2*cm, 3.5*cm, 4*cm, BODY_W - 9.5*cm - 1*cm], s,
        "TABLE I. REVISION HISTORY"))
    out.append(Spacer(1, 8 * mm))

    # Abstract
    out.append(_p("Abstract", s["abstract_hd"]))
    out.append(_p(req.project_overview or "No overview provided.", s["abstract_body"]))
    out.append(Spacer(1, 4 * mm))
    ts = req.recommended_tech_stack
    tech_str = f"{ts.frontend} / {ts.backend} / {ts.database}" if ts else "TBD"
    out.append(_p(
        f"<b>Index Terms</b> — Software Requirements Specification, IEEE Std 830, "
        f"functional requirements, non-functional requirements, use-case analysis, "
        f"system architecture, {tech_str}, {(req.project_name or '').lower()}",
        s["index_terms"]
    ))
    out.append(PageBreak())
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
        f"Software Requirements Specifications) and ISO/IEC 12207:2008. "
        f"This document serves as the primary contractual reference between all project stakeholders — "
        f"including product owners, software developers, quality assurance engineers, "
        f"and system administrators — governing what the system shall do and the constraints "
        f"under which it shall operate.", s["body"]
    ))

    out.append(_sub("B", "Scope of the Product", s))
    out.append(_p(
        f"The <b>{_safe(req.project_name or 'system')}</b> is a software product aimed at "
        f"delivering the following high-level value proposition:", s["body"]
    ))
    out.append(_callout(req.project_overview or "System scope not yet defined.", s))
    out.append(Spacer(1, 4 * mm))
    if req.objectives:
        out.append(_p("The primary objectives of the system are:", s["body"]))
        out.extend(_bullets(req.objectives, s))

    out.append(_sub("C", "Definitions, Acronyms, and Abbreviations", s))
    defs = [
        ("SRS",  "Software Requirements Specification"),
        ("FR",   "Functional Requirement"),
        ("NFR",  "Non-Functional Requirement"),
        ("UC",   "Use Case"),
        ("API",  "Application Programming Interface"),
        ("SDLC", "Software Development Life Cycle"),
        ("IEEE", "Institute of Electrical and Electronics Engineers"),
        ("ISO",  "International Organization for Standardization"),
        ("CRUD", "Create, Read, Update, Delete"),
        ("UI",   "User Interface"),
        ("UX",   "User Experience"),
        ("DB",   "Database"),
        ("REST", "Representational State Transfer"),
        ("JWT",  "JSON Web Token"),
        ("TBD",  "To Be Determined"),
    ]
    def_rows = [["Term / Acronym", "Definition"]] + [[k, v] for k, v in defs]
    out.extend(_std_table(def_rows, [4*cm, BODY_W - 4*cm - 1*cm], s, "TABLE II. GLOSSARY OF TERMS"))

    out.append(_sub("D", "References", s))
    refs = [
        "[1] IEEE Std 830-1998, IEEE Recommended Practice for Software Requirements Specifications, IEEE, 1998.",
        "[2] ISO/IEC 12207:2008, Systems and Software Engineering — Software Life Cycle Processes, ISO, 2008.",
        "[3] IEEE Std 29148-2018, Systems and Software Engineering — Life Cycle Processes — Requirements Engineering, IEEE, 2018.",
        "[4] ISO/IEC 25010:2011, Systems and Software Quality Requirements and Evaluation (SQuaRE), ISO, 2011.",
        "[5] R. S. Pressman, Software Engineering: A Practitioner's Approach, 9th ed., McGraw-Hill, 2019.",
    ]
    for ref in refs:
        out.append(Paragraph(f"\u2022\u2002{_safe(ref)}", s["bullet"]))
    out.append(Spacer(1, 3 * mm))

    out.append(_sub("E", "Document Overview", s))
    out.append(_p(
        "This document is structured as follows: Section II provides the overall system description "
        "and product context. Section III presents the complete specific requirements. "
        "Section IV covers external interface requirements. Section V enumerates all functional "
        "requirements with unique identifiers. Section VI details non-functional requirements. "
        "Section VII contains use case specifications. Section VIII specifies the technology stack. "
        "Section IX defines verification and validation criteria. Appendix A provides the "
        "Requirements Traceability Matrix. Appendix B contains the full glossary.", s["body"]
    ))
    return out


def _build_sec2(req: RequirementsResponse, s: dict) -> List[Flowable]:
    out = _sec("II", "Overall Description", s)

    out.append(_sub("A", "Product Perspective", s))
    out.append(_p(
        f"The {_safe(req.project_name or 'system')} is a standalone software product. "
        f"It shall operate as a multi-tier application with a presentation layer, an application "
        f"logic layer, and a data persistence layer. The system shall expose RESTful API endpoints "
        f"for communication between the frontend and backend, and shall integrate with external "
        f"services as defined in Section IV. The system boundaries are explicitly defined through "
        f"the use cases documented in Section VII.", s["body"]
    ))

    out.append(_sub("B", "Product Functions", s))
    out.append(_p("At a high level, the system shall provide the following major functions:", s["body"]))
    if req.objectives:
        out.extend(_bullets(req.objectives, s))
    else:
        out.append(_p("System functions to be elaborated during design phase.", s["body"]))

    out.append(_sub("C", "User Classes and Characteristics", s))
    out.append(_p(
        "The following user classes have been identified for this system. Each class has distinct "
        "interaction patterns, technical expertise levels, and system access privileges:", s["body"]
    ))
    if req.user_roles:
        role_rows = [["User Class", "Description", "Privilege Level"]]
        for role in req.user_roles:
            role_rows.append([role, f"Primary actor interacting with {_safe(req.project_name or 'the system')}", "Standard"])
        out.extend(_std_table(role_rows, [4*cm, BODY_W - 7*cm - 1*cm, 3*cm], s, "TABLE III. USER CLASSES"))
    else:
        out.append(_p("User classes to be defined during requirements elicitation.", s["body"]))

    out.append(_sub("D", "Operating Environment", s))
    ts = req.recommended_tech_stack
    out.append(_p(
        f"The system shall operate in a client-server environment with the following technology profile:", s["body"]
    ))
    env_rows = [
        ["Layer", "Technology", "Environment"],
        ["Presentation", ts.frontend if ts else "TBD", "Web Browser / Mobile"],
        ["Application", ts.backend if ts else "TBD", "Cloud / On-Premise Server"],
        ["Persistence", ts.database if ts else "TBD", "Dedicated Database Server"],
        ["Intelligence", ts.ai_framework if ts else "TBD", "AI/ML Inference Service"],
    ]
    out.extend(_std_table(env_rows, [4*cm, 5*cm, BODY_W - 9*cm - 1*cm], s, "TABLE IV. OPERATING ENVIRONMENT"))

    if req.assumptions:
        out.append(_sub("E", "Assumptions and Dependencies", s))
        out.append(_p("The following assumptions underpin the requirements stated in this document:", s["body"]))
        out.extend(_bullets(req.assumptions, s))

    if req.constraints:
        out.append(_sub("F", "Design and Implementation Constraints", s))
        out.append(_p(
            "The following constraints bound the design space available to the implementation team:", s["body"]
        ))
        out.extend(_bullets(req.constraints, s))

    if req.future_scope:
        out.append(_sub("G", "Future Scope and Planned Extensions", s))
        out.append(_p(
            "The following capabilities are explicitly out of scope for Version 1.0 but are "
            "planned for future releases:", s["body"]
        ))
        out.extend(_bullets(req.future_scope, s))

    return out


def _build_sec3(req: RequirementsResponse, s: dict) -> List[Flowable]:
    out = _sec("III", "Specific Requirements — Overview", s)
    out.append(_p(
        "This section and Sections IV through VI constitute the complete specification of "
        "requirements that the system shall satisfy. All requirements are categorised and "
        "uniquely identified for traceability. The identifiers follow this convention:", s["body"]
    ))
    id_rows = [
        ["Prefix", "Category", "Example"],
        ["FR-NNN",  "Functional Requirement",                    "FR-001"],
        ["NFR-NNN", "Non-Functional Requirement (Quality Attr.)", "NFR-001"],
        ["EI-NNN",  "External Interface Requirement",            "EI-001"],
        ["UC-NNN",  "Use Case Identifier",                       "UC-001"],
    ]
    out.extend(_std_table(id_rows, [3.5*cm, 8*cm, 3*cm], s, "TABLE V. REQUIREMENT IDENTIFIER CONVENTIONS"))
    out.append(_p(
        "Requirements marked [M] are Mandatory; [O] are Optional for Version 1.0. "
        "All Mandatory requirements shall be implemented before the system is accepted.", s["body"]
    ))
    if req.suggested_modules:
        out.append(_sub("A", "System Module Decomposition", s))
        out.append(_p(
            "The system is logically decomposed into the following modules. Each module "
            "corresponds to a cohesive set of functional requirements:", s["body"]
        ))
        mod_rows = [["Module", "Responsibility"]] + [[m, f"Handles {m} operations and domain logic"] for m in req.suggested_modules]
        out.extend(_std_table(mod_rows, [5*cm, BODY_W - 5*cm - 1*cm], s, "TABLE VI. MODULE DECOMPOSITION"))
    return out


def _build_sec4(req: RequirementsResponse, s: dict) -> List[Flowable]:
    out = _sec("IV", "External Interface Requirements", s)

    out.append(_sub("A", "User Interfaces", s))
    ts = req.recommended_tech_stack
    out.append(_p(
        f"The system shall provide a responsive web-based user interface implemented using "
        f"<b>{_safe(ts.frontend if ts else 'a modern frontend framework')}</b>. "
        f"The interface shall conform to WCAG 2.1 Level AA accessibility standards. "
        f"All screens shall render correctly on desktop (1280×800+), tablet (768×1024), "
        f"and mobile (375×667) viewports. Navigation shall be intuitive and "
        f"require no more than three clicks to reach any primary function.", s["body"]
    ))

    out.append(_sub("B", "Hardware Interfaces", s))
    out.append(_p(
        "The system shall not require specialised hardware beyond a standard network-connected "
        "server or cloud virtual machine. The client shall require only a web browser with "
        "JavaScript enabled. No proprietary hardware drivers or peripherals are required.", s["body"]
    ))

    out.append(_sub("C", "Software Interfaces", s))
    si_rows = [
        ["Interface", "Protocol", "Data Format", "Purpose"],
        ["Frontend ↔ Backend API", "HTTPS/REST", "JSON", "All client-server communication"],
        [f"Backend ↔ {_safe(ts.database if ts else 'Database')}", "TCP/SQL", "Binary/SQL", "Data persistence and retrieval"],
        [f"Backend ↔ {_safe(ts.ai_framework if ts else 'AI Engine')}", "HTTP", "JSON", "AI/ML inference requests"],
        ["Authentication Service", "OAuth 2.0 / JWT", "JSON", "Secure token-based authentication"],
    ]
    out.extend(_std_table(si_rows, [4*cm, 3*cm, 3*cm, BODY_W - 10*cm - 1*cm], s, "TABLE VII. SOFTWARE INTERFACES"))

    out.append(_sub("D", "Communications Interfaces", s))
    out.append(_p(
        "All external communications shall use HTTPS (TLS 1.2 minimum) to ensure data confidentiality "
        "and integrity in transit. The system shall support standard HTTP/1.1 and HTTP/2.0 protocols. "
        "WebSocket connections may be used for real-time features where applicable. "
        "All API endpoints shall enforce rate limiting to prevent abuse.", s["body"]
    ))
    return out


def _build_sec5(req: RequirementsResponse, s: dict) -> List[Flowable]:
    out = _sec("V", "System Features and Functional Requirements", s)
    out.append(_p(
        "This section enumerates every functional requirement the system shall satisfy. "
        "Each requirement is assigned a unique identifier (FR-NNN) and marked with its "
        "priority ([M] Mandatory / [O] Optional). Requirements are grouped by system feature.", s["body"]
    ))

    if not req.functional_requirements:
        out.append(_p("Functional requirements to be defined in subsequent elicitation sessions.", s["body"]))
        return out

    out.extend(_numbered_req(req.functional_requirements, "FR", s))

    # FR summary table
    summary_rows = [["ID", "Requirement (Abbreviated)", "Priority"]]
    for i, fr in enumerate(req.functional_requirements, 1):
        short = fr[:70] + "…" if len(fr) > 70 else fr
        summary_rows.append([f"FR-{i:03d}", short, "[M]"])
    out.append(Spacer(1, 4 * mm))
    out.extend(_std_table(summary_rows, [2*cm, BODY_W - 5*cm - 1*cm, 3*cm], s,
        "TABLE VIII. FUNCTIONAL REQUIREMENTS SUMMARY"))
    return out


def _build_sec6(req: RequirementsResponse, s: dict) -> List[Flowable]:
    out = _sec("VI", "Non-Functional Requirements (Quality Attributes)", s)
    out.append(_p(
        "Non-functional requirements define quality characteristics and operational "
        "constraints the system shall exhibit. They are categorised following ISO/IEC 25010:2011 "
        "product quality model and assigned unique NFR-NNN identifiers.", s["body"]
    ))

    if req.non_functional_requirements:
        out.extend(_numbered_req(req.non_functional_requirements, "NFR", s))
        out.append(Spacer(1, 4 * mm))

    # Standard quality attributes table
    qa_rows = [
        ["Quality Attribute", "Requirement", "Metric / Target"],
        ["Performance",    "Response time for all primary actions",  "< 2 seconds (P95)"],
        ["Availability",   "System uptime guarantee",                "99.5% monthly"],
        ["Scalability",    "Concurrent user sessions",               "≥ 100 simultaneous users"],
        ["Security",       "Authentication and authorisation",       "JWT / RBAC enforced"],
        ["Maintainability","Code coverage by automated tests",       "≥ 70%"],
        ["Usability",      "Task completion without training",       "≥ 80% success rate"],
        ["Portability",    "Deployment environments",                "Linux, Docker, Cloud-native"],
        ["Reliability",    "Mean Time Between Failures (MTBF)",      "≥ 720 hours"],
    ]
    out.extend(_std_table(qa_rows, [4*cm, 6*cm, BODY_W - 10*cm - 1*cm], s,
        "TABLE IX. QUALITY ATTRIBUTES SPECIFICATION"))
    return out


def _build_sec7(req: RequirementsResponse, s: dict) -> List[Flowable]:
    out = _sec("VII", "Use Case Specification", s)
    out.append(_p(
        "Use cases describe actor-system interactions that deliver observable value. "
        "Each use case follows the IEEE/UML standard format and is traceable to one or more "
        "functional requirements in Section V. User stories are expressed in the Connextra "
        "format: 'As a <role>, I want to <goal> so that <benefit>.'", s["body"]
    ))

    if not req.user_stories:
        out.append(_p("No use cases specified. To be elaborated during requirements workshops.", s["body"]))
        return out

    for i, story in enumerate(req.user_stories, 1):
        # Map each story to a FR
        fr_ref = f"FR-{((i-1) % max(len(req.functional_requirements), 1)) + 1:03d}" \
            if req.functional_requirements else "FR-001"
        uc_rows = [
            ["Field",             "Description"],
            ["Use Case ID",       f"UC-{i:03d}"],
            ["Use Case Name",     f"{_safe(story.role or 'User')} — {_safe((story.desire or '')[:50])}"],
            ["Primary Actor",     _safe(story.role or "User")],
            ["Goal",              _safe(story.desire or "—")],
            ["Pre-conditions",    "Actor is authenticated and has required permissions"],
            ["Post-conditions",   _safe(story.benefit or "—")],
            ["Main Flow",         "1. Actor initiates action via UI\n2. System validates input\n3. System processes request\n4. System returns result to actor"],
            ["Alternative Flow",  "If validation fails, system returns descriptive error message"],
            ["Linked FR",         fr_ref],
        ]
        uc_tbl = Table(uc_rows, colWidths=[4*cm, BODY_W - 4*cm - 1*cm])
        uc_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), NAVY),
            ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
            ("FONTNAME",      (0,0), (-1,0), "Times-Bold"),
            ("FONTNAME",      (0,1), (0,-1), "Times-Bold"),
            ("FONTNAME",      (1,1), (1,-1), "Times-Roman"),
            ("FONTSIZE",      (0,0), (-1,-1), 9),
            ("BACKGROUND",    (0,1), (0,-1), GREY),
            ("GRID",          (0,0), (-1,-1), 0.5, BORDER),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING",   (0,0), (-1,-1), 6),
            ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ]))
        out.append(KeepTogether([
            _p(f"TABLE X-{i}. USE CASE UC-{i:03d}", s["caption"]),
            uc_tbl,
            Spacer(1, 5 * mm),
        ]))
    return out


def _build_sec8(req: RequirementsResponse, s: dict) -> List[Flowable]:
    out = _sec("VIII", "Technology Stack Specification", s)
    ts = req.recommended_tech_stack
    out.append(_p(
        "The following technology stack is recommended based on the project requirements, "
        "team expertise assumptions, and scalability needs. Selection rationale is provided "
        "for each layer to facilitate architectural review.", s["body"]
    ))
    stack_rows = [
        ["Layer", "Selected Technology", "Category", "Justification"],
        ["Presentation",  _safe(ts.frontend if ts else "TBD"),      "Frontend Framework",  "Component-based UI, strong ecosystem"],
        ["Application",   _safe(ts.backend if ts else "TBD"),       "Backend Framework",   "High performance, type-safe APIs"],
        ["Persistence",   _safe(ts.database if ts else "TBD"),      "Database Engine",     "ACID compliance, relational integrity"],
        ["Intelligence",  _safe(ts.ai_framework if ts else "TBD"),  "AI/ML Runtime",       "Local inference, privacy-preserving"],
        ["DevOps",        "Docker + GitHub Actions",                 "CI/CD Pipeline",      "Containerised, reproducible builds"],
        ["Authentication","JWT / OAuth 2.0",                         "Security Layer",      "Stateless, industry-standard"],
    ]
    out.extend(_std_table(stack_rows,
        [3*cm, 4*cm, 3.5*cm, BODY_W - 10.5*cm - 1*cm], s,
        "TABLE XI. TECHNOLOGY STACK SPECIFICATION"))
    return out


def _build_sec9(req: RequirementsResponse, s: dict) -> List[Flowable]:
    out = _sec("IX", "Verification and Validation", s)
    out.append(_p(
        "Each requirement documented in this SRS shall be verified prior to system acceptance. "
        "The following verification methods are defined in accordance with IEEE Std 829.", s["body"]
    ))
    vv_rows = [
        ["Method",       "Description",                                          "Applies To"],
        ["Inspection",   "Manual review of source code and configuration",       "All FR, NFR"],
        ["Unit Testing", "Automated tests for individual modules (≥70% coverage)","All FR"],
        ["Integration",  "API contract testing between system layers",            "EI requirements"],
        ["System Test",  "End-to-end acceptance test per use case",              "All UC"],
        ["Performance",  "Load testing with simulated concurrent users",          "NFR (Performance)"],
        ["Security",     "Penetration testing and static code analysis",         "NFR (Security)"],
        ["UAT",          "User Acceptance Testing with real end-users",          "All UC"],
    ]
    out.extend(_std_table(vv_rows, [3*cm, 7*cm, BODY_W - 10*cm - 1*cm], s, "TABLE XII. VERIFICATION METHODS"))
    return out


def _build_traceability(req: RequirementsResponse, s: dict) -> List[Flowable]:
    out = _sec("X", "Appendix A — Requirements Traceability Matrix", s)
    out.append(_p(
        "The Requirements Traceability Matrix (RTM) below cross-references every functional "
        "requirement to its originating use case, enabling complete forward and backward "
        "traceability across the SDLC. A ✓ symbol indicates that the FR is addressed by that UC.", s["body"]
    ))
    fr_list = req.functional_requirements or []
    uc_list = req.user_stories or []

    if not fr_list:
        out.append(_p("No functional requirements defined. RTM will be populated after elicitation.", s["body"]))
        return out

    # Build matrix header
    uc_headers = [f"UC-{i:03d}" for i in range(1, min(len(uc_list) + 1, 9))]
    header_row = ["Req. ID", "Requirement (Summary)"] + uc_headers + ["Priority"]
    col_w = [2*cm, BODY_W - (2 + len(uc_headers) * 1.4 + 1.8 + 1)*cm] + [1.4*cm] * len(uc_headers) + [1.8*cm]

    matrix_rows = [header_row]
    for i, fr in enumerate(fr_list, 1):
        short = fr[:55] + "…" if len(fr) > 55 else fr
        # Simple round-robin assignment of primary UC
        uc_marks = []
        for j in range(1, len(uc_headers) + 1):
            uc_marks.append("✓" if ((i - 1) % max(len(uc_list), 1)) + 1 == j else "")
        matrix_rows.append([f"FR-{i:03d}", short] + uc_marks + ["[M]"])

    t = Table(matrix_rows, colWidths=col_w, repeatRows=1)
    tbl_style = [
        ("BACKGROUND",    (0,0), (-1,0), NAVY),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("FONTNAME",      (0,0), (-1,0), "Times-Bold"),
        ("FONTNAME",      (0,1), (-1,-1), "Times-Roman"),
        ("FONTSIZE",      (0,0), (-1,-1), 8),
        ("GRID",          (0,0), (-1,-1), 0.5, BORDER),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 4),
        ("ALIGN",         (0,0), (0,-1), "CENTER"),
        ("ALIGN",         (2,0), (-1,-1), "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ]
    for i in range(1, len(matrix_rows)):
        tbl_style.append(("BACKGROUND", (0,i), (-1,i), ROW_A if i % 2 == 1 else ROW_B))
    t.setStyle(TableStyle(tbl_style))
    out.append(_p("TABLE XIII. REQUIREMENTS TRACEABILITY MATRIX", s["caption"]))
    out.append(t)
    out.append(Spacer(1, 5 * mm))
    return out


def _build_glossary(req: RequirementsResponse, s: dict) -> List[Flowable]:
    out = _sec("XI", "Appendix B — Glossary", s)
    out.append(_p(
        "This glossary defines domain-specific and technical terms used throughout this document "
        "to ensure consistent interpretation among all stakeholders.", s["body"]
    ))
    ts = req.recommended_tech_stack
    terms = [
        ("API (Application Programming Interface)",
         "A defined set of protocols and tools for building software applications, specifying how components should interact."),
        ("Authentication",
         "The process of verifying the identity of a user or process before granting access to system resources."),
        ("Authorisation",
         "The process of determining the permissions a verified identity has within the system."),
        ("CRUD",
         "An acronym for the four basic database operations: Create, Read, Update, and Delete."),
        ("Database",
         f"A structured collection of data. This project uses {_safe(ts.database if ts else 'a relational database')} as its persistence layer."),
        ("Endpoint",
         "A specific URL within the REST API that accepts HTTP requests and returns responses."),
        ("Frontend",
         f"The client-side layer of the application, implemented using {_safe(ts.frontend if ts else 'a web framework')}."),
        ("IEEE Std 830-1998",
         "IEEE Recommended Practice for Software Requirements Specifications — the standard this document conforms to."),
        ("JWT (JSON Web Token)",
         "A compact, URL-safe means of representing claims to be transferred between two parties, used for authentication."),
        ("Requirement",
         "A condition or capability needed by a stakeholder to solve a problem or achieve an objective."),
        ("SRS",
         "Software Requirements Specification — this document."),
        ("Stakeholder",
         "Any person or organisation that affects or is affected by the system, including users, developers, and business owners."),
        ("Use Case",
         "A description of a sequence of actions performed by a system in response to a user request to accomplish a goal."),
    ]
    gl_rows = [["Term", "Definition"]] + [[t, d] for t, d in terms]
    out.extend(_std_table(gl_rows, [5*cm, BODY_W - 5*cm - 1*cm], s, "TABLE XIV. GLOSSARY"))
    return out


# ── Public API ──────────────────────────────────────────────────────────────
class SrsService:
    """Generates a complete IEEE Std 830-1998 SRS PDF document."""

    def generate_srs_pdf(self, req: RequirementsResponse) -> bytes:
        buffer = io.BytesIO()
        s = _styles()
        project_name = req.project_name or "UNTITLED"

        doc = BaseDocTemplate(
            buffer, pagesize=A4,
            leftMargin=LM, rightMargin=RM,
            topMargin=TM, bottomMargin=BM,
            title=f"SRS: {project_name}",
            author="BluePrint AI — Automated SDLC Planner",
        )
        doc._project_name = project_name

        # Single-column body frame
        body_frame = Frame(LM, BM, BODY_W, PAGE_H - TM - BM, id="body")
        cover_tpl = PageTemplate(id="Cover", frames=[body_frame], onPage=_cover_canvas)
        body_tpl  = PageTemplate(id="Body",  frames=[body_frame], onPage=_body_canvas)
        doc.addPageTemplates([cover_tpl, body_tpl])

        story: List[Flowable] = []
        story.extend(_build_cover(req, s))
        story.append(NextPageTemplate("Body"))
        story.append(PageBreak())
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

"""
docx_service.py
───────────────
Generates a comprehensive, professional Blueprint Word DOCX document
matching the PDF blueprint — including all sections, tables, and styling.
"""

import io
from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from datetime import datetime
from app.models.requirements import ProjectContext

# Brand Colors
PRIMARY_RGB = RGBColor(0, 51, 102)     # #003366 Dark Blue
SECONDARY_RGB = RGBColor(0, 80, 158)   # #00509E Blue
WHITE_RGB = RGBColor(255, 255, 255)


def _shade_cell(cell, hex_color: str):
    """Apply background fill to a table cell."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)


def _set_cell_borders(cell, color="BDC3C7", width="4"):
    """Add thin borders around a cell."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for side in ['top', 'left', 'bottom', 'right']:
        border = OxmlElement(f'w:{side}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), width)
        border.set(qn('w:color'), color)
        tcBorders.append(border)
    tcPr.append(tcBorders)


def _add_horizontal_rule(doc):
    """Add a thin horizontal rule paragraph."""
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '8')
    bottom.set(qn('w:color'), '003366')
    pBdr.append(bottom)
    pPr.append(pBdr)
    return p


def _add_sec_heading(doc, text: str):
    """Add a major section heading (navy blue, large, with underline rule)."""
    h = doc.add_paragraph()
    h.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = h.add_run(text.upper())
    run.font.name = 'Times New Roman'
    run.font.size = Pt(18)
    run.font.bold = True
    run.font.color.rgb = PRIMARY_RGB
    h.space_before = Pt(18)
    h.space_after = Pt(4)
    _add_horizontal_rule(doc)
    return h


def _add_sub_heading(doc, text: str):
    """Add a sub-section heading (darker blue, italic)."""
    h = doc.add_paragraph()
    h.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = h.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.italic = True
    run.font.color.rgb = SECONDARY_RGB
    h.space_before = Pt(12)
    h.space_after = Pt(6)
    return h


def _add_body_para(doc, text: str):
    """Add a justified body paragraph."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    p.space_after = Pt(6)
    return p


def _add_bullet(doc, text: str):
    """Add a bullet point paragraph."""
    p = doc.add_paragraph(style='List Bullet')
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    p.space_after = Pt(4)
    return p


def _add_caption(doc, text: str):
    """Add a table caption."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(10)
    run.font.bold = True
    run.font.color.rgb = PRIMARY_RGB
    p.space_after = Pt(4)
    return p


def _add_ieee_table(doc, rows_data: list, caption: str = ""):
    """Add a professional IEEE-styled table with navy header and alternating rows."""
    if caption:
        _add_caption(doc, caption)

    if not rows_data:
        return

    table = doc.add_table(rows=len(rows_data), cols=len(rows_data[0]))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'

    # Header row: Navy background, white bold text
    for i, cell_text in enumerate(rows_data[0]):
        cell = table.rows[0].cells[i]
        cell.text = ''
        run = cell.paragraphs[0].add_run(str(cell_text))
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)
        run.font.bold = True
        run.font.color.rgb = WHITE_RGB
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        _shade_cell(cell, '003366')

    # Data rows: alternating white/light grey
    for r_idx in range(1, len(rows_data)):
        bg = 'FFFFFF' if r_idx % 2 == 1 else 'F8F9FA'
        for c_idx, cell_text in enumerate(rows_data[r_idx]):
            cell = table.rows[r_idx].cells[c_idx]
            cell.text = ''
            run = cell.paragraphs[0].add_run(str(cell_text))
            run.font.name = 'Times New Roman'
            run.font.size = Pt(10)
            _shade_cell(cell, bg)
            _set_cell_borders(cell)

    doc.add_paragraph()  # spacing after table
    return table


def _add_callout(doc, text: str):
    """Add a highlighted callout/info box."""
    # Use a single-cell table to simulate callout
    table = doc.add_table(rows=1, cols=1)
    table.style = 'Table Grid'
    cell = table.rows[0].cells[0]
    cell.text = ''
    run = cell.paragraphs[0].add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    run.font.italic = True
    run.font.color.rgb = PRIMARY_RGB
    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    _shade_cell(cell, 'F0F4F8')  # Light blue background
    doc.add_paragraph()


class DocxService:
    def generate_docx(self, context: ProjectContext) -> bytes:
        doc = Document()

        # ----- Page Margins -----
        for section in doc.sections:
            section.left_margin = Cm(2.5)
            section.right_margin = Cm(2.5)
            section.top_margin = Cm(2.5)
            section.bottom_margin = Cm(2.5)

        # ----- Unpack context -----
        req = context.requirements
        arch = context.architecture
        db = context.database
        docs = context.documentation

        project_name = (req.project_name if req else "UNTITLED").upper()
        now = datetime.now()

        # =======================================================
        # COVER PAGE
        # =======================================================
        doc.add_paragraph()
        doc.add_paragraph()
        title_p = doc.add_paragraph()
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = title_p.add_run(project_name)
        title_run.font.name = 'Times New Roman'
        title_run.font.size = Pt(36)
        title_run.font.bold = True
        title_run.font.color.rgb = PRIMARY_RGB
        title_p.space_after = Pt(6)

        sub_p = doc.add_paragraph()
        sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sub_run = sub_p.add_run('Comprehensive Master Project Blueprint')
        sub_run.font.name = 'Times New Roman'
        sub_run.font.size = Pt(16)
        sub_run.font.color.rgb = SECONDARY_RGB
        sub_p.space_after = Pt(4)

        sub2_p = doc.add_paragraph()
        sub2_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sub2_run = sub2_p.add_run('End-to-End System Specifications & Documentation')
        sub2_run.font.name = 'Times New Roman'
        sub2_run.font.size = Pt(13)
        sub2_run.font.italic = True
        sub2_run.font.color.rgb = SECONDARY_RGB

        _add_horizontal_rule(doc)
        doc.add_paragraph()

        # Cover metadata table
        meta_rows = [
            ["Document Type", "Master Blueprint / Technical Specification"],
            ["Project Name", req.project_name if req else "—"],
            ["Version", "1.0 (Release)"],
            ["Date", now.strftime("%d %B %Y")],
            ["Prepared By", "BluePrint AI — Automated SDLC Agent"],
        ]
        _add_ieee_table(doc, meta_rows, "")

        doc.add_paragraph()
        # Revision History
        rev_rows = [
            ["Version", "Date", "Author", "Change Description"],
            ["1.0", now.strftime("%d %b %Y"), "BluePrint AI", "Initial project blueprint generated"],
        ]
        _add_ieee_table(doc, rev_rows, "TABLE I. REVISION HISTORY")

        doc.add_page_break()

        # =======================================================
        # TABLE OF CONTENTS (Manual)
        # =======================================================
        _add_sec_heading(doc, "Table of Contents")
        toc_items = [
            ("I.",   "Executive Summary & Problem Statement"),
            ("II.",  "Functional & Non-Functional Requirements"),
            ("III.", "System Architecture & Design"),
            ("IV.",  "Database Design & Entity Schema"),
            ("V.",   "Implementation & Installation Guide"),
            ("VI.",  "API Endpoints Documentation"),
            ("VII.", "Use Case Specifications"),
            ("VIII.","Verification & Validation Plan"),
            ("IX.",  "System Glossary"),
            ("X.",   "References"),
        ]
        for num, title in toc_items:
            p = doc.add_paragraph()
            run_num = p.add_run(f"{num}  ")
            run_num.font.bold = True
            run_num.font.name = 'Times New Roman'
            run_num.font.color.rgb = PRIMARY_RGB
            run_title = p.add_run(title)
            run_title.font.name = 'Times New Roman'
            run_title.font.size = Pt(11)
            p.space_after = Pt(4)

        doc.add_page_break()

        # =======================================================
        # I. EXECUTIVE SUMMARY
        # =======================================================
        _add_sec_heading(doc, "I. Executive Summary")

        _add_sub_heading(doc, "A. Problem Statement & Overview")
        overview = (getattr(docs, "project_overview", None) or
                    (req.project_overview if req else "No overview provided."))
        _add_callout(doc, overview)

        if req and req.objectives:
            _add_sub_heading(doc, "B. Project Objectives")
            for obj in req.objectives:
                _add_bullet(doc, obj)

        if req and req.assumptions:
            _add_sub_heading(doc, "C. Assumptions & Dependencies")
            for a in req.assumptions:
                _add_bullet(doc, a)

        if req and req.constraints:
            _add_sub_heading(doc, "D. Design Constraints")
            for c in req.constraints:
                _add_bullet(doc, c)

        if req and req.future_scope:
            _add_sub_heading(doc, "E. Future Scope")
            for f in req.future_scope:
                _add_bullet(doc, f)

        doc.add_page_break()

        # =======================================================
        # II. REQUIREMENTS
        # =======================================================
        _add_sec_heading(doc, "II. Requirements Specification")

        if req and req.functional_requirements:
            _add_sub_heading(doc, "A. Functional Requirements")
            _add_body_para(doc, "The following functional requirements describe the core behaviour the system shall exhibit. Each is assigned a unique identifier (FR-NNN).")
            fr_rows = [["ID", "Functional Requirement", "Priority"]]
            for i, item in enumerate(req.functional_requirements, 1):
                fr_rows.append([f"FR-{i:03d}", item, "[M]"])
            _add_ieee_table(doc, fr_rows, "TABLE II. FUNCTIONAL REQUIREMENTS")

        if req and req.non_functional_requirements:
            _add_sub_heading(doc, "B. Non-Functional Requirements (Quality Attributes)")
            _add_body_para(doc, "Non-functional requirements define system quality attributes per ISO/IEC 25010:2011.")
            nfr_rows = [["ID", "Non-Functional Requirement"]]
            for i, item in enumerate(req.non_functional_requirements, 1):
                nfr_rows.append([f"NFR-{i:03d}", item])
            _add_ieee_table(doc, nfr_rows, "TABLE III. NON-FUNCTIONAL REQUIREMENTS")

        # Quality attributes table
        _add_sub_heading(doc, "C. Quality Attributes (ISO/IEC 25010)")
        qa_rows = [
            ["Quality Attribute", "Requirement", "Target Metric"],
            ["Performance", "Response time for primary actions", "< 2 seconds (P95)"],
            ["Availability", "System uptime", "≥ 99.5% monthly"],
            ["Scalability", "Concurrent users", "≥ 100 simultaneous"],
            ["Security", "Auth mechanism", "JWT / RBAC"],
            ["Maintainability", "Code test coverage", "≥ 70%"],
            ["Usability", "Task completion without training", "≥ 80% success rate"],
        ]
        _add_ieee_table(doc, qa_rows, "TABLE IV. QUALITY ATTRIBUTES")

        if req and req.user_roles:
            _add_sub_heading(doc, "D. User Classes & Access Levels")
            role_rows = [["User Class", "Description", "Access Level"]]
            for role in req.user_roles:
                role_rows.append([role, f"Interacts with {req.project_name or 'the system'}", "Role-based"])
            _add_ieee_table(doc, role_rows, "TABLE V. USER CLASSES")

        doc.add_page_break()

        # =======================================================
        # III. SYSTEM ARCHITECTURE
        # =======================================================
        _add_sec_heading(doc, "III. System Architecture & Design")

        if arch:
            _add_sub_heading(doc, "A. High Level Architecture")
            _add_body_para(doc, arch.high_level_architecture or "No architecture defined.")

            _add_sub_heading(doc, "B. System Tier Diagram (Textual)")
            tier_rows = [
                ["Tier", "Layer", "Technology", "Responsibility"],
                ["1", "Presentation", (req.recommended_tech_stack.frontend if req and req.recommended_tech_stack else "—"), "User Interface & Interaction"],
                ["2", "Application", (req.recommended_tech_stack.backend if req and req.recommended_tech_stack else "—"), "Business Logic & API"],
                ["3", "Persistence", (req.recommended_tech_stack.database if req and req.recommended_tech_stack else "—"), "Data Storage & Retrieval"],
            ]
            _add_ieee_table(doc, tier_rows, "TABLE VI. SYSTEM TIERS")

            if arch.component_breakdown:
                _add_sub_heading(doc, "C. Module Decomposition")
                _add_body_para(doc, "The system is decomposed into the following modules:")
                c_rows = [["Module Name", "Dependencies", "Responsibility"]]
                for comp in arch.component_breakdown:
                    deps = ", ".join(comp.dependencies) if getattr(comp, "dependencies", None) else "None"
                    c_rows.append([comp.name, deps, comp.description])
                _add_ieee_table(doc, c_rows, "TABLE VII. MODULE DECOMPOSITION")

            _add_sub_heading(doc, "D. Data Flow Description")
            _add_body_para(doc, arch.data_flow or "Data flows from client via REST API to the backend, which queries the database and returns structured JSON responses.")

            if getattr(arch, "folder_structure", None):
                _add_sub_heading(doc, "E. Project Folder Structure")
                for line in arch.folder_structure:
                    _add_bullet(doc, line)

        doc.add_page_break()

        # =======================================================
        # IV. DATABASE DESIGN
        # =======================================================
        _add_sec_heading(doc, "IV. Database Design & Entity Schema")

        if db:
            _add_sub_heading(doc, "A. Entity Relationship Overview")
            _add_body_para(doc, f"The system database contains {len(db.entities or [])} entities. Each entity is fully defined below with its attributes and data types.")

            if db.entities:
                for idx, ent in enumerate(db.entities, 1):
                    _add_sub_heading(doc, f"Entity {idx}: {ent.name}")
                    ent_rows = [["Attribute", "Data Type / Definition"]]
                    for attr in ent.attributes:
                        if isinstance(attr, str):
                            parts = attr.split(" ", 1)
                            ent_rows.append([parts[0], parts[1] if len(parts) > 1 else "TEXT"])
                        else:
                            ent_rows.append([attr.get('name', ''), attr.get('type', 'TEXT')])
                    _add_ieee_table(doc, ent_rows, f"TABLE VIII-{idx}. ENTITY: {ent.name.upper()}")

            if db.sql_schema:
                _add_sub_heading(doc, "B. SQL DDL Schema")
                _add_body_para(doc, "The following DDL can be used to initialize the database schema:")
                # Add schema as monospace block
                p = doc.add_paragraph()
                run = p.add_run(db.sql_schema)
                run.font.name = 'Courier New'
                run.font.size = Pt(9)
                p.paragraph_format.left_indent = Cm(1.0)
        else:
            _add_body_para(doc, "No database design generated.")

        doc.add_page_break()

        # =======================================================
        # V. INSTALLATION & SETUP GUIDE
        # =======================================================
        _add_sec_heading(doc, "V. Implementation & Installation Guide")

        if docs and getattr(docs, "installation_guide", None):
            _add_sub_heading(doc, "A. Prerequisites & Environment Setup")
            _add_body_para(doc, docs.installation_guide)

        _add_sub_heading(doc, "B. System Requirements")
        sys_rows = [
            ["Component", "Minimum Requirement"],
            ["OS", "Ubuntu 22.04 / Windows 10 / macOS 12+"],
            ["Memory (RAM)", "8 GB"],
            ["Storage", "20 GB free space"],
            ["Runtime", "Python 3.10+, Node.js 18+"],
            ["Network", "Stable internet connection"],
        ]
        _add_ieee_table(doc, sys_rows, "TABLE IX. SYSTEM REQUIREMENTS")

        _add_sub_heading(doc, "C. Backend Setup Steps")
        backend_steps = [
            "Clone the repository: git clone <repo_url>",
            "Navigate to backend/: cd backend",
            "Create a virtual environment: python -m venv venv",
            "Activate the environment: source venv/bin/activate  (or .\\venv\\Scripts\\activate on Windows)",
            "Install dependencies: pip install -r requirements.txt",
            "Copy environment variables: cp .env.example .env",
            "Run database migrations: alembic upgrade head",
            "Start the server: uvicorn app.main:app --reload",
        ]
        for step in backend_steps:
            _add_bullet(doc, step)

        _add_sub_heading(doc, "D. Frontend Setup Steps")
        frontend_steps = [
            "Navigate to frontend/: cd frontend",
            "Install dependencies: npm install",
            "Copy environment variables: cp .env.example .env",
            "Start the development server: npm run dev",
            "Access the app at: http://localhost:5173",
        ]
        for step in frontend_steps:
            _add_bullet(doc, step)

        if docs and getattr(docs, "deployment_notes", None):
            _add_sub_heading(doc, "E. Deployment & Production Notes")
            _add_body_para(doc, docs.deployment_notes)

        if docs and getattr(docs, "developer_notes", None):
            _add_sub_heading(doc, "F. Developer Notes & Guidelines")
            _add_body_para(doc, docs.developer_notes)

        doc.add_page_break()

        # =======================================================
        # VI. API DOCUMENTATION
        # =======================================================
        _add_sec_heading(doc, "VI. API Endpoints Documentation")
        _add_body_para(doc, "All API endpoints follow RESTful conventions over HTTPS. Requests and responses are in JSON format. Authentication uses JWT Bearer tokens.")

        _add_sub_heading(doc, "A. Authentication Pattern")
        _add_body_para(doc, "Include the JWT token in every authenticated request:")
        p = doc.add_paragraph()
        run = p.add_run("Authorization: Bearer <your_jwt_token>")
        run.font.name = 'Courier New'
        run.font.size = Pt(10)
        run.font.color.rgb = PRIMARY_RGB

        if docs and getattr(docs, "api_documentation", None):
            _add_sub_heading(doc, "B. Endpoint Specifications")
            _add_body_para(doc, docs.api_documentation)
        else:
            _add_sub_heading(doc, "B. Core Endpoints")
            api_rows = [
                ["Method", "Endpoint", "Auth Required", "Description"],
                ["POST", "/auth/register", "No", "Register a new user account"],
                ["POST", "/auth/login", "No", "Login and receive JWT token"],
                ["GET", "/api/v1/resource", "Yes", "List all resources (paginated)"],
                ["POST", "/api/v1/resource", "Yes", "Create a new resource"],
                ["GET", "/api/v1/resource/{id}", "Yes", "Get a single resource by ID"],
                ["PUT", "/api/v1/resource/{id}", "Yes", "Update an existing resource"],
                ["DELETE", "/api/v1/resource/{id}", "Yes (Admin)", "Delete a resource"],
            ]
            _add_ieee_table(doc, api_rows, "TABLE X. API ENDPOINTS")

        doc.add_page_break()

        # =======================================================
        # VII. USE CASE SPECIFICATIONS
        # =======================================================
        _add_sec_heading(doc, "VII. Use Case Specifications")
        _add_body_para(doc, "Each use case describes a distinct interaction between an actor and the system that delivers measurable value.")

        if req and req.user_stories:
            for i, story in enumerate(req.user_stories, 1):
                _add_sub_heading(doc, f"Use Case UC-{i:03d}: {story.role} — {(story.desire or '')[:50]}")
                uc_rows = [
                    ["Field", "Description"],
                    ["Use Case ID", f"UC-{i:03d}"],
                    ["Primary Actor", story.role or "User"],
                    ["Goal", story.desire or "—"],
                    ["Pre-conditions", "Actor is authenticated and authorised"],
                    ["Post-conditions / Benefit", story.benefit or "—"],
                    ["Main Flow", "1. Actor initiates action\n2. System validates input\n3. System processes request\n4. System returns result"],
                    ["Alternative Flow", "Validation failure → System returns descriptive error"],
                ]
                _add_ieee_table(doc, uc_rows, f"TABLE XI-{i}. USE CASE UC-{i:03d}")
        else:
            _add_body_para(doc, "No use cases defined.")

        doc.add_page_break()

        # =======================================================
        # VIII. VERIFICATION & VALIDATION
        # =======================================================
        _add_sec_heading(doc, "VIII. Verification & Validation Plan")
        _add_body_para(doc, "Every requirement shall be verified prior to system acceptance using the methods below.")

        vv_rows = [
            ["Method", "Description", "Applies To"],
            ["Inspection", "Manual review of code and config", "All FR, NFR"],
            ["Unit Testing", "Automated module tests (≥ 70% coverage)", "All FR"],
            ["Integration Testing", "API contract validation between tiers", "EI Requirements"],
            ["System Testing", "End-to-end acceptance per use case", "All UC"],
            ["Performance Testing", "Load test with simulated concurrent users", "NFR (Performance)"],
            ["Security Audit", "Penetration test + static analysis", "NFR (Security)"],
            ["User Acceptance Testing", "Real-user testing against scenarios", "All UC"],
        ]
        _add_ieee_table(doc, vv_rows, "TABLE XII. VERIFICATION METHODS")

        doc.add_page_break()

        # =======================================================
        # IX. GLOSSARY
        # =======================================================
        _add_sec_heading(doc, "IX. System Glossary")
        _add_body_para(doc, "Domain-specific and technical terms used throughout this document.")

        terms = [
            ("API", "Application Programming Interface — a defined set of protocols for building software."),
            ("Authentication", "Verifying the identity of a user or process."),
            ("Authorisation", "Determining access permissions for a verified identity."),
            ("CRUD", "Create, Read, Update, Delete — basic database operations."),
            ("DFD", "Data Flow Diagram — depicts the flow of data through a system."),
            ("JWT", "JSON Web Token — compact, URL-safe means of representing claims."),
            ("REST", "Representational State Transfer — architectural style for APIs."),
            ("SDLC", "Software Development Life Cycle."),
            ("SRS", "Software Requirements Specification."),
            ("UAT", "User Acceptance Testing."),
            ("Use Case", "Description of actor-system interaction to achieve a goal."),
        ]
        gl_rows = [["Term", "Definition"]] + [[t, d] for t, d in terms]
        _add_ieee_table(doc, gl_rows, "TABLE XIII. GLOSSARY OF TERMS")

        doc.add_page_break()

        # =======================================================
        # X. REFERENCES
        # =======================================================
        _add_sec_heading(doc, "X. References")
        refs = [
            "[1] IEEE Std 830-1998, IEEE Recommended Practice for Software Requirements Specifications.",
            "[2] ISO/IEC 12207:2008, Systems and Software Engineering — Software Life Cycle Processes.",
            "[3] ISO/IEC 25010:2011, Systems and Software Quality Requirements and Evaluation (SQuaRE).",
            "[4] R. S. Pressman, Software Engineering: A Practitioner's Approach, 9th ed., McGraw-Hill, 2019.",
            "[5] IEEE Std 829, IEEE Standard for Software and System Test Documentation.",
        ]
        for ref in refs:
            _add_bullet(doc, ref)

        # =======================================================
        # Save & return
        # =======================================================
        buffer = io.BytesIO()
        doc.save(buffer)
        return buffer.getvalue()

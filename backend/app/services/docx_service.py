import io
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from datetime import datetime

from app.models.requirements import ProjectContext

class DocxService:
    """Compiles the ProjectContext produced by the planning agents into an
    IEEE Standard formatted DOCX document using python-docx.
    """

    def generate_docx(self, context: ProjectContext) -> bytes:
        doc = Document()

        # Page Setup - Standard 1 inch margins
        for section in doc.sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)

        # Set default styles to Times New Roman (IEEE Standard font)
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Times New Roman'
        font.size = Pt(10)
        font.color.rgb = RGBColor(0, 0, 0) # Black

        project_name = "UNTITLED SYSTEM SPECIFICATION"
        overview = ""
        if context.requirements:
            project_name = context.requirements.project_name or project_name
            overview = context.requirements.project_overview or ""

        # ─── 1. IEEE TITLE & COVER PAGE ───
        title_p = doc.add_paragraph()
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_p.paragraph_format.space_before = Pt(72)
        title_p.paragraph_format.space_after = Pt(12)
        title_run = title_p.add_run(project_name.upper())
        title_run.font.name = 'Times New Roman'
        title_run.font.size = Pt(24)
        title_run.font.bold = True
        title_run.font.color.rgb = RGBColor(0, 0, 0)

        subtitle_p = doc.add_paragraph()
        subtitle_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        subtitle_p.paragraph_format.space_after = Pt(24)
        sub_run = subtitle_p.add_run("SYSTEM ENGINEERING BLUEPRINT AND SRS DOCUMENTATION")
        sub_run.font.name = 'Times New Roman'
        sub_run.font.size = Pt(12)
        sub_run.font.bold = False
        sub_run.font.color.rgb = RGBColor(80, 80, 80)

        author_p = doc.add_paragraph()
        author_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        author_p.paragraph_format.space_after = Pt(48)
        auth_run = author_p.add_run(
            f"Prepared by: BluePrint Automated SDLC Agent Suite\n"
            f"Date: {datetime.now().strftime('%B %d, %Y')}\n"
            f"Standards Compliance: IEEE Std 830-1998 / ISO 12207"
        )
        auth_run.font.name = 'Times New Roman'
        auth_run.font.size = Pt(10)
        auth_run.font.color.rgb = RGBColor(0, 0, 0)

        if overview:
            # Abstract header
            abs_h = doc.add_paragraph()
            abs_h.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            abs_h_run = abs_h.add_run("Abstract—")
            abs_h_run.font.name = 'Times New Roman'
            abs_h_run.font.bold = True
            abs_h_run.font.italic = True
            
            abs_run = abs_h.add_run(overview)
            abs_run.font.name = 'Times New Roman'
            abs_run.font.italic = True
            abs_run.font.size = Pt(10)

        doc.add_page_break()

        # Helper for IEEE custom headings
        def add_ieee_heading(text: str, level: int):
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(18)
            h.paragraph_format.space_after = Pt(6)
            h.paragraph_format.keep_with_next = True
            
            run = h.add_run(text)
            run.font.name = 'Times New Roman'
            if level == 1:
                run.font.size = Pt(12)
                run.font.bold = True
                h.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif level == 2:
                run.font.size = Pt(11)
                run.font.bold = True
                run.font.italic = True
                h.alignment = WD_ALIGN_PARAGRAPH.LEFT
            else:
                run.font.size = Pt(10)
                run.font.italic = True
                h.alignment = WD_ALIGN_PARAGRAPH.LEFT
            return h

        # ─── 2. REQUIREMENTS SECTION ───
        if context.requirements:
            req = context.requirements
            add_ieee_heading("II. SOFTWARE REQUIREMENTS SPECIFICATION", 1)

            add_ieee_heading("A. Project Scope and Overview", 2)
            doc.add_paragraph(req.project_overview)

            if req.objectives:
                add_ieee_heading("B. System Objectives", 2)
                for obj in req.objectives:
                    doc.add_paragraph(obj, style='List Bullet')

            if req.functional_requirements:
                add_ieee_heading("C. Functional Requirements", 2)
                for f_req in req.functional_requirements:
                    doc.add_paragraph(f_req, style='List Bullet')

            if req.non_functional_requirements:
                add_ieee_heading("D. Non-Functional Requirements", 2)
                for nf_req in req.non_functional_requirements:
                    doc.add_paragraph(nf_req, style='List Bullet')

            if req.user_roles:
                add_ieee_heading("E. User Roles & Personas", 2)
                for role in req.user_roles:
                    doc.add_paragraph(role, style='List Bullet')

            if req.user_stories:
                add_ieee_heading("F. Use Case / User Story Breakdown", 2)
                
                # IEEE Style Table Caption
                caption = doc.add_paragraph()
                caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
                cap_run = caption.add_run("TABLE I. USER STORY SPECIFICATION")
                cap_run.font.bold = True
                cap_run.font.size = Pt(9)
                
                table = doc.add_table(rows=1, cols=3)
                table.autofit = True
                
                hdr_cells = table.rows[0].cells
                hdr_cells[0].text = 'Role'
                hdr_cells[1].text = 'Desire'
                hdr_cells[2].text = 'Benefit'
                for cell in hdr_cells:
                    cell.paragraphs[0].runs[0].font.bold = True
                    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="EAECEE"/>')
                    cell._tc.get_or_add_tcPr().append(shading_elm)

                for story in req.user_stories:
                    row_cells = table.add_row().cells
                    row_cells[0].text = story.role or ""
                    row_cells[1].text = story.desire or ""
                    row_cells[2].text = story.benefit or ""

            if req.recommended_tech_stack:
                add_ieee_heading("G. Technology Stack Composition", 2)
                ts = req.recommended_tech_stack
                
                caption = doc.add_paragraph()
                caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
                cap_run = caption.add_run("TABLE II. RECOMMENDED TECHNOLOGY PROFILE")
                cap_run.font.bold = True
                cap_run.font.size = Pt(9)

                table = doc.add_table(rows=5, cols=2)
                table.rows[0].cells[0].text = "Layer"
                table.rows[0].cells[1].text = "Technology Profile"
                for cell in table.rows[0].cells:
                    cell.paragraphs[0].runs[0].font.bold = True
                    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="EAECEE"/>')
                    cell._tc.get_or_add_tcPr().append(shading_elm)

                tech_rows = [
                    ("Frontend Client", ts.frontend),
                    ("Backend Application", ts.backend),
                    ("Database Server", ts.database),
                    ("Inference Engine", ts.ai_framework),
                ]
                for idx, (layer, tech) in enumerate(tech_rows, start=1):
                    table.rows[idx].cells[0].text = layer
                    table.rows[idx].cells[1].text = tech or "—"

            doc.add_page_break()

        # ─── 3. SYSTEM ARCHITECTURE ───
        if context.architecture:
            arch = context.architecture
            add_ieee_heading("III. SYSTEM ARCHITECTURE DESIGN", 1)

            add_ieee_heading("A. High-Level Architecture Description", 2)
            doc.add_paragraph(arch.high_level_architecture)

            if arch.data_flow:
                add_ieee_heading("B. Information Flow & Core Mechanics", 2)
                doc.add_paragraph(arch.data_flow)

            if arch.folder_structure:
                add_ieee_heading("C. Logical Project Directory Structure", 2)
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.5)
                run = p.add_run("\n".join(arch.folder_structure))
                run.font.name = 'Courier New'
                run.font.size = Pt(9)

            if arch.component_breakdown:
                add_ieee_heading("D. Component Decomposition", 2)
                for comp in arch.component_breakdown:
                    p = doc.add_paragraph()
                    p.add_run(f"Component: {comp.name}").bold = True
                    doc.add_paragraph(comp.description or "")
                    if comp.dependencies:
                        dep_p = doc.add_paragraph()
                        dep_p.paragraph_format.left_indent = Inches(0.25)
                        dep_p.add_run("Dependencies: ").italic = True
                        dep_p.add_run(", ".join(comp.dependencies))

            doc.add_page_break()

        # ─── 4. DATABASE SCHEMA ───
        if context.database:
            db = context.database
            add_ieee_heading("IV. DATABASE DESIGN AND SCHEMA NORMALIZATION", 1)

            if db.database_overview:
                add_ieee_heading("A. Database Overview", 2)
                doc.add_paragraph(db.database_overview)

            if db.normalization_notes:
                add_ieee_heading("B. Normalization and Integrity Constraints", 2)
                doc.add_paragraph(db.normalization_notes)

            if db.relationships:
                add_ieee_heading("C. Entity-Relationship Cardinalities", 2)
                for rel in db.relationships:
                    doc.add_paragraph(rel, style='List Bullet')

            if db.entities:
                add_ieee_heading("D. Entity Specifications", 2)
                for ent in db.entities:
                    p = doc.add_paragraph()
                    p.add_run(f"Table Schema: {ent.name}").bold = True
                    doc.add_paragraph(ent.description or "")
                    
                    if ent.attributes:
                        table = doc.add_table(rows=1, cols=1)
                        hdr_cell = table.rows[0].cells[0]
                        hdr_cell.text = "Columns / Attributes"
                        hdr_cell.paragraphs[0].runs[0].font.bold = True
                        shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="EAECEE"/>')
                        hdr_cell._tc.get_or_add_tcPr().append(shading_elm)
                        
                        for attr in ent.attributes:
                            row = table.add_row()
                            row.cells[0].text = attr

                    p_keys = []
                    if ent.primary_key:
                        p_keys.append(f"Primary Key: {ent.primary_key}")
                    if ent.foreign_keys:
                        p_keys.append(f"Foreign Keys: {', '.join(ent.foreign_keys)}")
                    if p_keys:
                        doc.add_paragraph(" | ".join(p_keys))

            if db.sql_schema:
                add_ieee_heading("E. ANSI-Compliant DDL Statements", 2)
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.5)
                run = p.add_run(db.sql_schema)
                run.font.name = 'Courier New'
                run.font.size = Pt(9)

            doc.add_page_break()

        # ─── 5. DOCUMENTATION ───
        if context.documentation:
            d = context.documentation
            add_ieee_heading("V. SYSTEM EXECUTION AND REFERENCE DOCUMENTATION", 1)

            if d.project_overview:
                add_ieee_heading("A. System Execution Summary", 2)
                doc.add_paragraph(d.project_overview)

            if d.installation_guide:
                add_ieee_heading("B. Deployment & Installation Blueprint", 2)
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.5)
                run = p.add_run(d.installation_guide)
                run.font.name = 'Courier New'
                run.font.size = Pt(9)

            if d.api_documentation:
                add_ieee_heading("C. API Interface Profiles", 2)
                doc.add_paragraph(d.api_documentation)

            if d.developer_notes:
                add_ieee_heading("D. Development Practices & Conventions", 2)
                doc.add_paragraph(d.developer_notes)

        # Save to byte stream
        stream = io.BytesIO()
        doc.save(stream)
        return stream.getvalue()

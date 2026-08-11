import io
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from datetime import datetime

from app.models.requirements import ProjectContext

class DocxService:
    """Compiles the ProjectContext produced by the planning agents into a
    professionally-styled DOCX document using python-docx.
    """

    def generate_docx(self, context: ProjectContext) -> bytes:
        doc = Document()

        # Set default styles
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Arial'
        font.size = Pt(11)
        font.color.rgb = RGBColor(15, 23, 42) # Slate-900

        project_name = "Untitled Project"
        overview = ""
        if context.requirements:
            project_name = context.requirements.project_name or project_name
            overview = context.requirements.project_overview or ""

        # ─── 1. COVER PAGE ───
        title_p = doc.add_paragraph()
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = title_p.add_run(f"\n\n\n\n📐\n{project_name}")
        title_run.font.name = 'Arial'
        title_run.font.size = Pt(32)
        title_run.font.bold = True
        title_run.font.color.rgb = RGBColor(79, 70, 229) # Indigo-600

        subtitle_p = doc.add_paragraph()
        subtitle_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sub_run = subtitle_p.add_run("Software Blueprint & Requirements Specification")
        sub_run.font.size = Pt(16)
        sub_run.font.color.rgb = RGBColor(124, 58, 237) # Violet-600

        meta_p = doc.add_paragraph()
        meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        meta_run = meta_p.add_run(f"\n\n\nGenerated on {datetime.now().strftime('%B %d, %Y')}\nCreated by BluePrint AI")
        meta_run.font.size = Pt(10)
        meta_run.font.italic = True
        meta_run.font.color.rgb = RGBColor(100, 116, 139) # Slate-500

        doc.add_page_break()

        # Helper for custom section headers
        def add_heading(text: str, level: int):
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(18)
            h.paragraph_format.space_after = Pt(6)
            h.paragraph_format.keep_with_next = True
            
            run = h.add_run(text)
            run.font.name = 'Arial'
            run.font.bold = True
            if level == 1:
                run.font.size = Pt(18)
                run.font.color.rgb = RGBColor(79, 70, 229)
            elif level == 2:
                run.font.size = Pt(14)
                run.font.color.rgb = RGBColor(124, 58, 237)
            else:
                run.font.size = Pt(12)
                run.font.color.rgb = RGBColor(15, 23, 42)
            return h

        # ─── 2. REQUIREMENTS SECTION ───
        if context.requirements:
            req = context.requirements
            add_heading("1. Software Requirements Specification", 1)

            add_heading("Project Overview", 2)
            doc.add_paragraph(req.project_overview)

            if req.objectives:
                add_heading("Objectives", 2)
                for obj in req.objectives:
                    doc.add_paragraph(obj, style='List Bullet')

            if req.functional_requirements:
                add_heading("Functional Requirements", 2)
                for f_req in req.functional_requirements:
                    doc.add_paragraph(f_req, style='List Bullet')

            if req.non_functional_requirements:
                add_heading("Non-Functional Requirements", 2)
                for nf_req in req.non_functional_requirements:
                    doc.add_paragraph(nf_req, style='List Bullet')

            if req.user_roles:
                add_heading("User Roles", 2)
                for role in req.user_roles:
                    doc.add_paragraph(role, style='List Bullet')

            if req.user_stories:
                add_heading("User Stories", 2)
                table = doc.add_table(rows=1, cols=3)
                table.autofit = True
                
                # Header formatting
                hdr_cells = table.rows[0].cells
                hdr_cells[0].text = 'Role'
                hdr_cells[1].text = 'Desire'
                hdr_cells[2].text = 'Benefit'
                for cell in hdr_cells:
                    cell.paragraphs[0].runs[0].font.bold = True
                    # Light shading
                    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F1F5F9"/>')
                    cell._tc.get_or_add_tcPr().append(shading_elm)

                for story in req.user_stories:
                    row_cells = table.add_row().cells
                    row_cells[0].text = story.role or ""
                    row_cells[1].text = story.desire or ""
                    row_cells[2].text = story.benefit or ""

            if req.recommended_tech_stack:
                add_heading("Recommended Tech Stack", 2)
                ts = req.recommended_tech_stack
                table = doc.add_table(rows=5, cols=2)
                table.rows[0].cells[0].text = "Layer"
                table.rows[0].cells[1].text = "Technology"
                for cell in table.rows[0].cells:
                    cell.paragraphs[0].runs[0].font.bold = True
                    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F1F5F9"/>')
                    cell._tc.get_or_add_tcPr().append(shading_elm)

                tech_rows = [
                    ("Frontend", ts.frontend),
                    ("Backend", ts.backend),
                    ("Database", ts.database),
                    ("AI / LLM", ts.ai_framework),
                ]
                for idx, (layer, tech) in enumerate(tech_rows, start=1):
                    table.rows[idx].cells[0].text = layer
                    table.rows[idx].cells[1].text = tech or "—"

            doc.add_page_break()

        # ─── 3. SYSTEM ARCHITECTURE ───
        if context.architecture:
            arch = context.architecture
            add_heading("2. System Architecture", 1)

            add_heading("High-Level Architecture Description", 2)
            doc.add_paragraph(arch.high_level_architecture)

            if arch.data_flow:
                add_heading("Data Flow & Mechanics", 2)
                doc.add_paragraph(arch.data_flow)

            if arch.folder_structure:
                add_heading("Recommended Directory Structure", 2)
                # Code block representation
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.5)
                run = p.add_run("\n".join(arch.folder_structure))
                run.font.name = 'Courier New'
                run.font.size = Pt(9.5)

            if arch.component_breakdown:
                add_heading("Component Breakdown", 2)
                for comp in arch.component_breakdown:
                    p = doc.add_paragraph()
                    p.add_run(f"{comp.name}: ").bold = True
                    p.add_run(comp.description or "")
                    if comp.dependencies:
                        dep_p = doc.add_paragraph()
                        dep_p.paragraph_format.left_indent = Inches(0.25)
                        dep_p.add_run("Dependencies: ").italic = True
                        dep_p.add_run(", ".join(comp.dependencies))

            doc.add_page_break()

        # ─── 4. DATABASE SCHEMA ───
        if context.database:
            db = context.database
            add_heading("3. Database Schema & Normalization", 1)

            if db.database_overview:
                add_heading("Overview", 2)
                doc.add_paragraph(db.database_overview)

            if db.normalization_notes:
                add_heading("Normalization & Design Decisions", 2)
                doc.add_paragraph(db.normalization_notes)

            if db.relationships:
                add_heading("Entity Relationships", 2)
                for rel in db.relationships:
                    doc.add_paragraph(rel, style='List Bullet')

            if db.entities:
                add_heading("Table & Entities Definition", 2)
                for ent in db.entities:
                    p = doc.add_paragraph()
                    p.add_run(f"Table: {ent.name}").bold = True
                    doc.add_paragraph(ent.description or "")
                    
                    if ent.attributes:
                        table = doc.add_table(rows=1, cols=1)
                        hdr_cell = table.rows[0].cells[0]
                        hdr_cell.text = "Columns / Attributes"
                        hdr_cell.paragraphs[0].runs[0].font.bold = True
                        
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
                add_heading("SQL DDL Script", 2)
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.5)
                run = p.add_run(db.sql_schema)
                run.font.name = 'Courier New'
                run.font.size = Pt(9.5)

            doc.add_page_break()

        # ─── 5. DOCUMENTATION ───
        if context.documentation:
            d = context.documentation
            add_heading("4. User & Developer Documentation", 1)

            if d.project_overview:
                add_heading("Developer Overview", 2)
                doc.add_paragraph(d.project_overview)

            if d.installation_guide:
                add_heading("Installation and Setup Guide", 2)
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.5)
                run = p.add_run(d.installation_guide)
                run.font.name = 'Courier New'
                run.font.size = Pt(9.5)

            if d.api_documentation:
                add_heading("API Endpoints & Integration Documentation", 2)
                doc.add_paragraph(d.api_documentation)

            if d.readme_md:
                add_heading("Generated README.md Markdown", 2)
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.5)
                run = p.add_run(d.readme_md)
                run.font.name = 'Courier New'
                run.font.size = Pt(9.5)

        # Save to byte stream
        stream = io.BytesIO()
        doc.save(stream)
        return stream.getvalue()

"""
docx_service.py
───────────────
Generates a full Blueprint (Requirements + Architecture + Database + Documentation)
as an IEEE-styled Word DOCX document with navy and green colored headings.
"""

import io
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from app.models.requirements import ProjectContext

# Brand Colors matching PDF
NAVY = RGBColor(26, 39, 68)   # #1A2744
GREEN = RGBColor(21, 87, 36)  # #155724


def _shade_cell(cell, hex_color: str):
    """Apply background color to a DOCX table cell."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)


def _set_cell_text_color(cell, color: RGBColor):
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            run.font.color.rgb = color


class DocxService:
    def generate_docx(self, context: ProjectContext) -> bytes:
        doc = Document()
        
        req = context.requirements
        arch = context.architecture
        db = context.database
        docs = context.documentation

        # Styles
        style_normal = doc.styles['Normal']
        style_normal.font.name = 'Times New Roman'
        style_normal.font.size = Pt(11)

        # Cover Page
        project_name = (req.project_name if req else "UNTITLED").upper()
        
        doc.add_heading('BLUEPRINT', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
        title = doc.add_paragraph(project_name)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title.runs[0].font.name = 'Times New Roman'
        title.runs[0].font.size = Pt(24)
        title.runs[0].font.bold = True
        title.runs[0].font.color.rgb = NAVY

        doc.add_paragraph('\n')
        sub = doc.add_paragraph('System Architecture & Design Document')
        sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sub.runs[0].font.size = Pt(14)
        doc.add_page_break()

        def add_ieee_heading(text: str, level: int):
            h = doc.add_heading(level=level)
            run = h.add_run(text)
            run.font.name = 'Times New Roman'
            if level == 1:
                run.font.bold = True
                run.font.size = Pt(14)
                run.font.color.rgb = NAVY
                h.alignment = WD_ALIGN_PARAGRAPH.LEFT
            elif level == 2:
                run.font.bold = True
                run.font.italic = True
                run.font.size = Pt(12)
                run.font.color.rgb = GREEN
                h.alignment = WD_ALIGN_PARAGRAPH.LEFT

        def add_table_with_header(rows_data, caption: str):
            if caption:
                cap = doc.add_paragraph(caption)
                cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                cap.runs[0].font.bold = True
                cap.runs[0].font.size = Pt(9)

            table = doc.add_table(rows=len(rows_data), cols=len(rows_data[0]))
            table.style = 'Table Grid'
            
            # Format header row
            hdr_cells = table.rows[0].cells
            for i, text in enumerate(rows_data[0]):
                hdr_cells[i].text = str(text)
                hdr_cells[i].paragraphs[0].runs[0].font.bold = True
                hdr_cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
                _shade_cell(hdr_cells[i], '1A2744')  # NAVY hex
                
            # Data rows
            for r_idx in range(1, len(rows_data)):
                row_cells = table.rows[r_idx].cells
                bg_color = 'FFFFFF' if r_idx % 2 == 1 else 'F8F9FA'
                for c_idx, text in enumerate(rows_data[r_idx]):
                    row_cells[c_idx].text = str(text)
                    _shade_cell(row_cells[c_idx], bg_color)
                    
            doc.add_paragraph()

        # I. Requirements
        if req:
            add_ieee_heading('I. SYSTEM REQUIREMENTS', 1)
            
            add_ieee_heading('A. Project Overview', 2)
            doc.add_paragraph(req.project_overview or "No overview provided.")
            
            add_ieee_heading('B. Functional Requirements', 2)
            for item in (req.functional_requirements or []):
                doc.add_paragraph(item, style='List Bullet')
                
            add_ieee_heading('C. Technology Stack', 2)
            ts = req.recommended_tech_stack
            ts_rows = [
                ["Layer", "Technology"],
                ["Frontend", ts.frontend if ts else "—"],
                ["Backend", ts.backend if ts else "—"],
                ["Database", ts.database if ts else "—"],
                ["AI Framework", ts.ai_framework if ts else "—"]
            ]
            add_table_with_header(ts_rows, "TABLE I. TECHNOLOGY STACK")
            doc.add_page_break()

        # II. Architecture
        if arch:
            add_ieee_heading('II. SYSTEM ARCHITECTURE', 1)
            
            add_ieee_heading('A. High Level Design', 2)
            doc.add_paragraph(arch.high_level_architecture or "No architecture overview.")
            
            add_ieee_heading('B. Component Breakdown', 2)
            if arch.component_breakdown:
                c_rows = [["Component", "Type", "Description"]]
                for comp in arch.component_breakdown:
                    c_rows.append([comp.name, comp.type, comp.description])
                add_table_with_header(c_rows, "TABLE II. COMPONENT BREAKDOWN")

            add_ieee_heading('C. Data Flow', 2)
            doc.add_paragraph(arch.data_flow or "Data flow not defined.")
            doc.add_page_break()

        # III. Database
        if db:
            add_ieee_heading('III. DATABASE DESIGN', 1)
            
            add_ieee_heading('A. Entity Relationship Schema', 2)
            if db.entities:
                for idx, ent in enumerate(db.entities, 1):
                    ent_rows = [["Attribute", "Definition"]]
                    for attr in ent.attributes:
                        parts = attr.split(" ", 1)
                        name = parts[0]
                        defn = parts[1] if len(parts) > 1 else "TEXT"
                        ent_rows.append([name, defn])
                    add_table_with_header(ent_rows, f"TABLE III-{idx}. ENTITY: {ent.name.upper()}")
            else:
                doc.add_paragraph("No entities defined.")
            doc.add_page_break()

        # IV. Documentation
        if docs:
            add_ieee_heading('IV. DOCUMENTATION', 1)
            
            add_ieee_heading('A. README Content', 2)
            doc.add_paragraph(docs.readme_md or "No README generated.")
            
            if docs.api_docs_md:
                add_ieee_heading('B. API Documentation', 2)
                doc.add_paragraph(docs.api_docs_md)

        buffer = io.BytesIO()
        doc.save(buffer)
        return buffer.getvalue()

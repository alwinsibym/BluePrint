"""
export_endpoint.py
──────────────────
POST /export/pdf
  Accepts a ProjectContext JSON body and returns a binary PDF stream.
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import io

from app.models.requirements import ProjectContext
from app.services.export_service import ExportService

router = APIRouter()

_export_service = ExportService()


@router.post(
    "/export/pdf",
    summary="Export project blueprint as PDF",
    description=(
        "Accepts the full ProjectContext (requirements, architecture, database, "
        "documentation) and returns a professionally-styled PDF document."
    ),
    response_class=StreamingResponse,
    tags=["export"],
)
async def export_pdf(context: ProjectContext) -> StreamingResponse:
    pdf_bytes: bytes = _export_service.generate_pdf(context)

    project_name = "blueprint"
    if context.requirements and context.requirements.project_name:
        project_name = context.requirements.project_name.lower().replace(" ", "_")

    filename = f"{project_name}_blueprint.pdf"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )

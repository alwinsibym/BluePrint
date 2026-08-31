"""
docx_endpoint.py
──────────────────
POST /export/docx
  Accepts a ProjectContext JSON body and returns a binary Word DOCX stream.
"""

from fastapi import APIRouter, Response
import io

from app.models.requirements import ProjectContext
from app.services.docx_service import DocxService

router = APIRouter()

_docx_service = DocxService()


@router.post(
    "/export/docx",
    summary="Export project blueprint as Word DOCX",
    description=(
        "Accepts the full ProjectContext (requirements, architecture, database, "
        "documentation) and returns an IEEE-styled Word document."
    ),
    response_class=Response,
    tags=["export"],
)
async def export_docx(context: ProjectContext) -> Response:
    docx_bytes: bytes = _docx_service.generate_docx(context)

    project_name = "blueprint"
    if context.requirements and context.requirements.project_name:
        project_name = context.requirements.project_name.lower().replace(" ", "_")

    filename = f"{project_name}_blueprint.docx"

    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(docx_bytes)),
        },
    )

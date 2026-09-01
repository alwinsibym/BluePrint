"""
srs_endpoint.py
───────────────
POST /export/srs
  Accepts a RequirementsResponse JSON body and returns a standalone
  IEEE Std 830-1998 compliant SRS PDF document.
"""

from fastapi import APIRouter, Response

from app.models.requirements import RequirementsResponse
from app.services.srs_service import SrsService

router = APIRouter()
_srs_service = SrsService()


@router.post(
    "/export/srs",
    summary="Export IEEE Std 830 SRS document",
    description=(
        "Accepts a RequirementsResponse and returns a standalone, "
        "fully formatted IEEE Std 830-1998 Software Requirements Specification PDF."
    ),
    response_class=Response,
    tags=["export"],
)
async def export_srs(requirements: RequirementsResponse) -> Response:
    pdf_bytes: bytes = _srs_service.generate_srs_pdf(requirements)

    project_name = "srs"
    if requirements.project_name:
        project_name = requirements.project_name.lower().replace(" ", "_")

    filename = f"{project_name}_SRS_IEEE830.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )

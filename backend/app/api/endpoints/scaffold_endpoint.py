from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.models.requirements import ProjectContext
from app.models.scaffold import ScaffoldResponse
from app.services.scaffold_service import ScaffoldService
from app.services.zip_service import ZipService

router = APIRouter()

_service = ScaffoldService()

@router.post(
    "/agents/scaffold",
    response_model=ScaffoldResponse,
    summary="Generate project skeleton from accumulated ProjectContext",
    description=(
        "Accepts the full accumulated ProjectContext (Requirements + Architecture + "
        "Database + Documentation) and runs the deterministic Project Generator to "
        "assemble a complete, development-ready project foundation. No LLM calls are "
        "made during generation – all files are produced from templates."
    ),
    tags=["agents"],
)
async def create_scaffold(context: ProjectContext) -> ScaffoldResponse:
    return await _service.generate_scaffold(context)


@router.post(
    "/agents/scaffold/export-zip",
    summary="Export ScaffoldResponse as a downloadable ZIP archive",
    description="Accepts a ScaffoldResponse object and returns a compressed .zip file download stream.",
    tags=["agents"],
)
async def export_scaffold_zip(scaffold: ScaffoldResponse) -> StreamingResponse:
    zip_buffer = ZipService.create_zip_archive(scaffold)
    project_name = scaffold.project_name or "blueprint-project"
    
    # Sanitize project name for safe filename header
    safe_filename = "".join(c for c in project_name if c.isalnum() or c in ("-", "_")).strip() or "blueprint-project"

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename}.zip"'
        },
    )

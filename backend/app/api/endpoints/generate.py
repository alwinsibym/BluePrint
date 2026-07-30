from fastapi import APIRouter
from app.schemas.project import GenerateRequest, GenerateResponse, ProjectMock

router = APIRouter()

@router.post("/generate", response_model=GenerateResponse)
async def generate_project(payload: GenerateRequest):
    # Retrieve the user input and return it in the mock response as requested
    return GenerateResponse(
        status="success",
        message="Blueprint backend is connected successfully.",
        project=ProjectMock(
            name=payload.name if payload.name else "Sample Project",
            description=payload.description if payload.description else "This is mock data."
        )
    )

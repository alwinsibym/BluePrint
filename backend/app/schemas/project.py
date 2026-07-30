from pydantic import BaseModel

class GenerateRequest(BaseModel):
    name: str
    description: str
    tech_stack: str

class ProjectMock(BaseModel):
    name: str
    description: str

class GenerateResponse(BaseModel):
    status: str
    message: str
    project: ProjectMock

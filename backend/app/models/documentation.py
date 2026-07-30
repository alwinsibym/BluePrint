from pydantic import BaseModel, Field

class DocumentationResponse(BaseModel):
    project_overview: str = Field(..., description="High-level summary of objectives, purpose, and scope")
    readme_md: str = Field(..., description="Complete production-ready GitHub README.md text")
    installation_guide: str = Field(..., description="Step-by-step setup instructions for dev, prerequisites, backend, frontend, and Ollama")
    api_documentation: str = Field(..., description="Detailed documentation for API endpoints, request, and response formats")
    folder_structure_description: str = Field(..., description="Explanation of every folder and module in the project structure")
    deployment_notes: str = Field(..., description="Development vs Production notes, env variables, Ollama setup, SQLite, and Docker hints")
    developer_notes: str = Field(..., description="Assumptions, limitations, extension points, and coding conventions")

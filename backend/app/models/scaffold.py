from pydantic import BaseModel, Field
from typing import List

class ScaffoldFile(BaseModel):
    path: str = Field(..., description="Relative file path, e.g. 'backend/app/main.py'")
    content: str = Field(..., description="Text content of the file")
    language: str = Field(..., description="Language for syntax highlighting, e.g. 'python', 'typescript', 'sql', 'json', 'markdown'")
    generated_by: str = Field(..., description="Agent or module that contributed this file, e.g. 'ScaffoldAgent (Template Engine)'")

class ScaffoldResponse(BaseModel):
    project_name: str = Field(..., description="Normalized project name")
    tree_view: str = Field(..., description="ASCII representation of the generated project directory tree")
    files: List[ScaffoldFile] = Field(..., description="List of all scaffolded files")
    total_files: int = Field(..., description="Total count of files generated")
    generation_summary: str = Field(..., description="Overview summary of assembled project foundation")

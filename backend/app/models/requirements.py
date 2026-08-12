from pydantic import BaseModel, Field
from typing import List, Dict

class UserStory(BaseModel):
    role: str = Field(default="User", description="The role of the user")
    desire: str = Field(default="interact with system", description="What the user wants to achieve")
    benefit: str = Field(default="accomplish task", description="Why it matters")

class RecommendedTechStack(BaseModel):
    frontend: str = Field(default="React / TypeScript", description="Frontend framework or library")
    backend: str = Field(default="FastAPI / Python", description="Backend language/framework")
    database: str = Field(default="PostgreSQL", description="Database technology")
    ai_framework: str = Field(default="Ollama", description="AI/LLM framework used, e.g., Ollama")

class RequirementsResponse(BaseModel):
    project_name: str = Field(..., description="Project name")
    project_overview: str = Field(..., description="Project overview")
    objectives: List[str] = Field(default_factory=list)
    functional_requirements: List[str] = Field(default_factory=list)
    non_functional_requirements: List[str] = Field(default_factory=list)
    user_roles: List[str] = Field(default_factory=list)
    user_stories: List[UserStory] = Field(default_factory=list)
    suggested_modules: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    recommended_tech_stack: RecommendedTechStack = Field(default_factory=RecommendedTechStack)
    future_scope: List[str] = Field(default_factory=list)

class RequirementsRequest(BaseModel):
    idea: str = Field(..., description="Natural‑language description of the software project idea")

# Import ArchitectureResponse inside the module if possible, or at the top.
# To avoid circular imports if any, we'll import it here.
from typing import Optional, Dict
from app.models.architecture import ArchitectureResponse
from app.models.database import DatabaseResponse
from app.models.documentation import DocumentationResponse
from app.models.scaffold import ScaffoldResponse

class ProjectContext(BaseModel):
    """Aggregates planning artifacts produced by sequential agents.
    Each field is optional because agents will progressively enrich the context.
    """
    requirements: RequirementsResponse | None = None
    architecture: ArchitectureResponse | None = None
    database: DatabaseResponse | None = None
    documentation: DocumentationResponse | None = None
    scaffold: ScaffoldResponse | None = None

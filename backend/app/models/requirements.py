from pydantic import BaseModel, Field
from typing import List, Dict

class UserStory(BaseModel):
    role: str = Field(..., description="The role of the user")
    desire: str = Field(..., description="What the user wants to achieve")
    benefit: str = Field(..., description="Why it matters")

class RecommendedTechStack(BaseModel):
    frontend: str = Field(..., description="Frontend framework or library")
    backend: str = Field(..., description="Backend language/framework")
    database: str = Field(..., description="Database technology")
    ai_framework: str = Field(..., description="AI/LLM framework used, e.g., Ollama")

class RequirementsResponse(BaseModel):
    project_name: str
    project_overview: str
    objectives: List[str]
    functional_requirements: List[str]
    non_functional_requirements: List[str]
    user_roles: List[str]
    user_stories: List[UserStory]
    suggested_modules: List[str]
    assumptions: List[str]
    constraints: List[str]
    recommended_tech_stack: RecommendedTechStack
    future_scope: List[str]

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

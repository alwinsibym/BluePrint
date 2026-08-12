from pydantic import BaseModel, Field
from typing import List

class ArchitectureComponent(BaseModel):
    name: str = Field(default="Component", description="Name of the component or module")
    description: str = Field(default="", description="What this component does")
    dependencies: List[str] = Field(default_factory=list, description="Other components this depends on")

class ArchitectureResponse(BaseModel):
    high_level_architecture: str = Field(default="Modular system architecture", description="Description of the overall system architecture")
    folder_structure: List[str] = Field(default_factory=list, description="Recommended folder paths")
    component_breakdown: List[ArchitectureComponent] = Field(default_factory=list, description="List of major components")
    data_flow: str = Field(default="Data flows from client UI via REST API to backend application layer and database.", description="Description of how data moves through the system")

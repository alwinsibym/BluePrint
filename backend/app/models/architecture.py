from pydantic import BaseModel, Field
from typing import List

class ArchitectureComponent(BaseModel):
    name: str = Field(..., description="Name of the component or module")
    description: str = Field(..., description="What this component does")
    dependencies: List[str] = Field(..., description="Other components this depends on")

class ArchitectureResponse(BaseModel):
    high_level_architecture: str = Field(..., description="Description of the overall system architecture")
    folder_structure: List[str] = Field(..., description="Recommended folder paths")
    component_breakdown: List[ArchitectureComponent] = Field(..., description="List of major components")
    data_flow: str = Field(..., description="Description of how data moves through the system")

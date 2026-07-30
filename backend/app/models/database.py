from pydantic import BaseModel, Field
from typing import List

class Entity(BaseModel):
    name: str = Field(..., description="Name of the database entity/table")
    description: str = Field(..., description="Description of the entity's purpose")
    attributes: List[str] = Field(..., description="List of attributes/columns with data types")
    primary_key: str = Field(..., description="Primary key attribute(s)")
    foreign_keys: List[str] = Field(default_factory=list, description="Foreign keys and references")

class DatabaseResponse(BaseModel):
    database_overview: str = Field(..., description="High-level overview of the database design")
    entities: List[Entity] = Field(..., description="List of database entities")
    relationships: List[str] = Field(..., description="Entity relationships (e.g., User 1:N Orders)")
    normalization_notes: str = Field(..., description="Notes on normalization level and decisions")
    table_summary: str = Field(..., description="Summary of tables created")
    sql_schema: str = Field(..., description="ANSI/SQLite-compliant SQL DDL statements")
    mermaid_er_diagram: str = Field(..., description="Raw Mermaid ER diagram string")

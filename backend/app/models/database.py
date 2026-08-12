from pydantic import BaseModel, Field
from typing import List

class Entity(BaseModel):
    name: str = Field(default="Entity", description="Name of the database entity/table")
    description: str = Field(default="", description="Description of the entity's purpose")
    attributes: List[str] = Field(default_factory=list, description="List of attributes/columns with data types")
    primary_key: str = Field(default="id", description="Primary key attribute(s)")
    foreign_keys: List[str] = Field(default_factory=list, description="Foreign keys and references")

class DatabaseResponse(BaseModel):
    database_overview: str = Field(default="Relational database schema designed for data integrity.", description="High-level overview of the database design")
    entities: List[Entity] = Field(default_factory=list, description="List of database entities")
    relationships: List[str] = Field(default_factory=list, description="Entity relationships (e.g., User 1:N Orders)")
    normalization_notes: str = Field(default="3NF normalization applied.", description="Notes on normalization level and decisions")
    table_summary: str = Field(default="", description="Summary of tables created")
    sql_schema: str = Field(default="", description="ANSI/SQLite-compliant SQL DDL statements")
    mermaid_er_diagram: str = Field(default="", description="Raw Mermaid ER diagram string")

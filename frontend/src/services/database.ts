import api from "./api";
import { RequirementsResponse } from "./requirements";
import { ArchitectureResponse } from "./architecture";

export interface Entity {
  name: string;
  description: string;
  attributes: string[];
  primary_key: string;
  foreign_keys: string[];
}

export interface DatabaseResponse {
  database_overview: string;
  entities: Entity[];
  relationships: string[];
  normalization_notes: string;
  table_summary: string;
  sql_schema: string;
  mermaid_er_diagram: string;
}

export interface ProjectContextInput {
  requirements?: RequirementsResponse | null;
  architecture?: ArchitectureResponse | null;
  database?: DatabaseResponse | null;
  documentation?: import("./documentation").DocumentationResponse | null;
}

export const generateDatabase = async (context: ProjectContextInput): Promise<DatabaseResponse> => {
  const response = await api.post<DatabaseResponse>("/agents/database", context);
  return response.data;
};

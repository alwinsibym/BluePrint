import api from "./api";
import { ProjectContextInput } from "./database";

export interface DocumentationResponse {
  project_overview: string;
  readme_md: string;
  installation_guide: string;
  api_documentation: string;
  folder_structure_description: string;
  deployment_notes: string;
  developer_notes: string;
}

export const generateDocumentation = async (context: ProjectContextInput): Promise<DocumentationResponse> => {
  const response = await api.post<DocumentationResponse>("/agents/documentation", context);
  return response.data;
};

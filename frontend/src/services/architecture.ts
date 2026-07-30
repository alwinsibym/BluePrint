import api from "./api";
import { RequirementsResponse } from "./requirements";

export interface ArchitectureComponent {
  name: string;
  description: string;
  dependencies: string[];
}

export interface ArchitectureResponse {
  high_level_architecture: string;
  folder_structure: string[];
  component_breakdown: ArchitectureComponent[];
  data_flow: string;
}

export const generateArchitecture = async (requirements: RequirementsResponse): Promise<ArchitectureResponse> => {
  const response = await api.post<ArchitectureResponse>("/agents/architecture", requirements);
  return response.data;
};

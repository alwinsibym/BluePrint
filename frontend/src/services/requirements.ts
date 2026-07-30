import api from "./api";

// TypeScript types mirroring backend Pydantic models

export interface UserStory {
  role: string;
  desire: string;
  benefit: string;
}

export interface RecommendedTechStack {
  frontend: string;
  backend: string;
  database: string;
  ai_framework: string;
}

export interface RequirementsResponse {
  project_name: string;
  project_overview: string;
  objectives: string[];
  functional_requirements: string[];
  non_functional_requirements: string[];
  user_roles: string[];
  user_stories: UserStory[];
  suggested_modules: string[];
  assumptions: string[];
  constraints: string[];
  recommended_tech_stack: RecommendedTechStack;
  future_scope: string[];
}

/**
 * Calls the Requirements Agent endpoint to generate structured planning output.
 * @param idea Natural-language description of the software project idea.
 */
export const createRequirements = async (
  idea: string
): Promise<RequirementsResponse> => {
  const response = await api.post<RequirementsResponse>(
    "/agents/requirements",
    { idea }
  );
  return response.data;
};

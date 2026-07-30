import axios from "axios";

const getBaseURL = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  if (typeof window !== "undefined" && window.location.hostname) {
    return `http://${window.location.hostname}:8000`;
  }
  return "http://localhost:8000";
};

// Create the Axios instance pointing to the FastAPI backend.
const api = axios.create({
  baseURL: getBaseURL(),
  // 10-minute timeout — qwen3:8b can take 2-5 minutes for large prompts.
  // Without this, the browser default (~30s) cuts off before the model finishes.
  timeout: 600_000,
  headers: {
    "Content-Type": "application/json",
  },
});

// TypeScript interfaces for request inputs and response payloads
export interface GenerateParams {
  name: string;
  description: string;
  tech_stack: string;
}

export interface ProjectMock {
  name: string;
  description: string;
}

export interface GenerateResponse {
  status: string;
  message: string;
  project: ProjectMock;
}

/**
 * Triggers the project generation endpoint on the backend.
 * @param params Project Name, Description, and Tech Stack.
 */
export const generateBlueprint = async (params: GenerateParams): Promise<GenerateResponse> => {
  const response = await api.post<GenerateResponse>("/generate", params);
  return response.data;
};

export default api;

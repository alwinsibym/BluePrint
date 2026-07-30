import api from "@/services/api";
import { ProjectContextInput } from "@/services/database";

// ─── Response types ──────────────────────────────────────────────────────────

export interface ScaffoldFile {
  path: string;
  content: string;
  language: string;
  generated_by: string;
}

export interface ScaffoldResponse {
  project_name: string;
  tree_view: string;
  files: ScaffoldFile[];
  total_files: number;
  generation_summary: string;
}

// ─── API calls ────────────────────────────────────────────────────────────────

export const generateScaffold = async (
  context: ProjectContextInput
): Promise<ScaffoldResponse> => {
  const response = await api.post<ScaffoldResponse>("/agents/scaffold", context);
  return response.data;
};

export const downloadScaffoldZip = async (
  scaffold: ScaffoldResponse
): Promise<void> => {
  const response = await api.post("/agents/scaffold/export-zip", scaffold, {
    responseType: "blob",
  });

  // Extract filename from header if present, or format from project_name
  const safeName =
    scaffold.project_name.toLowerCase().replace(/[^a-z0-9_-]/g, "-") || "blueprint-project";
  const filename = `${safeName}.zip`;

  // Create temporary URL & download link trigger
  const blob = new Blob([response.data], { type: "application/zip" });
  const downloadUrl = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = downloadUrl;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(downloadUrl);
};

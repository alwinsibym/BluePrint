import api from "./api";
import { ProjectContextInput } from "./database";

/**
 * Calls POST /export/pdf with the current ProjectContext.
 * Returns a Blob (PDF binary) that can be downloaded in the browser.
 */
export const exportBlueprintPdf = async (
  context: ProjectContextInput
): Promise<Blob> => {
  const response = await api.post("/export/pdf", context, {
    responseType: "blob",
  });
  return response.data as Blob;
};

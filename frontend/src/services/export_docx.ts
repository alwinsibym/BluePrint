import api from "./api";
import { ProjectContextInput } from "./database";

/**
 * Calls POST /export/docx with the current ProjectContext.
 * Returns a Blob (Word DOCX binary) that can be downloaded in the browser.
 */
export const exportBlueprintDocx = async (
  context: ProjectContextInput
): Promise<Blob> => {
  const response = await api.post("/export/docx", context, {
    responseType: "blob",
  });
  return response.data as Blob;
};

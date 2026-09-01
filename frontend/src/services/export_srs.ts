import api from "./api";
import { RequirementsResponse } from "./requirements";

/**
 * Calls POST /export/srs with a RequirementsResponse body.
 * Returns a Blob containing the IEEE Std 830-1998 SRS PDF document.
 */
export const exportSrsPdf = async (
  requirements: RequirementsResponse
): Promise<Blob> => {
  const response = await api.post("/export/srs", requirements, {
    responseType: "blob",
  });
  return response.data as Blob;
};

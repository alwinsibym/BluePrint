import api from "./api";

/**
 * Sends a short prompt to the backend /test-llm endpoint to verify Ollama connectivity.
 * Uses the shared `api` instance so it routes to the correct backend host:port.
 * @param prompt The text prompt to send.
 * @returns Axios response containing `{ response: string }`
 */
export const testLLM = async (prompt: string) =>
  api.post("/test-llm", { prompt });

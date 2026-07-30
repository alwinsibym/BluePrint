import axios from "axios";

/**
 * Sends a prompt to the backend test‑LLM endpoint.
 * @param prompt The text prompt to send.
 * @returns Axios response containing `{ response: string }`
 */
export const testLLM = async (prompt: string) =>
  axios.post("/test-llm", { prompt });

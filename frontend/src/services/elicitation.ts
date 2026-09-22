/**
 * elicitation.ts
 * ──────────────
 * Frontend API service for the Interactive Requirements Elicitation Engine.
 */
import api from "./api";

export interface ElicitationMessage {
  role: "assistant" | "user";
  content: string;
  phase: number;
}

export interface ElicitationResponse {
  question: string;
  phase: number;
  phase_label: string;
  phase_description: string;
  progress_pct: number;
  history: ElicitationMessage[];
  is_complete: boolean;
  requirements?: import("./requirements").RequirementsResponse;
}

/** Start a new elicitation interview with the project idea. */
export const startElicitation = async (idea: string): Promise<ElicitationResponse> => {
  const { data } = await api.post<ElicitationResponse>("/elicit/start", { idea });
  return data;
};

/** Send the developer's answer and receive the next question (or final requirements). */
export const sendElicitationAnswer = async (
  idea: string,
  user_answer: string,
  history: ElicitationMessage[]
): Promise<ElicitationResponse> => {
  const { data } = await api.post<ElicitationResponse>("/elicit/chat", {
    idea,
    user_answer,
    history,
  });
  return data;
};

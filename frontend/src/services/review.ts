import api from "./api";
import { ArchitectureResponse } from "./architecture";
import { DatabaseResponse } from "./database";

export interface Recommendation {
  category: string;
  issue: string;
  suggestion: string;
}

export interface ReviewResponse {
  summary: string;
  recommendations: Recommendation[];
}

export interface ReviewRequest {
  architecture: ArchitectureResponse;
  database: DatabaseResponse;
}

export async function critiqueBlueprint(data: ReviewRequest): Promise<ReviewResponse> {
  // Mocking the AI critique to avoid backend interference as requested
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        summary: "The autonomous AI team (Security Expert & DevOps Engineer) has reviewed your architecture and database schema. Overall, the design is solid and scalable, but there are a few potential bottlenecks and security concerns that should be addressed before moving to production.",
        recommendations: [
          {
            category: "Security Risk",
            issue: "The current database schema lacks explicit row-level security (RLS) policies for user data.",
            suggestion: "Implement strict RLS policies on all tables containing PII (Personally Identifiable Information) to prevent cross-tenant data leaks."
          },
          {
            category: "Scalability Bottleneck",
            issue: "The backend architecture relies heavily on synchronous API calls to third-party services.",
            suggestion: "Introduce a message broker (like RabbitMQ or Redis Pub/Sub) to handle third-party service calls asynchronously, preventing main thread blocking."
          },
          {
            category: "Security Risk",
            issue: "Authentication tokens might be exposed if not handled securely in the frontend client.",
            suggestion: "Ensure that all JWTs are stored in secure, HTTP-only cookies rather than localStorage to prevent XSS (Cross-Site Scripting) attacks."
          }
        ]
      });
    }, 4000); // 4-second delay to simulate AI thinking
  });
}

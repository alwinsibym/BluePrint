export type AgentStatus = "waiting" | "running" | "completed";

export interface Agent {
  id: string;
  name: string;
  description: string;
  status: AgentStatus;
  progress: number;
}

export const initialAgents: Agent[] = [
  {
    id: "requirements",
    name: "Requirements Analyst",
    description: "Extracts functional & non-functional requirements",
    status: "waiting",
    progress: 0,
  },
  {
    id: "architect",
    name: "Software Architect",
    description: "Designs services, patterns, and tech decisions",
    status: "waiting",
    progress: 0,
  },
  {
    id: "database",
    name: "Database Designer",
    description: "Builds schemas, relations, and migrations",
    status: "waiting",
    progress: 0,
  },
  {
    id: "docs",
    name: "Documentation Agent",
    description: "Writes README and technical documentation",
    status: "waiting",
    progress: 0,
  },
  {
    id: "scaffold",
    name: "Project Scaffold Agent",
    description: "Generates a starter repository",
    status: "waiting",
    progress: 0,
  },
];

export const sampleRequirements = `# Functional Requirements

1. Users can create and manage projects.
2. Projects have members, roles, and permissions.
3. Support for OAuth (Google, GitHub) authentication.
4. Real-time collaboration on planning documents.
5. Export generated artifacts as a ZIP archive.

# Non-Functional Requirements

- Response time under 200ms for read APIs.
- 99.9% availability across primary regions.
- End-to-end encryption for user data at rest.
- Horizontal scalability for planning workers.
`;

export const sampleArchitecture = `# System Architecture

- Frontend: React + TypeScript (Vite), TanStack Router
- Backend: FastAPI (Python 3.12), async workers
- Datastore: PostgreSQL 16 (primary), Redis (cache/queue)
- AI Layer: Local LLM runtime via Ollama, orchestrated by an
  agent supervisor pattern.

## Services

- api-gateway  — routes external traffic, handles auth
- planner      — orchestrates the multi-agent pipeline
- artifacts    — stores generated files and diagrams
- notifier     — websocket updates to the dashboard
`;

export const sampleDatabase = `-- Core tables
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  tech_stack TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE artifacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  kind TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);`;

export const sampleErDiagram = `erDiagram
  USERS ||--o{ PROJECTS : owns
  PROJECTS ||--o{ ARTIFACTS : produces
  USERS {
    uuid id
    text email
    text name
  }
  PROJECTS {
    uuid id
    uuid owner_id
    text name
    text tech_stack
  }
  ARTIFACTS {
    uuid id
    uuid project_id
    text kind
    text content
  }`;

export const sampleDocumentation = `# Project Overview

This project is scaffolded by Blueprint. It includes a React + TypeScript
frontend and a FastAPI backend, wired together via a shared OpenAPI schema.

## Getting Started

\`\`\`bash
git clone <repo>
cd project
pnpm install
pnpm dev
\`\`\`

## Deployment

Use the included Docker Compose file to run the stack locally, or deploy
each service independently to your preferred cloud.
`;

export const sampleStructure = `my-project/
├── frontend/
│   ├── src/
│   │   ├── routes/
│   │   ├── components/
│   │   └── lib/
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   └── services/
│   └── pyproject.toml
├── database/
│   └── migrations/
├── docker-compose.yml
└── README.md`;

export const generatedFiles = [
  { name: "README.md", size: "3.2 KB", kind: "doc" },
  { name: "requirements.md", size: "1.8 KB", kind: "doc" },
  { name: "architecture.md", size: "2.4 KB", kind: "doc" },
  { name: "database.sql", size: "4.7 KB", kind: "sql" },
  { name: "er-diagram.mmd", size: "0.9 KB", kind: "diagram" },
  { name: "frontend/", size: "42 files", kind: "folder" },
  { name: "backend/", size: "28 files", kind: "folder" },
] as const;

# Blueprint

> AI-Assisted Software Planning Platform

Blueprint is an AI-powered software planning platform that transforms software ideas into structured, development-ready project foundations.

Instead of generating complete applications, Blueprint focuses on the **planning phase of the Software Development Life Cycle (SDLC)** by producing requirements, architecture, database design, documentation, and project scaffolds using multiple specialized AI agents running on local Large Language Models (LLMs).

---

## Overview

Blueprint helps developers convert a simple project idea into organized planning artifacts before development begins.

The platform follows a modular multi-agent architecture where each AI agent is responsible for a specific planning task. Every generated artifact becomes the input for the next agent, resulting in a complete and consistent project foundation.

The entire AI workflow runs locally using **Ollama**, providing privacy, offline capability, and lower operational costs.

---

## Features

- AI-assisted software planning
- Multi-Agent architecture
- Local LLM integration (Ollama)
- Automatic requirement analysis
- Software architecture generation
- Database design generation
- SQL schema generation
- Mermaid ER diagram generation
- Documentation generation
- README generation
- Project scaffold generation
- Interactive dashboard
- Modular and extensible architecture
- Offline AI execution
- Export-ready project artifacts

---

## Project Workflow

```
Software Idea
      │
      ▼
Requirements Agent
      │
      ▼
Architecture Agent
      │
      ▼
Database Agent
      │
      ▼
Documentation Agent
      │
      ▼
Scaffold Agent
      │
      ▼
Template Engine
      │
      ▼
Generated Project Foundation
```

---

## Project Architecture

```
Frontend (React)
        │
        ▼
FastAPI Backend
        │
        ▼
Agent Layer
        │
        ▼
Service Layer
        │
        ▼
Ollama (Local LLM)
```

---

# AI Agents

## Requirements Agent

Generates:

- Project Overview
- Objectives
- Functional Requirements
- Non-functional Requirements
- User Stories
- Suggested Modules
- Assumptions
- Constraints
- Recommended Technology Stack

---

## Architecture Agent

Generates:

- System Architecture
- Folder Structure
- Layered Design
- Module Responsibilities
- API Design
- Technology Recommendations

---

## Database Agent

Generates:

- Database Entities
- Relationships
- SQL Schema
- Mermaid ER Diagram

---

## Documentation Agent

Generates:

- Project Overview
- README.md
- Installation Guide
- API Documentation Summary

---

## Scaffold Agent

Generates:

- Development-ready project structure
- Starter React project
- Starter FastAPI project
- Configuration files
- Documentation files
- SQL schema
- Template-based project foundation

---

## Technology Stack

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- Axios

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy

### AI

- CrewAI
- Ollama
- Qwen

### Database

- SQLite

### Templates

- Jinja2

### Development Tools

- Git
- VS Code
- Postman

---

## Current Progress

### ✅ Phase 1 — Project Setup

- React frontend
- FastAPI backend
- Project structure
- API communication

### ✅ Phase 2 — Local LLM Integration

- Ollama integration
- LLM communication service
- Prompt testing

### ✅ Phase 3 — Requirements Agent

- Requirement generation
- Structured JSON output
- Interactive frontend

### 🚧 Phase 4 — Architecture Agent

In Progress

### 📅 Upcoming

- Database Agent
- Documentation Agent
- Scaffold Agent
- ZIP Export
- Optional Features

---

## Folder Structure

```
Blueprint/

├── frontend/
├── backend/
│   ├── agents/
│   ├── services/
│   ├── api/
│   ├── models/
│   ├── prompts/
│   ├── templates/
│   └── generated_projects/
├── docs/
├── README.md
├── roadmap.md
└── project.md
```

---

## Why Local LLM?

Blueprint uses locally hosted language models instead of cloud APIs.

Advantages include:

- Privacy
- Offline support
- No API costs
- Faster experimentation
- Full control over models
- Easy customization

---

## Future Roadmap

- GitHub Repository Integration
- Git Initialization
- ZIP Project Export
- PDF Documentation Export
- DOCX Export
- Docker Template Support
- Multiple Framework Support
- Authentication Module
- CI/CD Template Generation
- Project Cost Estimation
- Timeline Estimation
- Multi-language Support

---

## Project Status

**Active Development**

Current milestone:
**Phase 4 — Architecture Agent**

---

## License

This project is developed as part of an **MCA Mini Project** for academic purposes.

---

## Author

**Alwin Siby**

Master of Computer Applications (MCA)

Mar Augusthinose College, Ramapuram

---

## Acknowledgements

- Ollama
- CrewAI
- FastAPI
- React
- Vite
- Tailwind CSS
- SQLite
- Jinja2

---

> **Blueprint** aims to bridge the gap between software ideation and implementation by providing AI-assisted planning artifacts that help developers start projects with a structured, consistent, and development-ready foundation.

# Blueprint

**Tagline:** From Idea to Project Foundation

## Project Overview

Blueprint is a multi-agent software planning platform that transforms software ideas into development-ready project foundations. Using CrewAI and locally hosted language models through Ollama, the platform automates the initial stages of the Software Development Life Cycle (SDLC) by generating project requirements, software architecture, database design, documentation, and a starter project scaffold.

Blueprint is designed to assist developers during project planning rather than replace software developers.

---

# Problem Statement

Software projects require significant planning before development begins. Preparing software requirements, architecture, database design, documentation, and project setup is repetitive and time-consuming.

Blueprint automates these initial planning activities, allowing developers and students to begin implementation with a structured project foundation.

---

# Objectives

- Generate Software Requirement Specification (SRS)
- Generate Functional Requirements
- Generate Non-functional Requirements
- Generate User Stories
- Suggest Project Modules
- Generate High-Level Software Architecture
- Generate Database Schema
- Generate Mermaid ER Diagram
- Generate README Documentation
- Generate Starter React + FastAPI Project Structure
- Export Generated Project as ZIP

---

# Project Scope

## Included

- AI-assisted software planning
- Multi-agent workflow using CrewAI
- Local LLM execution through Ollama
- Requirements generation
- Architecture generation
- Database schema generation
- Mermaid ER Diagram generation
- README generation
- Starter project scaffold
- ZIP export

## Not Included

- Complete production-ready software generation
- Automatic debugging
- Automatic deployment
- CI/CD pipeline generation
- Full testing automation
- Cloud-based AI APIs

---

# Core AI Agents

## 1. Requirements Agent

Responsible for:
- Project Objective
- Functional Requirements
- Non-functional Requirements
- User Stories
- Suggested Modules

---

## 2. Architecture Agent

Responsible for:
- High-Level Architecture
- Folder Structure
- Recommended Tech Stack
- Component Breakdown

---

## 3. Database Agent

Responsible for:
- Entities
- Relationships
- SQL Schema
- ER Diagram (Mermaid)

---

## 4. Documentation Agent

Responsible for:
- README.md
- Installation Guide
- Project Overview

---

## 5. Scaffold Agent

Responsible for:
- React Starter Project
- FastAPI Starter Project
- Folder Structure
- Configuration Files

This agent should use predefined templates instead of generating complete applications from scratch.

---

# System Workflow

User

↓

Project Description

↓

Requirements Agent

↓

Architecture Agent

↓

Database Agent

↓

Documentation Agent

↓

Scaffold Agent

↓

Generated Project

↓

ZIP Download

---

# Technology Stack

Frontend
- React
- Vite
- Tailwind CSS

Backend
- FastAPI
- Python

AI
- CrewAI
- Ollama
- Qwen Coder
- Qwen Instruct

Database
- SQLite

Documentation
- Markdown
- Mermaid

Version Control
- Git

---

# Development Rules

- Build incrementally.
- Do not modify the frontend unless necessary.
- Keep the architecture modular.
- Use local LLMs only.
- Use template-based scaffolding instead of full application generation.
- Explain all significant code changes.
- Avoid unnecessary dependencies.
- Keep the UI clean and professional.

---

# Future Scope

- GitHub Repository Creation
- Git Push
- PDF Export
- DOCX Export
- Docker Support
- Additional UML Diagrams
- More Project Templates

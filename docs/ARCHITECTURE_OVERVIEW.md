# Architecture Overview

Quintessence is a local-first full-stack web application.

The architecture is intentionally simple, maintainable, and personal-first.

## System Context

Single User
-> React / TypeScript / Vite Frontend
-> FastAPI Backend
-> SQLite Database
-> Local File Storage
-> Backup and Export Folders

## Frontend

The frontend is built with React, TypeScript, Vite, Tailwind CSS, and Lucide React icons.

## Backend

The backend is built with FastAPI, SQLAlchemy, SQLite, and Pydantic.

## Core Backend Responsibilities

- authentication
- CRUD endpoints
- database persistence
- evidence file upload handling
- evidence scoring
- draft resume bullet generation
- STAR story draft generation
- weekly review generation
- activity timeline
- backup and export endpoints
- local settings endpoints

## Database

Core tables include:

- projects
- tasks
- opportunities
- capabilities
- capability_history
- fgas
- evidence_items
- ai_items
- notes
- decisions
- weekly_review_snapshots
- activity_logs
- settings

## Evidence Engine

Evidence can be linked manually to capabilities, projects, tasks, FGAs, and opportunities.

Evidence records include summary, tags, local file path, evidence score, completeness notes, resume bullet draft, interview story draft, and STAR story draft.

## Local Storage

Uploaded files are stored locally under backend/storage.

SQLite data is stored locally under backend/data.

Backups and exports are stored locally under backend/backups and backend/exports.

These folders are excluded from Git tracking to protect private data.

## Security Model

Quintessence uses a simple local single-user authentication model.

The application is not designed as a multi-user SaaS platform.

## Architectural Intent

The architecture prioritises maintainability, local ownership, low operational complexity, clear module boundaries, evidence traceability, and personal workflow usefulness.

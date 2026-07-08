# 02 Product Requirements Document

## Functional requirements

- Single-user authentication.
- Dashboard with active projects, FGAs, opportunities, evidence, recent decisions, and weekly review.
- Project management with tasks, statuses, milestones, documents, and decision logs.
- Career pipeline with opportunities and fit scores.
- Capability Atlas with scores and growth notes.
- FGA management with target capability, outcome, evidence, portfolio value, and reflection.
- Evidence Repository with metadata, local file uploads, manual links, generated resume bullet drafts, and interview story drafts.
- AI Workspace for prompts, workflow designs, experiments, and model comparisons.
- Knowledge Vault for notes, research, tags, and document-like content.
- Decision Register with rationale, consequences, and review dates.
- Weekly Review endpoint.

## Non-functional requirements

- Runs locally with SQLite.
- Docker-compatible.
- Clear folder structure.
- Low-maintenance UX.
- No required external AI provider.
- File uploads stored locally under backend/storage.
- API documented through FastAPI OpenAPI.

## User stories

- As the user, I want a Mission Control dashboard so I can immediately see what needs attention.
- As the user, I want to link evidence to capabilities so my growth is visible.
- As the user, I want application fit fields so I can evaluate career opportunities objectively.
- As the user, I want generated draft resume bullets and interview stories so evidence becomes reusable.
- As the user, I want decisions logged with rationale so I do not re-solve the same problems repeatedly.

## Acceptance criteria

- The app launches with seed data.
- The user can log in with the configured local account.
- The user can create, read, update, and delete core records.
- Evidence can be uploaded and linked manually.
- Weekly review returns completed work, blockers, evidence, and next actions.
- Docker Compose starts backend and frontend.

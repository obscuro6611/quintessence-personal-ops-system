# 06 Development Plan

## Phase 1 — Runnable MVP

- Docs.
- Single-user auth.
- CRUD APIs.
- Dashboard.
- Evidence upload and linking.
- Weekly Review.
- Docker.

## Phase 2 — Deeper workflows

- Rich kanban board.
- More link editing in UI.
- Better search and filters.
- Resume/interview story refinement.
- Capability growth charts.

## Phase 3 — AI provider layer

- Optional provider abstraction.
- Local Ollama support.
- Prompt execution history.
- Evidence summarization.

## Milestones

1. Architecture and schema locked.
2. Backend CRUD complete.
3. Frontend module shell complete.
4. Evidence engine complete.
5. Docker package complete.

## Risks

- Scope creep: keep Phase 1 focused.
- Evidence model complexity: use manual linking first.
- UI overload: prioritize clarity over density.

## Testing strategy

- Pytest for health, auth, and core API flows.
- Vitest-ready frontend structure.
- Manual Docker smoke test.

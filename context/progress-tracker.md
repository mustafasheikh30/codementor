# Progress Tracker

Update this file after every meaningful implementation
change.

## Current Phase

- End-to-end readiness check (no new feature work).

## Current Goal

- Verify startup, DB connectivity, Docker permissions safely, sandbox isolation constraints, main flows, and all checks.

## Completed

- Initial project structure established.
- FastAPI backend configured.
- PostgreSQL database integration established.
- Codeforces problem metadata models and API routes implemented.
- Problem discovery supports filtering, sorting, and pagination.
- Codeforces problem ingestion implemented.
- Angular frontend scaffold established.
- Sample problem data and automated tests included in the project.
- Codeforces OIDC login and callback implemented with state/nonce signing.
- OIDC configuration, safe return-path validation, and error handling implemented.
- Authentication test suite passes (14 tests) without requiring a database.
- Persistent local user accounts linked to verified Codeforces identities added (SQLModel `User`, upsert/lookup service).
- Session-based authentication endpoints added (`GET /api/auth/me`, `POST /api/auth/logout`); app sessions use `codementor_session` (14 days).
- Users migration (`0002_create_users_table`) applied; tests updated for user truncation and DB-backed user service coverage.
- Full test suite verified against dedicated PostgreSQL `codementor_test`.
- Per-user solved-problem tracking added (`user_problem_solved`, migration 0003) with mark/unmark/status/list/count endpoints.
- Problemset solved filter added (`?solved=true|false`, ignored for anonymous requests).
- Angular profile, progress dashboard, auth-aware header, login/logout, solved indicators, and solved filter implemented.
- Frontend Vitest setup added; focused `AuthService` and `AuthApi` tests pass.
- Docker Compose passes Codeforces OIDC and AI settings through to the API container.
- Progress endpoint aggregates solved count and difficulty buckets without N+1 frontend requests.
- AI coach endpoint and problem-page hint UI added; provider configuration is optional and the coach returns 503 when disabled.
- Coach service and route tests cover prompt context, provider parsing, timeouts/errors, authentication, and missing problems.
- Submission history added (`submissions` table, migration 0004) applied to `codementor` after backup; authenticated record/list/detail endpoints, per-user isolation, and validation.
- Problem page records submissions with language; profile and progress show recent/history submissions. DB-free service and route tests added.
- Migrations 0002-0004 applied to `codementor`; DB-backed tests run against `codementor_test` (18 passed). All DB-free tests pass (31), lint clean, frontend tests/build pass.
- Sandboxed execution module added (`app/sandbox/`) with Docker-based isolated design, resource limits (CPU/memory/pids/ulimits), read-only filesystem, no network by default, disabled by default. Authenticated API endpoint `/api/sandbox/execute`. DB-free service and route tests added (8 passed). No code executed on host.

## In Progress

- End-to-end readiness verification (startup, DB, Docker permissions, sandbox isolation, flows).

## Next Up

- After readiness verification, consider personalized reports and recommendations. Sandbox remains disabled until secure isolation backend is available/configured.

## Open Questions

- Select and configure the AI provider and model for the initial release.
- Define the sandbox implementation and execution support for every Codeforces-supported programming language.

## Architecture Decisions

- Use FastAPI and Python for the backend, Angular and TypeScript for the frontend, and PostgreSQL with SQLModel for persistent data.
- Use Alembic for versioned database schema changes.
- Keep the application as a modular monolith rather than introducing microservices.
- Use Codeforces authentication as the only sign-in method for the initial release.
- Execute submitted code only in an isolated sandbox with appropriate resource limits, never inside the API process.
- Use an AI API initially rather than training a large language model from scratch.

## Session Notes

- Existing problem discovery, filtering, sorting, pagination, and Codeforces ingestion are implemented.
- Codeforces OIDC sign-in is implemented and covered by focused tests; it remains a verification flow until local accounts and sessions are added.
- User accounts, persistent learning history, AI mentorship, personalized reports, recommendations, and sandboxed code execution remain planned features.
- The full database-backed test suite has not been run because the dedicated `codementor_test` database does not exist.
- The initial release must support all programming languages supported by Codeforces.
- Ask for approval before database migrations or other persistent-state changes.

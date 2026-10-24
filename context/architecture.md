# Architecture Context

## Stack

| Layer      | Technology               | Role                                      |
| ---------- | ------------------------ | ----------------------------------------- |
| Framework  | FastAPI + Python          | Backend API and application logic         |
| UI         | Angular + TypeScript      | Web interface and API integration         |
| Auth       | Codeforces OpenID Connect | User identity verification and profile integration |
| Database   | SQLModel + PostgreSQL     | Data models, queries, and persistent storage |
| Migrations | Alembic                  | Versioned database schema changes         |
| Runtime    | Docker Compose            | Local application and database services   |

## System Boundaries

- `app/core/` — Application settings, database engine, and database session dependency.
- `app/problems/` — Codeforces problem metadata, problem queries, API routes, and problem ingestion.
- `app/users/` — Codeforces OIDC, local accounts, and session authentication.
- `app/solved/` — Per-user solved-problem tracking and progress aggregation.
- `app/submissions/` — Recorded code attempts with metadata and per-user access control.
- `app/ai/` — Progressive-hint coach backed by an OpenAI-compatible chat-completions provider.
- `app/sandbox/` — Planned isolated code execution and resource limits.
- `frontend/`, `migrations/`, `data/`, `tests/` — Angular interface, database migrations, bundled sample problem data, and automated tests.

## Storage Model

- **PostgreSQL**: Codeforces problem metadata, user accounts, sessions, per-user solved-problem tracking, and submission history are stored in the current implementation. Learning reports and recommendations will be stored here as their features are implemented.
- **AI provider**: Hints are generated on demand and are not persisted. Any OpenAI-compatible chat-completions endpoint can be configured; the coach is disabled when credentials/model are missing.
- **File Storage**: No separate file or blob storage is currently configured. Add it only if a future feature requires persistent storage for files or large artifacts.

## Auth and Access Model

- Codeforces OpenID Connect is the sign-in method for the initial release.
- `/api/auth/login` starts the OIDC flow and `/api/auth/callback` verifies the identity token, creates or updates the local account, and starts a signed session.
- Sign-in is disabled with HTTP 503 unless the OIDC client settings and state-signing secret are configured.
- `GET /api/auth/me` returns the current account and `POST /api/auth/logout` clears the session.
- Each authenticated CodeMentor user has a local account linked to their verified Codeforces identity.
- Solved-problem tracking is stored per user in `user_problem_solved` and exposed through `/api/users/me/solved` and problem solved endpoints.
- User-specific submissions, learning history, and reports must be accessible only to their owner unless an explicitly approved feature defines otherwise.

## Invariants

1. PostgreSQL is the primary application database; database schema changes must use Alembic migrations.
2. Existing problem discovery, filtering, sorting, pagination, and Codeforces ingestion must remain functional as new features are added.
3. User-submitted code must not be executed inside the API process; code execution requires an isolated sandbox with appropriate resource limits.
4. Keep the backend as a modular monolith; implement new capabilities within the existing backend unless a separate service is explicitly approved.

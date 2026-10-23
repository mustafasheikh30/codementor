# Code Standards

## General

- Keep modules small and single-purpose.
- Fix root causes, do not layer workarounds.
- Do not mix unrelated concerns in one component, route, or service.
- Preserve existing behavior and verify relevant tests when making changes.

## TypeScript

- Follow the existing Angular and TypeScript conventions.
- Avoid `any` — use explicit interfaces or narrowly scoped types.
- Validate unknown external input at system boundaries before trusting it.

## Python / FastAPI

- Use type hints for function parameters and return values.
- Keep route handlers focused on HTTP concerns and delegate business logic to appropriate modules.
- Use Pydantic or SQLModel validation at system boundaries.
- Use dependency injection for shared resources such as database sessions.
- Keep database access and business logic separate where the existing architecture supports it.
- Handle errors explicitly and return consistent API responses.

## Styling

- Use the CSS custom properties defined in `ui-context.md` — avoid hardcoded colors when an existing token is appropriate.
- Follow the border radius and layout conventions defined in `ui-context.md`.
- Preserve the existing Angular component and custom CSS approach.

## API Routes

- Validate and parse request input before business logic runs.
- Enforce authentication and resource ownership before accessing or modifying user-specific data.
- Return consistent, predictable response shapes.
- Preserve existing API behavior unless a change is explicitly approved.

## Data and Storage

- Store persistent application metadata and learning history in PostgreSQL.
- Use SQLModel for database models and Alembic for schema migrations.
- Do not commit secrets or credentials; use environment-based configuration.
- Avoid storing large generated artifacts directly in the database when a suitable storage approach is required.

## File Organization

- `app/core/` — Application settings, database engine, and shared dependencies.
- `app/problems/` — Codeforces problem models, queries, routes, and ingestion.
- `app/users/` — User accounts and Codeforces identity integration.
- `app/submissions/` — Code attempts, analysis history, and learning activity.
- `app/ai/` — AI provider integration, diagnosis, hints, and retrieval.
- `app/sandbox/` — Isolated code execution and resource limits.
- `frontend/` — Angular application and TypeScript components.
- `migrations/` — Versioned database schema changes.
- `tests/` — Automated tests for application behavior.

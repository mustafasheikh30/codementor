# CodeMentor

An agentic competitive-programming coach: browse Codeforces problems in a dark,
Codeforces-style UI, then (in later milestones) get graded hints, similar problems and
counterexamples for your wrong solutions.

**Stack:** FastAPI · PostgreSQL · SQLModel · Alembic · Angular · Docker Compose

## Run everything with Docker

```bash
docker compose up --build
# in another terminal, load data once:
docker compose exec api python -m app.problems.ingest
```

Open http://localhost:8080 (API docs at http://localhost:8080/api/docs).

Use `docker compose exec api python -m app.problems.ingest --seed` to load a tiny sample
set instead of the real problemset.

## Local development

You need `uv`, Node 22+ and Docker (for Postgres).

```bash
docker compose up -d db                     # Postgres on localhost:5432
cp .env.example .env
uv sync
uv run alembic upgrade head                 # create tables
uv run python -m app.problems.ingest        # load real problems (or add --seed)
uv run fastapi dev app/main.py              # API on :8000

cd frontend && npm install && npx ng serve  # UI on :4200 (proxies /api to :8000)
```

## Codeforces sign-in

Register an OAuth application with Codeforces, then set these values in `.env`:

```bash
CODEFORCES_OIDC_CLIENT_ID=...
CODEFORCES_OIDC_CLIENT_SECRET=...
CODEFORCES_OIDC_STATE_SECRET=...   # long random value used to sign the session cookie
CODEFORCES_OIDC_REDIRECT_URI=http://localhost:4200/api/auth/callback
```

Use `http://localhost:4200/api/auth/callback` for `ng serve` and
`http://localhost:8080/api/auth/callback` for Docker Compose. The redirect host must be
the one the browser uses, because the callback finishes by redirecting back to the
frontend. `GET /api/auth/login` redirects to Codeforces; the callback verifies the
identity token, creates or updates the local account, and starts a 14-day session.
`GET /api/auth/me` returns the current account, `POST /api/auth/logout` clears the
session, and sign-in responds with `503` while any value above is missing.

Signed-in users can mark problems solved. `GET /api/users/me/solved` and
`/api/users/me/solved/count` power the profile and progress pages, and
`/api/problems?solved=true|false` filters the problemset (the parameter is ignored for
anonymous requests).

## AI coach

Set an OpenAI-compatible chat-completions provider in `.env`:

```bash
AI_API_KEY=...
AI_BASE_URL=https://api.openai.com/v1   # any compatible endpoint
AI_MODEL=...
```

Signed-in users can request a progressive hint from the problem page
(`POST /api/coach/hint?contest_id=4&index=A`). Leaving the key or model empty disables
the coach with HTTP 503; the rest of the app continues to work. The API never executes
submitted code.

## Tests and checks

```bash
# tests use a separate database; create it once:
docker compose exec db psql -U codementor -c "CREATE DATABASE codementor_test"
uv run pytest
uv run ruff check . && uv run ruff format --check .
cd frontend && npx tsc --noEmit && npx ng test --watch=false && npx ng build
```

## Layout

```
app/
  core/        settings, DB engine and session dependency
  problems/    models, schemas, service (queries), routes, Codeforces ingestion
  users/       Codeforces OIDC client, accounts, and authentication routes
  solved/      per-user solved-problem tracking and progress endpoints
migrations/    Alembic migrations (schema changes always go through these)
data/          bundled sample problems
tests/         pytest, run against real Postgres
frontend/      Angular app (lazy-loaded pages, URL-driven filters)
```

## Changing the database schema

1. Edit the SQLModel class in `app/problems/models.py`.
2. `uv run alembic revision --autogenerate -m "describe the change"`
3. Read the generated file in `migrations/versions/`, then `uv run alembic upgrade head`.

## Not affiliated with Codeforces

Problem metadata comes from the public Codeforces API. Statements are not stored;
problem pages link to Codeforces.

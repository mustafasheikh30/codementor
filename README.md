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

## Tests and checks

```bash
# tests use a separate database; create it once:
docker compose exec db psql -U codementor -c "CREATE DATABASE codementor_test"
uv run pytest
uv run ruff check . && uv run ruff format --check .
cd frontend && npx ng build
```

## Layout

```
app/
  core/        settings, DB engine and session dependency
  problems/    models, schemas, service (queries), routes, Codeforces ingestion
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

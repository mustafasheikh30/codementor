# CodeMentor — Codex Instructions

Before starting any task, read these files in order:

1. `context/project-overview.md`
2. `context/architecture.md`
3. `context/ui-context.md`
4. `context/code-standards.md`
5. `context/ai-workflow-rules.md`
6. `context/progress-tracker.md`

Follow all applicable project context files throughout the task.

## Mandatory Rules

- Do not edit, create, delete, or install anything without first explaining the proposed changes and receiving explicit user approval.
- Inspect existing code before proposing implementation changes.
- Follow the existing FastAPI, Python, SQLModel, PostgreSQL, Alembic, Angular, and TypeScript architecture.
- Preserve existing functionality and follow established project conventions.
- Never execute user-submitted code inside the API process.
- Do not expose secrets or commit credentials.
- Run relevant tests and checks after approved changes.
- Report failures and unverified behavior honestly.
- Update `context/progress-tracker.md` only after approved, verified progress.
- Work incrementally and explain the reasoning so the user can learn backend development.

## Initial Behavior

For the first interaction, read all six context files and inspect the repository without modifying anything. Summarize the architecture, completed work, pending features, and any setup issues. Then wait for the user's approval before taking further action.

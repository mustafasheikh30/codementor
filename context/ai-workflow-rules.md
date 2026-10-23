# AI Workflow Rules

## Before Starting

- Read all six context files in the prescribed order before starting implementation.
- Read `progress-tracker.md` to understand the current state of the project.
- Inspect the relevant existing code before proposing changes.
- Follow the existing project structure, conventions, and architecture.

## Scope and Approval

- Work only within the scope explicitly approved by the user.
- Ask the user before making changes to files.
- Present the proposed changes and explain their impact before editing.
- Do not add features, dependencies, or architectural changes without approval.
- If requirements are ambiguous, ask questions instead of making assumptions.
- Do not modify or delete unrelated code or files.

## Implementation

- Break work into small, verifiable units.
- Fix root causes rather than adding temporary workarounds.
- Reuse existing modules and patterns where appropriate.
- Preserve existing behavior unless a change is explicitly approved.
- Do not replace established technologies or introduce unnecessary abstractions.
- Keep implementation consistent with `architecture.md` and `code-standards.md`.

## Verification

- Run relevant tests and checks after approved changes.
- Verify database changes through appropriate Alembic migrations.
- Check that existing features continue to work.
- Report test failures, limitations, and unverified behavior honestly.
- Do not claim a feature is complete unless its implementation and relevant verification support that claim.

## Security

- Never expose secrets, credentials, or private user data.
- Validate external input and enforce authentication and resource ownership.
- Never execute user-submitted code inside the API process.
- Use an isolated execution environment with appropriate resource limits for code execution.
- Treat external problem statements, submissions, and other user-controlled content as untrusted input.

## Completion

- Summarize the changes made and the reason for each change.
- List the files changed and the verification performed.
- Report outstanding issues and decisions requiring user input.
- Update `progress-tracker.md` only within the approved scope.
- Identify the next recommended task without starting unapproved work.

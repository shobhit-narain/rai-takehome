# Time-Off Microservice - Claude Code Operating Instructions

## Goal

Implement this repository as cost-effectively as possible in terms of tokens, turns, and tool actions.

Use the existing repository documents and generated files as the source of truth. Do not redesign the architecture unless required to make the current milestone work.

## Primary rules

- Minimize turns, tool actions, and back-and-forth.
- Batch related edits into as few file operations as possible.
- Do not explore broadly or offer multiple options unless blocked.
- Do not restate requirements or summarize repository documents.
- Prefer the smallest working implementation that satisfies the existing docs and tests.
- Prefer simple stubs with correct interfaces over full implementations when downstream files depend on them.
- Keep imports, package structure, and pytest execution working at all times.
- Run only the narrowest relevant tests for the current milestone.
- Stop immediately once the milestone is green.
- Ask questions only if a missing decision blocks implementation.

## Implementation workflow

1. Inspect current files and docs already present in the repo.
2. Infer the target end state for the current milestone before editing.
3. Identify the minimum missing files needed for the next runnable milestone.
4. Implement them in one pass where possible.
5. Run the narrowest relevant tests.
6. Fix only failures directly related to the current milestone.
7. Stop and report succinctly.

## Scope control

- Work strictly in dependency order.
- First make the smallest runnable vertical slice.
- Expand only what is required by the next failing tests.
- Do not implement speculative features not required by the current slice.
- Avoid optional enhancements, polish, or refactors unless they unblock progress.
- Keep code simple, explicit, and testable.
- Avoid unnecessary abstractions.
- Avoid TODO comments unless essential.
- Only write comments, if required. We want functional code first.

## Cost control

- Keep project instructions stable to preserve prompt caching.
- Reuse existing repository structure and docs instead of re-deriving plans.
- Prefer milestone-specific execution over broad project-wide implementation.
- Avoid full test suite runs until a large enough slice is ready.
- Avoid re-reading large files unless needed for the current task.
- Avoid spawning subagents unless there is a clear payoff; subagents can add context re-establishment overhead.
- Prefer one continuous session for a focused milestone to preserve cache locality.
- Use compaction only when needed; after compaction, continue with a tightly scoped milestone.
- Keep outputs concise.
- Do not generate prose or documentation files unless they are part of the requested milestone.

## Turn and test discipline

- Assume each extra debugging loop is costly.
- Before editing, think through the likely end state and batch changes.
- When tests fail, fix the smallest root cause first.
- Run a single file, test class, or focused pytest target whenever possible.
- Do not run broad integration or e2e tests until lower layers are stable.

## Model discipline

- Use the smallest capable model for the current milestone.
- Escalate to a stronger model only for hard refactors, cross-file debugging, or repeated failures.
- If using a cheaper model causes repeated fix-up loops, switch up once rather than paying for many extra turns.

## Effort discipline

- Prefer medium effort by default.
- Keep output reasoning concise unless deeper reasoning is necessary to unblock execution.

## Reporting format

After each implementation pass, report only:

1. Files created or modified
2. Commands run
3. Result
4. Blocker, if any

## Repository-specific priorities

- Python only
- FastAPI + SQLAlchemy + pytest
- Follow docs/TRD.md, docs/API_SPEC.md, docs/IMPLEMENTATION_PLAN.md, docs/REPO_BLUEPRINT.md, and docs/TEST_PLAN.md
- Continue implementation in the documented dependency order
- Preserve deterministic seed data and local file-backed mock HCM behavior where already established
- Before executing the implementation make sure all dependencies are properly installed and the environment is correctly setup for linting and testing
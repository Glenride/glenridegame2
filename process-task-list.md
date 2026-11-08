# Task List Management – Telegram Romance Simulation Bot

Project artifacts:

- **PRD**: `create-prd.md`
- **Task List**: `generate-tasks.md`
- **Analytics Spec**: events defined under Functional Requirement 6 & Task Group 6

Use this document as the working agreement for driving `generate-tasks.md` to completion.

## Execution Protocol

1. Always verify the next unchecked sub-task in `generate-tasks.md` before coding. Finish items in numerical order unless the user reprioritizes (analytics tasks in §6 must precede premium content work in §7).
2. Work on one sub-task at a time when possible, but you do **not** need to request approval before starting each item.
3. After completing a sub-task:
   - Update `generate-tasks.md`, switching `[ ]` → `[x]` for that sub-task and documenting any new insights below the task if needed (e.g., currency enablement decisions, analytics schema updates).
   - Provide a brief status update to the user after finishing a meaningful milestone (e.g., an entire parent task or a cluster of closely related subtasks).

## Completion Workflow (per parent task)

1. When every sub-task under a parent task is `[x]`:
   - Kill any previously started dev servers related to the work.
   - Run the full automated test suite for the codebase.
   - If tests pass, stage only relevant files (`git add <files>`).
   - Remove temporary logs/scripts.
   - Commit using conventional commits, referencing the task ID (e.g., `feat: wire /start onboarding (Task 1.3)`).
2. After committing, mark the parent task checkbox and note the commit hash beside it in `generate-tasks.md`.
3. Start a fresh server session so the user can validate the changes.

## Task List Hygiene

- Keep the `Relevant Files` section of `generate-tasks.md` synchronized with actual changes (new modules, tests, configs, etc.).
- If new work emerges, add additional sub-tasks beneath the appropriate parent task, documenting why.
- Reference environment differences (dev/test/prod) in task notes when behavior diverges.
- Note analytics dependencies: Task 6 must emit events before Tasks 4 & 7 mark complete; payment changes should reference the active currency set.

## Testing & Logging

- Prefer simple, deterministic tests colocated with their modules (see `tests/` directory).
- Expand logging for difficult bugs, then remove noisy logs before committing unless they serve ongoing diagnostics. Ensure analytics events are validated in `tests/test_analytics.py` before marking Task 6 subtasks complete.

## Server Management

- Before launching any server, ensure older related processes are terminated.
- After every code change batch, start a clean server instance so the user can manually verify behavior (including payment sandbox flows and analytics hooks).

## Communication Checklist

- Summaries must cite files with `@filepath#Lx-Ly`.
- Call out any blocking questions or risks immediately in status updates.

Following this process keeps the PRD, tasks, and implementation aligned while honoring user workflow preferences.
# Testing Strategy for Magnetar Mnemosyne

## Types of Tests

- Unit tests: validate focused logic such as dependency handling, conversation parsing, and render job assembly.
- Integration tests: validate HTTP routes, admin flows, and persistence behavior through FastAPI test clients.
- End-to-end tests: planned for full browser-level validation of exam-taking and admin authoring journeys.

## Code Coverage

- Target automated coverage for core logic: `80%+` on newly added modules.
- High-risk modules such as exam persistence and audio conversation parsing should maintain direct test coverage.

## Acceptance Criteria

- Core student exam routes return expected pages and state transitions.
- Admin routes can create exams, import questions, and create structured audio entries.
- Invalid conversation payloads fail predictably during parsing or persistence.
- Schema migrations do not break existing local databases.

## Bug Reporting Process

1. Record the issue in the active tracking system or project plan.
2. If the issue blocks progress, create or update an entry in `BLOCKERS.md`.
3. Capture reproduction details, expected behavior, actual behavior, and environment context.
4. Add a `BITACORA.md` entry for material defects, fixes, or accepted deviations.

## Current Commands

```bash
python3 -m py_compile main.py src/audio/conversation_generator.py src/exams/questions.py src/ui/server.py
.venv/bin/python -m pytest tests
python3 run_tests.py
```

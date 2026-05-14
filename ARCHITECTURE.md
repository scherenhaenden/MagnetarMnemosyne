# Architecture of Magnetar Mnemosyne

## High-Level Diagram

```text
Browser
  |
  v
FastAPI UI Layer (`src/ui/server.py`)
  |-- Jinja2 templates (`src/ui/templates`)
  |-- Admin routes
  |-- Student exam routes
  |
  v
Domain Modules
  |-- Exam persistence (`src/exams/questions.py`)
  |-- Audio conversation parsing (`src/audio/conversation_generator.py`)
  |-- Dependency management (`src/utils/dependency_manager.py`)
  |
  v
SQLite (`src/exams/exams.db`)

Optional local render backend
  |
  v
Generated audio assets referenced by `audio_url`
```

## Components

### UI Layer

- Responsibility: expose student and admin workflows over HTTP.
- Technologies: FastAPI, Jinja2, HTMX, Tailwind via CDN.
- Key files: `src/ui/server.py`, `src/ui/templates/index.html`, `src/ui/templates/admin.html`.

### Exam Persistence Layer

- Responsibility: store questions, exams, and results; perform lightweight schema migrations.
- Technologies: Python `sqlite3`, JSON serialization.
- Key file: `src/exams/questions.py`.

### Audio Conversation Module

- Responsibility: normalize and validate multi-speaker listening payloads, parse dialogue blocks, and assemble render jobs.
- Technologies: Python dataclasses, JSON, regex-based dialogue parsing.
- Key file: `src/audio/conversation_generator.py`.

### Dependency Management Layer

- Responsibility: auto-install missing runtime dependencies in local environments when possible.
- Technologies: `importlib`, `subprocess`, `uv` or `pip`.
- Key file: `src/utils/dependency_manager.py`.

## Key Design Decisions

- SQLite is the current persistence backend to keep the system simple and local-first.
- Listening scenes are stored as structured JSON so the same source can drive both display and local TTS rendering.
- Audio generation is treated as an external backend contract rather than embedded directly in request-time UI logic.

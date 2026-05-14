# Architecture & Design

## 1. Modular Overview
The system is divided into three main layers:

### A. Utility Layer (`src/utils`)
- **Dependency Manager**: The "heart" of the auto-healing feature. It handles runtime installation of packages using `subprocess` and `importlib`. It prioritized `uv` if available for performance.

### B. Logic Layer (`src/exams`)
- **SQLite Storage**: Uses `sqlite3` to store questions.
- **Data Model**: Questions are stored with fields for `type`, `question`, `options` (serialized JSON), `correct_answer_index`, and `explanation`.

### C. UI Layer (`src/ui`)
- **FastAPI**: Provides the web server and routing.
- **HTMX**: Used in the frontend to handle partial DOM updates.
- **Jinja2**: Handles HTML templating for both the student and admin interfaces.

### D. Audio Layer (`src/audio`)
- **Conversation Generator**: Normalizes `conversation_json` payloads into speakers, turns, and render jobs.
- **Render Runner**: Dispatches audio generation to interchangeable local backends such as `F5-TTS` and `Kokoro`.
- **Generated Assets**: Stores transcripts, payload snapshots, backend configs, and local render output under `src/generated_audio`.

### E. Configuration Layer (`src/config`)
- **App Settings Loader**: Reads `appsettings.json` and exposes audio backend defaults, paths, and enabled backend options to the UI and render layer.

## 2. Data Flow
1. Server starts via `main.py`.
2. Database is initialized if it doesn't exist.
3. Users interact with the frontend.
4. HTMX makes POST/GET requests to FastAPI.
5. FastAPI updates the state (or DB) and returns rendered HTML fragments.
6. For audio scenes, the admin page builds a normalized conversation payload and sends it to the configured backend runner.
7. Render status, output path, backend command, stdout, and last error are persisted with the audio question.

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

## 2. Data Flow
1. Server starts via `main.py`.
2. Database is initialized if it doesn't exist.
3. Users interact with the frontend.
4. HTMX makes POST/GET requests to FastAPI.
5. FastAPI updates the state (or DB) and returns rendered HTML fragments.

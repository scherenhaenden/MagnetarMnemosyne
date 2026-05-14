# Development Guide

## Setup for Development
1. Clone the repository.
2. If using PyCharm, ensure your interpreter is set correctly.
3. Run `main.py` to let the auto-healer install base dependencies.
4. Review `appsettings.json` and set the audio tool paths for your machine before testing admin audio rendering.

## Adding New Features
- **UI Changes**: Modify templates in `src/ui/templates`.
- **Logic Changes**: Update `src/exams/questions.py` for database/model changes.
- **Testing**: Always add a test in `tests/` and verify with `run_tests.py`.
- **Audio Backends**: Keep backend-specific defaults in `appsettings.json`, not hardcoded in the UI layer.

## Testing Policy
- We target **100% coverage**.
- Use `pytest` for unit and integration tests.
- Mock external calls (like `pip` or `uv`) in the dependency manager tests.

## Audio Development Notes

- `F5-TTS` and `Kokoro` are treated as interchangeable backends from the admin page.
- Backend availability and labels come from `appsettings.json`.
- The create-audio page must stay on the same view when render fails and display the backend error.
- For local backend details and JSON payload format, see [docs/AUDIOS.md](/Users/edwardflores/Projects/Development/MagnetarMnemosyne/docs/AUDIOS.md:1).

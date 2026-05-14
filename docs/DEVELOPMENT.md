# Development Guide

## Setup for Development
1. Clone the repository.
2. If using PyCharm, ensure your interpreter is set correctly.
3. Run `main.py` to let the auto-healer install base dependencies.

## Adding New Features
- **UI Changes**: Modify templates in `src/ui/templates`.
- **Logic Changes**: Update `src/exams/questions.py` for database/model changes.
- **Testing**: Always add a test in `tests/` and verify with `run_tests.py`.

## Testing Policy
- We target **100% coverage**.
- Use `pytest` for unit and integration tests.
- Mock external calls (like `pip` or `uv`) in the dependency manager tests.

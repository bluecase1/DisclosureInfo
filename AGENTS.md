# DisclosureInfo Knowledge Base

Generated for local onboarding and automation context.

## Overview
- FastAPI-based KIND disclosure collection service.
- Core stack: Python 3.11, FastAPI, Pydantic Settings, SQLAlchemy, PostgreSQL/Redis (optional at MVP), Docker.
- Domain: RSS polling, disclosure normalization, categorization, and API delivery.

## Structure
- `src/disclosureinfo/main.py`: FastAPI app factory and router mount (`/api/v1` for disclosures, `/health` for system).
- `src/disclosureinfo/settings.py`: environment-based configuration via `Settings`/Pydantic.
- `src/disclosureinfo/routers/`: API endpoints (`/health`, `/disclosures`, `/categories`, detail endpoint stub).
- `docs/`: API spec, architecture, system rules, and policy documents.
- `scripts/`: helper scripts for scaffolding/docs.
- `pyproject.toml`: dependency and project metadata.
- `tests/`: test files (pytest-based).

## Commands

### Running the Service
```bash
# Start full service stack locally
docker compose up --build

# Or run directly with uvicorn (requires PostgreSQL)
uvicorn disclosureinfo.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Run all tests
pytest

# Run a specific test file
pytest tests/test_api.py

# Run a specific test function
pytest tests/test_api.py::test_list_returns_paginated_results -v

# Run with coverage (if pytest-cov installed)
pytest --cov=src/disclosureinfo --cov-report=html
```

### Linting & Type Checking (no config - uses defaults)
```bash
# Ruff (if installed)
ruff check src/

# MyPy (if installed)
mypy src/

# Black (if installed)
black --check src/
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Rollback one
alembic downgrade -1
```

## Code Style Guidelines

### Imports
- Use absolute imports from package root: `from disclosureinfo.db import get_db`
- Sort with `ruff check --select I src/` or follow standard: stdlib → third-party → local
- Use `from __future__ import annotations` for forward references

### Type Hints
- Use Python 3.11+ syntax: `str | None` instead of `Optional[str]`
- Use `Callable` from `collections.abc` for callables
- Use `Mapped` and `mapped_column` from SQLAlchemy for ORM models
- Add return type hints on all functions: `def foo() -> None:`

### Naming Conventions
- **Classes**: `PascalCase` (e.g., `class DisclosureDetail`)
- **Functions/variables**: `snake_case` (e.g., `def fetch_html()`, `detail_update_existing`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `TEST_DATABASE_URL`)
- **Private members**: Leading underscore (e.g., `self._client`)

### Database Models (SQLAlchemy)
- Use Declarative Base pattern with `Base(DeclarativeBase)`
- Use `Mapped[type] = mapped_column(...)` syntax
- Always define `__tablename__` as string
- Use `func.now()` for server-side defaults
- Use relationships with back_populates for bidirectional links

### Error Handling
- Use `HTTPException` for API errors with appropriate status codes
- Use `tenacity` for retry logic (already used in http_fetcher.py)
- Log warnings for non-critical failures, not exceptions
- Never silently swallow exceptions without logging

### FastAPI Patterns
- Define response models using Pydantic schemas (in `schemas.py`)
- Use dependency injection for DB sessions: `db: Session = Depends(get_db)`
- Use Query parameters with validation: `limit: int = Query(default=50, ge=1, le=200)`
- Return structured responses with `response_model=`

### Settings
- All config via `Settings` class in `settings.py` using Pydantic
- Use `Field(..., alias="ENV_VAR")` for env var mapping
- Never hardcode runtime values

### Testing Patterns
- Use `conftest.py` to set environment variables BEFORE importing app
- Use in-memory SQLite for tests: `sqlite:///:memory:`
- Use dependency overrides for DB: `app.dependency_overrides[get_db] = override_get_db`
- Tests can run standalone: `python tests/test_api.py`

### Project Conventions
- Keep service settings externalized (env/config), avoid hardcoded URLs/intervals/db credentials.
- Prefer explicit, deterministic processing first, then AI fallback where required by policy.
- Favor `uv`/Python module style conventions for consistency with FastAPI service layout.
- API paths should stay under `/api/v1` unless intentionally introducing new public root routes.
- Keep modules small and focused (`api`, `settings`, `collector`, `parser`, `fetcher`, `repositories`, `services`, `classifier`).

### Anti-Patterns (project-level)
- Hardcoding runtime config values.
- Ignoring retry/timeout behavior on network calls.
- Leaving core processing paths untested.
- Using `as any`, `@ts-ignore`, `@ts-expect-error` for type suppression.

### Logging
- Use `structlog` for structured logging
- Get logger per module: `logger = logging.getLogger(__name__)`
- Use extra params for context: `logger.warning("msg", extra={"key": "value"})`

## Agent Output/Commit Rules
- 한글로 출력 가능한 내용은 한글로 우선 작성한다.
- 각 작업별 변경사항은 작업 단위로 분리하여 `git commit` 한다.

## Documentation
- API behavior: `docs/API_SPEC.md`, `src/disclosureinfo/routers/disclosures.py`
- Platform constraints: `docs/SYSTEM_RULES.md`
- Data model: `docs/RSS_SPEC.md`, `docs/CATEGORY_POLICY.md`
- OpenAPI docs: http://localhost:8000/docs (when running)

## Notes
- Mandatory categories documented in `docs/CATEGORY_POLICY.md`
- Currently returns placeholders in some endpoints; downstream tasks should fill DB/service layer wiring.

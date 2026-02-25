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

## Where To Look
- API behavior and responses: `docs/API_SPEC.md`, `src/disclosureinfo/routers/disclosures.py`.
- Platform constraints and rules: `docs/SYSTEM_RULES.md`.
- Data and category model: `docs/RSS_SPEC.md`, `docs/CATEGORY_POLICY.md`.
- Deployment/run commands: `README.md`.

## Conventions
- Keep service settings externalized (env/config), avoid hardcoded URLs/intervals/db credentials.
- Prefer explicit, deterministic processing first, then AI fallback where required by policy.
- Favor `uv`/Python module style conventions for consistency with FastAPI service layout.
- API paths should stay under `/api/v1` unless intentionally introducing new public root routes.
- Keep modules small and focused (`api`, `settings`, `collect`, `storage`, `ai` split) as complexity grows.

## Anti-Patterns (project-level)
- Hardcoding runtime config values.
- Ignoring retry/timeout behavior on network calls.
- Leaving core processing paths untested.

## Commands
```bash
docker compose up --build          # start full service stack locally
```
- Docs: OpenAPI at `http://localhost:8000/docs`

## Notes
- `routers/disclosures.py` currently returns placeholders; downstream tasks should fill DB/service layer wiring.
- Mandatory categories are documented in `docs/CATEGORY_POLICY.md`.

## Agent Output/Commit Rules
- 한글로 출력 가능한 내용은 한글로 우선 작성한다.
- 각 작업별 변경사항은 작업 단위로 분리하여 `git commit` 한다.

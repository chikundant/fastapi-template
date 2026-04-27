# FastAPI Template — Improvement Plan

## ⚠️ Security note
[.env](.env) contains real-looking API keys (Google, OpenAI, LangSmith). Rotate them immediately and confirm `.env` is gitignored. Keys must never be committed.

---

## Current state

```
app/
├── __init__.py          # creates lifespan, calls init_sentry, mounts /fastapi-template/api/v1
├── run.py               # uvicorn entry
├── agent/agent.py       # 1-line stub: create_agent(model="gpt-5")
├── core/
│   ├── settings.py      # Settings + DBSettings (no .env loading configured)
│   └── logger.py        # empty
├── db/connections.py    # async engine provider, session dep, retry logic
├── exceptions/repos.py  # 4 exception classes
├── models/base.py       # SQLAlchemy DeclarativeBase
├── repositories/base.py # BaseRepo (broken: imports `Base` from sqlalchemy.orm)
├── routers/rest/user.py # single dummy GET returning {"hi there"}
├── schemas/base.py      # BaseSchema with custom dump methods
└── utils/sentry.py      # init_sentry
tests/                   # empty
```

## Issues found

### Dead / unused / broken
- [app/utils/sentry.py](app/utils/sentry.py) + `sentry-sdk` dependency — remove entirely.
- [app/agent/agent.py](app/agent/agent.py) — stub with `model="gpt-5"` (invalid). Replace with a working minimal langgraph agent; keep `langgraph.json`, `langchain`, `langchain-openai`, `langgraph-cli`.
- [entrypoint.dev.sh](entrypoint.dev.sh) — references `app.main:app` which doesn't exist.
- [poetry.lock](poetry.lock) alongside [uv.lock](uv.lock) — drop `poetry.lock` (project uses uv).
- [app/core/logger.py](app/core/logger.py) — empty.
- [app/repositories/base.py:7](app/repositories/base.py#L7) — `from sqlalchemy.orm import Base` is wrong; never executed.
- `BaseSchema.model_dump_json` override duplicates pydantic's API for marginal value.
- [app/__init__.py:13](app/__init__.py#L13) — `setup_routers` is called inside `lifespan` (runs at startup, not at app build time). Routers should be registered before the app is returned.
- [app/db/connections.py:54](app/db/connections.py#L54) — references `settings.PATH` which doesn't exist on `DBSettings`.
- `Settings` doesn't load `.env` (no `SettingsConfigDict(env_file=...)`).
- `tests/` directory empty.
- `.langgraph_api/` cache present; ensure ignored.

### Dockerfile
Old multi-stage with `pip install uv` + `uv export` + `pip install`. Replace with the uv-based Dockerfile (3.13-slim, `/opt/venv`, `uv sync --frozen --no-dev --no-install-project`).

### docker-compose.yml
- Uses removed `target: dev`.
- `version: "3.8"` is obsolete.
- Bind-mounts whole repo over `/app` (kills the image's installed deps).

### Misc
- `requires-python = ">=3.14"` but Dockerfile targets 3.13. Align to 3.13.
- `app.include_router(api_router, prefix="/fastapi-template")` — odd nesting (`/fastapi-template/api/v1/user/`); flatten to `/api/v1`.

---

## Proposed plan

### 1. Remove (cleanup)
- Delete [app/utils/sentry.py](app/utils/sentry.py), drop `sentry-sdk` from [pyproject.toml](pyproject.toml), remove `init_sentry` call and `SENTRY_DSN` setting.
- Replace [app/agent/agent.py](app/agent/agent.py) stub with a working minimal langgraph agent (`create_react_agent`, real model id, one example tool). Keep `langgraph.json`, `langchain`, `langchain-openai`, `langgraph-cli`.
- Delete [entrypoint.dev.sh](entrypoint.dev.sh) (broken, unused with new Dockerfile).
- Delete [poetry.lock](poetry.lock).
- Delete empty [app/core/logger.py](app/core/logger.py) (or fill with minimal logger setup if we keep it).
- Delete [app/utils/](app/utils/) if it ends up empty.
- Delete the committed [.env](.env) — keep [example.env](example.env) only.

### 2. Restructure (align with reference repo)
Target layout:
```
app/
├── __init__.py
├── run.py
├── core/
│   ├── __init__.py
│   ├── settings.py         # Settings with env_file=".env"
│   └── logger.py            # optional minimal logging config
├── db/
│   ├── __init__.py
│   └── session.py           # engine + session dependency (renamed from connections.py)
├── models/
│   └── base.py
├── schemas/
│   └── base.py              # simplified
├── repositories/
│   └── base.py              # fixed
├── services/                # NEW — business logic layer
│   └── __init__.py
├── routers/
│   ├── __init__.py
│   └── rest/
│       ├── __init__.py
│       └── health.py        # replace dummy /user with /health
└── exceptions/
    └── repos.py
```

### 3. Fix and improve code quality
- [app/__init__.py](app/__init__.py): build the app at import time (router registration outside `lifespan`); keep `lifespan` only for DB pool init/teardown using `init_db_pool` / `close_db_pool`. Drop the `/fastapi-template` prefix.
- [app/core/settings.py](app/core/settings.py): add `model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__", extra="ignore")`. Drop `SENTRY_DSN`. Make DB DSN realistic (no `"AsyncDSN"` placeholder string).
- `app/db/session.py`: simplify — remove unused `provide_db_pool` async-cm and `_db_json` helper unless we actually need numpy/datetime in JSONB. Drop the retry loop (rely on orchestrator restarts).
- [app/repositories/base.py](app/repositories/base.py): import `Base` from `app.models.base`; collapse overlapping `add` / `create`.
- [app/schemas/base.py](app/schemas/base.py): remove the `model_dump_json` override (pydantic handles it); keep `BaseSchema` with config + a small `dump()` shortcut only if reused.
- [app/models/base.py](app/models/base.py): keep — clean. Drop the `dict()` method unless used.
- `app/routers/rest/`: replace `user.py` placeholder with `health.py` returning `{"status": "ok"}`.

### 4. Replace Dockerfile
Use the uv-based Dockerfile (3.13-slim, `/opt/venv`, `uv sync --frozen --no-dev --no-install-project`).

### 5. Fix docker-compose.yml
- Drop `version:` line.
- Remove `target: dev` (single-stage now).
- Remove the `volumes: - .:/app` bind mount, or document it as dev-only.
- Add a healthcheck for `db` and `depends_on: { condition: service_healthy }`.

### 6. pyproject.toml
- Set `requires-python = ">=3.13"`.
- Final deps: `fastapi`, `uvicorn`, `pydantic`, `pydantic-settings`, `sqlalchemy[asyncio]`, `asyncpg`, `orjson`.
- Dev: `pytest`, `pytest-asyncio`, `ruff`, `httpx` (for TestClient).
- Add `[tool.ruff]` config block.

### 7. Tests
Add a minimal `tests/test_health.py` hitting `/api/v1/health` so `make verify` does something.

### 8. README
[README.md](README.md) is empty. Add a short README with: requirements, `cp example.env .env`, `make run`, endpoints. (Only if explicitly requested.)

---

## Order of execution

1. Cleanup (delete sentry, agent, langgraph, poetry.lock, broken scripts).
2. Update `pyproject.toml` + regenerate `uv.lock`.
3. Replace Dockerfile + fix docker-compose.
4. Fix `core/settings.py` (env loading).
5. Fix `app/__init__.py` (lifespan / routing).
6. Fix `db/connections.py` → `db/session.py` and the broken `repositories/base.py` import.
7. Replace dummy router with `/health`.
8. Add a smoke test, run `make verify`, run `docker compose up --build`, hit the endpoint.

---

## Open questions

1. **Keep `repositories/` + `services/` skeletons** even though there's no real domain yet? Recommendation: yes — wired layers give users a place to add code.
2. **Drop DB entirely** vs keep async SQLAlchemy + Postgres? Recommendation: keep it (matches reference repo).

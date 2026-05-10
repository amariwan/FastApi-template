---
name: create-service
description: Scaffolds a new backend service module under app/services/<service_name>/ following the repo's clean architecture conventions. Use this skill whenever the user wants to add a new service, feature module, or domain package to the backend — even if they just say "add a X service", "create a module for Y", or "scaffold Z". Also triggers when wiring a new router into the app, adding domain models with persistence, or setting up use-case/application logic for a new domain. Always use this skill instead of guessing the folder structure.
---

# Create Service Skill

Scaffolds a production-ready backend service following clean architecture conventions.  
The Core Loader auto-discovers any subdirectory under `app/services/` that contains an `integration.py` — so structure must be exact.

---

## Decision: Which pattern to use?

| Situation | Pattern |
|---|---|
| Simple service, 1 entity | `service.py` directly, no Mixins |
| Multiple entities / complex logic | Mixin pattern |
| Complex query logic | Extract to `_<entity>_query.py` |
| Other services consume this one | Add `contracts/schemas.py` |
| Custom validation rules | Add `validation/` layer |
| No persistence needed | Omit `models/` and `repositories/` |

---

## MUST Rules

1. Directory: `app/services/<service_name>/` — valid Python package name, lowercase, no hyphens, no leading underscore.
2. `integration.py` must export `register_service() -> ServiceRegistration`.
3. `ServiceRegistration.routers` must be `list[APIRouter]` — at least one router required.
4. `startup_hooks` / `shutdown_hooks` must be lists of callables. Pairs must be index-aligned; shutdown receives the startup return value at the same index.
5. **No side effects on import** — no connections, no expensive init outside of startup hooks.
6. `runtime_config_hook` (if present) must return `Mapping[str, object]`.
7. `use_api_prefix=True` by default. Use `False` only for root-level health/metrics endpoints.

---

## Directory Structure

```
app/services/<service_name>/
├── __init__.py
├── constants.py
├── patterns.py                     # optional: regex patterns
├── integration.py                  # ← REQUIRED
├── integration_test.py
├── smoke_imports_test.py
├── README.md
│
├── api/
│   ├── __init__.py
│   ├── router.py                   # aggregates sub-routers
│   ├── dependencies.py
│   ├── error_handlers.py
│   └── <resource>/
│       ├── __init__.py
│       ├── create.py  + create_test.py
│       ├── get.py     + get_test.py
│       ├── list.py    + list_test.py
│       ├── patch.py   + patch_test.py
│       ├── update.py  + update_test.py
│       └── delete.py  + delete_test.py
│
├── application/
│   ├── __init__.py
│   ├── service.py
│   ├── service_test.py
│   ├── _<entity>_mixin.py          # one mixin per entity if using mixin pattern
│   ├── _helpers.py
│   ├── _audit_mixin.py             # if audit trail needed
│   └── ports/
│       ├── __init__.py
│       └── <adapter_name>.py
│
├── domain/
│   ├── __init__.py
│   ├── exceptions.py
│   ├── ports.py                    # alternative to application/ports/ for simple services
│   ├── entities/
│   └── value_objects/
│
├── infrastructure/
│   ├── __init__.py
│   ├── providers.py
│   └── <adapter>.py
│
├── models/
│   ├── __init__.py
│   └── base.py                     # SQLAlchemy ORM models
│
├── repositories/
│   ├── __init__.py
│   ├── <entity>_repository.py
│   ├── _<entity>_query.py
│   ├── _<entity>_serialization.py
│   └── _<entity>_types.py
│
├── schemas/
│   ├── __init__.py
│   ├── common.py
│   ├── request/
│   └── response/
│
├── errors/
│   ├── __init__.py
│   └── api.py
│
├── messages/
│   ├── messages.de.json
│   └── messages.en.json
│
├── contracts/                      # only if other services consume this one
│   ├── __init__.py
│   └── schemas.py
│
└── tests/
    ├── e2e/
    │   └── <service_name>_workflow_e2e_test.py
    └── integration/
        └── <service_name>_api_integration_test.py
```

> Unit tests are co-located as `<module>_test.py` next to source files.  
> `tests/e2e/` and `tests/integration/` are strictly for higher-level tests.

---

## Code Templates

### `integration.py`

```python
from app.core.core_extensions.loader import ServiceRegistration
from .api.router import router


async def startup(app):
    # app.state.my_client = await MyClient.connect()
    pass


async def shutdown(app, startup_result):
    pass


def register_service() -> ServiceRegistration:
    return ServiceRegistration(
        name="<service_name>",
        routers=[router],
        startup_hooks=[startup],
        shutdown_hooks=[shutdown],
        use_api_prefix=True,
    )
```

### `api/router.py`

```python
from fastapi import APIRouter
from .example import create, get, list as list_, patch

router = APIRouter(prefix="/<service_name>", tags=["<ServiceName>"])

router.include_router(create.router)
router.include_router(get.router)
router.include_router(list_.router)
router.include_router(patch.router)
```

### `api/<resource>/create.py`

```python
from fastapi import APIRouter, Depends, status
from app.services.<service_name>.api.dependencies import get_service
from app.services.<service_name>.schemas.request.<service_name> import <Entity>CreateRequest
from app.services.<service_name>.schemas.response.<service_name> import <Entity>Response
from app.services.<service_name>.application.service import <ServiceName>Service

router = APIRouter()

@router.post("/", response_model=<Entity>Response, status_code=status.HTTP_201_CREATED)
async def create_<entity>(
    body: <Entity>CreateRequest,
    svc: <ServiceName>Service = Depends(get_service),
) -> <Entity>Response:
    return await svc.create(body)
```

### `api/dependencies.py`

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.core_db.db_dependency import get_db
from app.services.<service_name>.application.service import <ServiceName>Service
from app.services.<service_name>.repositories.<entity>_repository import <Entity>Repository


def get_service(db: AsyncSession = Depends(get_db)) -> <ServiceName>Service:
    repo = <Entity>Repository(db)
    return <ServiceName>Service(repo)
```

### `application/service.py` — Mixin Pattern

```python
# application/_example_mixin.py
class ExampleMixin:
    async def create_example(self, ...) -> ...: ...
    async def get_example(self, ...) -> ...: ...


# application/service.py
from ._example_mixin import ExampleMixin
from ._status_mixin import StatusMixin
from ._audit_mixin import AuditMixin

class <ServiceName>Service(ExampleMixin, StatusMixin, AuditMixin):
    def __init__(self, repo: ...) -> None:
        self._repo = repo
```

### `domain/exceptions.py`

```python
from app.shared.errors.exceptions import AppError

class <Entity>NotFoundError(AppError): ...
class <Entity>ConflictError(AppError): ...
class <Entity>ValidationError(AppError): ...
```

### `errors/api.py`

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from app.services.<service_name>.domain.exceptions import <Entity>NotFoundError

async def handle_not_found(request: Request, exc: <Entity>NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})
```

Register in `integration.py` startup hook:
```python
app.add_exception_handler(<Entity>NotFoundError, handle_not_found)
```

### `repositories/<entity>_repository.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.<service_name>.models.base import <Entity>


class <Entity>Repository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, entity_id: str) -> <Entity> | None:
        return await self._db.get(<Entity>, entity_id)

    async def save(self, entity: <Entity>) -> <Entity>:
        self._db.add(entity)
        await self._db.flush()
        return entity
```

### `messages/messages.en.json`

```json
{
  "<service_name>": {
    "not_found": "<Entity> not found.",
    "created": "<Entity> successfully created.",
    "updated": "<Entity> successfully updated.",
    "deleted": "<Entity> successfully deleted."
  }
}
```

---

## Tests

### Unit (co-located)

```python
# application/service_test.py
import pytest
from unittest.mock import AsyncMock
from .service import <ServiceName>Service

@pytest.fixture
def svc():
    return <ServiceName>Service(repo=AsyncMock())

async def test_create_returns_entity(svc):
    result = await svc.create(...)
    assert result.id is not None
```

### Integration

```python
# tests/integration/<service_name>_api_integration_test.py
from fastapi.testclient import TestClient
from app.asgi import app

client = TestClient(app)

def test_create_<entity>():
    r = client.post("/api/<service_name>/", json={...})
    assert r.status_code == 201
```

### Smoke Import Test

```python
# smoke_imports_test.py
def test_integration_importable():
    from app.services.<service_name> import integration
    assert hasattr(integration, "register_service")
```

---

## Local Dev

```bash
uvicorn app.asgi:app --reload --port 5000
pytest app/services/<service_name>/ -q
pytest app/services/<service_name>/tests/ -q --tb=short
```

---

## PR Checklist

- [ ] `integration.py` with `register_service()` → `ServiceRegistration`
- [ ] `smoke_imports_test.py` present
- [ ] API: one package per resource, one file per HTTP verb
- [ ] No cross-service imports (only `core/` and `shared/`)
- [ ] Unit tests co-located as `<module>_test.py`
- [ ] E2E/Integration tests under `tests/e2e/` or `tests/integration/`
- [ ] `messages.de.json` + `messages.en.json` present
- [ ] `schemas/request/` and `schemas/response/` separated
- [ ] Domain exceptions in `domain/exceptions.py`, HTTP mapping in `errors/api.py`
- [ ] Alembic migration created if new ORM models added
- [ ] `__init__.py` in every package folder
- [ ] Type hints complete, `ruff check .` clean

# Services Guide

**TL;DR:** Create a standalone service package under `src/{{ cookiecutter.package_name }}/services/<service_name>/`, implement the necessary layers there (api, application, domain, infrastructure, tests), and export an `integration.py` file with a `register_service()` function. The Core Loader will
automatically load all subdirectories in `src/{{ cookiecutter.package_name }}/services/` that contain an `integration.py`.

**Important:** This document describes binding rules (MUST) and recommendations (SHOULD) for new services. It avoids examples that directly reference existing `doc*` modules — the rules apply universally to all new microservices in this repository.

## Rules (MUST)

1. **Placement:** The service directory must be located under `src/{{ cookiecutter.package_name }}/services/<service_name>/` and must contain an `integration.py` file.
2. **Package Name:** `<service_name>` must be a valid Python package name (lowercase, letters/numbers/underscores), must not start with an underscore (`_`), and must not contain hyphens.
3. **`integration.py`:** Must export a callable function named `register_service()`. This function must return either a `ServiceRegistration` object or a `dict` with compatible fields.
4. **Routers:** `ServiceRegistration.routers` must be a `list` and exclusively contain `fastapi.APIRouter` instances. At least one router per service is mandatory.
5. **Hooks:** `startup_hooks` and `shutdown_hooks` must be lists of callables. If startup hooks create resources (e.g., a DB client), the corresponding shutdown hook at the same index position must cleanly release that resource. The lengths of these lists should match.
6. **No Side Effects on Import:** Importing the `src/{{ cookiecutter.package_name }}/services/<service_name>/integration.py` module must not establish connections or execute expensive initializations. All connections/clients must be initialized within the startup hooks.
7. **Type Compliance:** `runtime_config_hook` (if present) must be callable and return a `Mapping[str, object]`.
8. **Prefix Behavior:** `use_api_prefix` controls whether the routers are mounted with the global `API_PREFIX` (Default: `True`). Use `False` only if a root/global path is explicitly required (e.g., special metric or health endpoints, if desired).

## Recommendations (SHOULD)

- Use router tags (`APIRouter(tags=[...])`) for OpenAPI documentation.
- Use `Depends(...)` for DI-capable provider functions (e.g., `get_db_client`).
- Store long-lived clients in `app.state` (e.g., `app.state.my_client`) during the startup hook and read them in your dependencies.
- Write unit and integration tests per layer; router tests can utilize `fastapi.testclient.TestClient`.
- Briefly document new endpoints in the `README.md` of the service folder.

## Technical Details / Loader Notes

- **Discovery:** The Core Loader searches `src/{{ cookiecutter.package_name }}/services/` for subdirectories containing an `integration.py` and imports `{{ cookiecutter.package_name }}.services.<service_name>.integration`.
- **`ServiceRegistration` Constraints:** `routers` must be `list[APIRouter]`; `startup` and `shutdown` must be `list[callable]`; `runtime_config` must be callable or `None`; `use_api_prefix` must be a `bool`.
- **Startup/Shutdown Execution:** Startup hooks are executed in order, and their return values are collected. During shutdown, the shutdown hooks are called in reverse order; `shutdown_hooks[i]` receives the startup result at index `i` (if any). Ensure that pairs (startup, shutdown) are aligned
  correctly.
- **Async vs Sync:** Startup/Shutdown callables can be sync or async. Background tasks (`asyncio.Task`/`Future`) returned by startup are _not_ awaited by the loader — they remain as tasks and can be canceled/awaited during shutdown.

## Conventions / Naming

- **Package:** `{{ cookiecutter.package_name }}.services.<service_name>`
- **Integration file:** `src/{{ cookiecutter.package_name }}/services/<service_name>/integration.py`
- **API router:** `src/{{ cookiecutter.package_name }}/services/<service_name>/api/router.py` with `router = APIRouter(...)`
- **Application code:** `application/` for use cases, `domain/` for entities/ports, `infrastructure/` for adapters

## Minimal Implementation Flow (Short)

1. Create a new directory: `src/{{ cookiecutter.package_name }}/services/<service_name>/`
2. Create `api/router.py` with an `APIRouter` (no connections on import).
3. Create `application/`, `domain/`, `infrastructure/` folders and write the initial implementation.
4. Write `integration.py` and export `register_service()` (see template below).
5. Write tests: `tests/test_*.py` (Unit and Router tests).
6. PR: Lint, Type-Checks, tests passing (green run).

## Template: Directory Structure

```text
src/{{ cookiecutter.package_name }}/services/<service_name>/
├── __init__.py
├── constants.py                    # Service-wide constants
├── patterns.py                     # Regex/Matching patterns (if needed)
├── integration.py                  # ← Mandatory: Entry point for the app loader
├── integration_test.py             # Smoke test: loads integration.py and checks register
├── smoke_imports_test.py           # Sanity check: are all modules importable?
├── README.md
│
├── api/
│   ├── __init__.py
│   ├── router.py                   # Aggregates all sub-routers
│   ├── dependencies.py             # FastAPI Depends providers
│   ├── error_handlers.py           # HTTPException mapping for this service
│   └── <resource>/                 # One package per REST resource
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
│   ├── service.py                  # Main Use-Case class (composed via mixins if needed)
│   ├── service_test.py
│   ├── _<entity>_mixin.py          # Mixin per entity (docmanager pattern, for many entities)
│   ├── _helpers.py
│   ├── _audit_mixin.py             # If audit trail is required
│   └── ports/                      # Abstract interfaces (protocols) for infrastructure
│       ├── __init__.py
│       └── <adapter_name>.py
│
├── domain/
│   ├── __init__.py
│   ├── exceptions.py
│   ├── ports.py                    # Alternative to application/ports/ for simple services
│   ├── entities/
│   │   └── __init__.py
│   └── value_objects/
│       ├── __init__.py
│       └── <name>.py
│
├── infrastructure/
│   ├── __init__.py
│   ├── providers.py                # DI-Wiring: creates concrete adapter instances
│   └── <adapter>.py                # Implementation of ports (DB, S3, external APIs)
│
├── models/
│   ├── __init__.py
│   └── base.py                     # SQLAlchemy ORM models
│
├── persistence/
│   ├── __init__.py
│   └── models.py                   # Alternative/supplementary location for persistence models
│
├── repositories/
│   ├── __init__.py
│   ├── <entity>_repository.py
│   ├── _<entity>_query.py          # Complex query logic extracted
│   ├── _<entity>_serialization.py  # DB→Domain mapping extracted
│   └── _<entity>_types.py          # Repository-internal types
│
├── schemas/
│   ├── __init__.py
│   ├── common.py                   # Shared schema parts
│   ├── request/
│   │   ├── __init__.py
│   │   └── <service_name>.py
│   └── response/
│       ├── __init__.py
│       └── <service_name>.py
│
├── errors/
│   ├── __init__.py
│   └── api.py                      # Domain Exceptions → HTTP errors
│
├── messages/
│   ├── messages.de.json
│   └── messages.en.json
│
├── contracts/                      # Only if other services consume this one
│   ├── __init__.py
│   └── schemas.py
│
└── tests/
    ├── e2e/
    │   └── <service_name>_workflow_e2e_test.py
    └── integration/
        └── <service_name>_api_integration_test.py

```

> **Always co-locate tests:** Unit tests should be `<module>_test.py` next to the source file. `tests/e2e/` and `tests/integration/` are strictly for higher-level tests.

---

## `integration.py`

```python
from {{ cookiecutter.package_name }}.core.core_extensions.loader import ServiceRegistration
from .api.router import router


async def startup(app):
    # Optional: Initialize clients, connections
    # app.state.my_client = await MyClient.connect()
    pass


async def shutdown(app, startup_result):
    # Optional: Shut down cleanly
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

---

## `api/router.py`

```python
from fastapi import APIRouter
from .example import create, get, list as list_, patch

router = APIRouter(prefix="/<service_name>", tags=["<ServiceName>"])

router.include_router(create.router)
router.include_router(get.router)
router.include_router(list_.router)
router.include_router(patch.router)

```

---

## `api/<resource>/create.py` (Example Verb)

```python
from fastapi import APIRouter, Depends, status
from {{ cookiecutter.package_name }}.services.<service_name>.api.dependencies import get_service
from {{ cookiecutter.package_name }}.services.<service_name>.schemas.request.<service_name> import <Entity>CreateRequest
from {{ cookiecutter.package_name }}.services.<service_name>.schemas.response.<service_name> import <Entity>Response
from {{ cookiecutter.package_name }}.services.<service_name>.application.service import <ServiceName>Service

router = APIRouter()

@router.post("/", response_model=<Entity>Response, status_code=status.HTTP_201_CREATED)
async def create_<entity>(
    body: <Entity>CreateRequest,
    svc: <ServiceName>Service = Depends(get_service),
) -> <Entity>Response:
    return await svc.create(body)

```

---

## `api/dependencies.py`

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from {{ cookiecutter.package_name }}.core.core_db.db_dependency import get_db
from {{ cookiecutter.package_name }}.services.<service_name>.application.service import <ServiceName>Service
from {{ cookiecutter.package_name }}.services.<service_name>.repositories.<entity>_repository import <Entity>Repository


def get_service(db: AsyncSession = Depends(get_db)) -> <ServiceName>Service:
    repo = <Entity>Repository(db)
    return <ServiceName>Service(repo)

```

---

## `application/service.py` — Mixin Pattern (docmanager)

For multiple entities: Compose the service out of mixins instead of building a monolith class.

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

---

## `application/ports/<adapter>.py`

```python
from abc import ABC, abstractmethod

class StoragePort(ABC):
    @abstractmethod
    async def save(self, key: str, data: bytes) -> None: ...

    @abstractmethod
    async def load(self, key: str) -> bytes: ...

```

Implementation resides in `infrastructure/<adapter>.py`, wiring in `infrastructure/providers.py`.

---

## `domain/exceptions.py`

```python
from {{ cookiecutter.package_name }}.shared.errors.exceptions import AppError

class <Entity>NotFoundError(AppError): ...
class <Entity>ConflictError(AppError): ...
class <Entity>ValidationError(AppError): ...

```

---

## `errors/api.py`

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from {{ cookiecutter.package_name }}.services.<service_name>.domain.exceptions import <Entity>NotFoundError

async def handle_not_found(request: Request, exc: <Entity>NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})

```

Register this in `integration.py`:

```python
from .errors.api import handle_not_found
from .domain.exceptions import <Entity>NotFoundError

# In the startup hook or directly inside register_service:
app.add_exception_handler(<Entity>NotFoundError, handle_not_found)

```

---

## `repositories/<entity>_repository.py`

If query logic is complex: extract it to `_<entity>_query.py`.

```python
from sqlalchemy.ext.asyncio import AsyncSession
from {{ cookiecutter.package_name }}.services.<service_name>.models.base import <Entity>


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

---

## `messages/messages.en.json`

### Example payload

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
from {{ cookiecutter.package_name }}.asgi import app

client = TestClient(app)

def test_create_<entity>():
    r = client.post("{{ cookiecutter.api_prefix }}/<service_name>/", json={...})
    assert r.status_code == 201

```

### Smoke Import Test (service root)

```python
# smoke_imports_test.py
def test_integration_importable():
    from {{ cookiecutter.package_name }}.services.<service_name> import integration
    assert hasattr(integration, "register_service")

```

---

## Local Development

```bash
uvicorn {{ cookiecutter.package_name }}.asgi:app --reload --host {{ cookiecutter.default_host }} --port {{ cookiecutter.dev_port }}
pytest src/{{ cookiecutter.package_name }}/services/<service_name>/ -q
pytest src/{{ cookiecutter.package_name }}/services/<service_name>/tests/ -q --tb=short

```

---

## Decision Guide

| Situation                           | Pattern                              |
| ----------------------------------- | ------------------------------------ |
| Simple service, 1 Entity            | Use `service.py` directly, no Mixins |
| Multiple entities, complex logic    | Mixin pattern (like `docmanager`)    |
| Complex query logic                 | Extract to `_<entity>_query.py`      |
| Other services consume this service | Create `contracts/schemas.py`        |
| Custom validation rules             | `validation/` Layer (like `docgen`)  |
| No persistence needed               | Omit `models/` and `repositories/`   |

---

## PR Checklist

- [ ] `integration.py` with `register_service()` → `ServiceRegistration`
- [ ] `smoke_imports_test.py` is present
- [ ] API: one package per resource, one file per HTTP verb
- [ ] No cross-service imports (only `core/` and `shared/`)
- [ ] Unit tests are co-located as `<module>_test.py`
- [ ] E2E/Integration tests are under `tests/e2e/` or `tests/integration/`
- [ ] `messages.de.json` + `messages.en.json` are present
- [ ] `schemas/request/` and `schemas/response/` are separated
- [ ] Domain exceptions are in `domain/exceptions.py`, HTTP mapping is in `errors/api.py`
- [ ] Alembic migration is created if new ORM models were added
- [ ] `__init__.py` in every package folder
- [ ] Type hints are complete, `ruff check .` is clean

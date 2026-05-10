---
name: backend
description: Architecture rules for this backend project. Use this skill whenever writing backend code, creating new services, adding tests, handling imports between services, or adjusting folder structures. Also applies to refactoring, new modules, migrations, or CI pipeline changes in the backend context.
---

# Backend Rules

## Project Structure

```
/workspace/backend/
├── tests/                        ← E2E / integration tests for core & shared ONLY
├── src/
│   ├── core/
│   │   └── core_auth/
│   │       ├── service.py
│   │       └── service_test.py   ← unit test co-located next to source
│   ├── shared/
│   └── app/
│       └── services/
│           ├── docgen/
│           │   ├── some_module.py
│           │   ├── some_module_test.py  ← unit test co-located
│           │   └── tests/              ← E2E / integration tests only
│           │       └── e2e/
│           └── docmanager/
│               ├── some_module.py
│               ├── some_module_test.py
│               └── tests/
│                   ├── e2e/
│                   └── integration/
```

---

## Rule 1: Service Isolation (strict)

Every service is a fully independent module.

**Allowed:**

- Imports from `core/` and `shared/`
- Own models, schemas, routers, utils within the service folder

**Forbidden:**

- Direct imports between services
- Shared state or shared DB models between services

```python
# ✅ OK
from app.core.database import get_db
from app.shared.utils import paginate

# ❌ FORBIDDEN
from app.services.docgen.models import Document  # inside docmanager
```

**Goal:** If Service A is deleted, Service B continues to work without any code changes.
If logic is needed in multiple services → extract it into `core/` or `shared/`, never duplicate or cross-import.

---

## Rule 2: Test Structure

Three-tier pattern — pick the right tier:

| Tier                            | Pattern                                             | Where                              |
| ------------------------------- | --------------------------------------------------- | ---------------------------------- |
| Unit tests                      | `module_test.py` co-located next to source          | same folder as the file under test |
| E2E / Integration (service)     | `test_*.py` in `tests/e2e/` or `tests/integration/` | inside service folder              |
| E2E / Integration (core/shared) | `test_*.py`                                         | `/workspace/backend/tests/`        |

```
# ✅ Correct

# Unit test — co-located
src/app/services/docgen/application/orchestrator.py
src/app/services/docgen/application/orchestrator_test.py

# E2E — inside service tests folder
src/app/services/docgen/tests/e2e/test_builddoc_file.py
src/app/services/docmanager/tests/e2e/test_workflow.py
src/app/services/docmanager/tests/integration/test_api.py

# Core/shared E2E
tests/e2e/test_core.py

# ❌ Wrong
tests/e2e/test_docgen_orchestrator.py   ← service test in root tests/
src/app/services/docgen/tests/test_orchestrator.py  ← unit test should be co-located
```

**Never** place service-specific tests in `/workspace/backend/tests/`.

---

## Rule 3: Creating a New Service

Checklist:

- [ ] Own folder under `src/app/services/<n>/`
- [ ] Unit tests co-located as `<module>_test.py` next to each file
- [ ] Own `tests/e2e/` and/or `tests/integration/` for higher-level tests
- [ ] No imports from other service folders
- [ ] Shared logic extracted to `core/` or `shared/`, never duplicated
- [ ] Service registered in the app router, not directly coupled to other services

---

## Rule 4: core/ vs shared/

| `core/`                  | `shared/`                     |
| ------------------------ | ----------------------------- |
| DB session, Base models  | Pagination, Response wrappers |
| Auth / JWT / Permissions | Custom exceptions             |
| Config / Settings        | Validators, Helpers           |
| Logging setup            | Mixins                        |

Rule of thumb: `core/` = infrastructure, `shared/` = utilities without business logic.

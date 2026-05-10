from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter

DEFAULT_TEMPLATES_DIR = Path(__file__).resolve().parents[4] / "templates"
TEMPLATES_DIR = Path(os.environ.get("TEMPLATES_DIR", DEFAULT_TEMPLATES_DIR))

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", summary="List available template assets")
def list_templates() -> dict[str, object]:
    if not TEMPLATES_DIR.exists():
        return {"path": str(TEMPLATES_DIR), "templates": []}

    templates = sorted(path.name for path in TEMPLATES_DIR.iterdir())
    return {"path": str(TEMPLATES_DIR), "templates": templates}
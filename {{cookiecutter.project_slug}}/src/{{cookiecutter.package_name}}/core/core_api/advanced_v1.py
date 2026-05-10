from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/advanced", tags=["advanced"])


@router.get("/version", summary="Return a simple version payload")
def version() -> dict[str, str]:
    return {"version": "0.1.0"}


@router.get("/features", summary="Describe included template features")
def features() -> dict[str, list[str]]:
    return {
        "features": [
            "cookiecutter-ready",
            "src-layout",
            "vscode-config",
            "devcontainer-config",
        ]
    }
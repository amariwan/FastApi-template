from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["public"])


@router.get("/", summary="Template landing endpoint")
def read_root() -> dict[str, str]:
    return {"message": "Welcome to {{ cookiecutter.app_title }}"}


@router.get("/public/ping", summary="Simple public ping endpoint")
def ping() -> dict[str, str]:
    return {"status": "ok"}


def register_public_subrouter(subrouter: APIRouter) -> None:
    router.include_router(subrouter)
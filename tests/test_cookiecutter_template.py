from __future__ import annotations

import re
from pathlib import Path

import pytest
from cookiecutter.exceptions import FailedHookException
from cookiecutter.main import cookiecutter

REPO_ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".py", ".toml", ".ini", ".md", ".json", ".yml", ".yaml", ".txt"}
TEXT_NAMES = {"Dockerfile", "Justfile", ".gitignore", ".dockerignore", ".env.example"}
STALE_PATTERNS = (
    re.compile(r"(?m)^\s*from app(?=[.\s])"),
    re.compile(r"(?m)^\s*import app(?=[.\s]|$)"),
    re.compile(r"src/app"),
    re.compile(r"src\.app"),
    re.compile(r"Template Project"),
)


def render_template(tmp_path: Path, **extra_context: str) -> Path:
    rendered = cookiecutter(
        str(REPO_ROOT),
        no_input=True,
        output_dir=str(tmp_path),
        extra_context=extra_context,
    )
    return Path(rendered)


def iter_text_files(project_root: Path):
    for path in project_root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix in TEXT_SUFFIXES or path.name in TEXT_NAMES:
            yield path


def stale_references(project_root: Path) -> list[tuple[str, str]]:
    hits: list[tuple[str, str]] = []
    for path in iter_text_files(project_root):
        text = path.read_text(encoding="utf-8")
        for pattern in STALE_PATTERNS:
            if pattern.search(text):
                hits.append((path.relative_to(project_root).as_posix(), pattern.pattern))
    return hits


def test_renders_default_project_structure(tmp_path: Path) -> None:
    project = render_template(tmp_path)

    assert project.name == "fastapi-cookiecutter-app"
    assert (project / ".env").exists()
    assert (project / "src" / "fastapi_cookiecutter_app" / "asgi.py").exists()
    assert (project / ".vscode" / "launch.json").exists()
    assert (project / ".devcontainer" / "devcontainer.json").exists()
    assert not (project / ".claude").exists()
    assert not (project / "uv.lock").exists()

    dockerfile = (project / "Dockerfile").read_text(encoding="utf-8")
    assert "fastapi_cookiecutter_app.asgi:app" in dockerfile


def test_renders_custom_package_name_without_stale_app_references(tmp_path: Path) -> None:
    project = render_template(
        tmp_path,
        project_name="Acme Platform API",
        project_slug="acme-platform-api",
        package_name="platform_api",
        app_title="Acme Platform API",
        default_host="127.0.0.1",
        dev_port="5055",
        prod_host="127.0.0.1",
        prod_port="9090",
        api_prefix="/internal",
        default_log_level="DEBUG",
        default_test_mode="true",
        default_profiling_enabled="true",
        default_cors_allowed_origins="https://example.com",
        default_cors_allow_methods="GET,POST,PATCH",
        default_cors_allow_headers="Authorization,Content-Type",
        default_auth_mode="hs",
        default_auth_algorithms="HS256,RS256",
        auth_validate_signature="false",
        auth_verify_signature="false",
        auth_verify_exp="false",
        auth_verify_iss="false",
        auth_verify_aud="false",
        auth_disable_ssl_verify="true",
        auth_clock_skew_secs="120",
        db_enabled="true",
        db_host="db.internal",
        db_port="15432",
        db_username="acme",
        db_database="acme_api",
        db_engine_echo="true",
        db_auto_create_tables="true",
        db_pool_size="12",
        db_max_overflow="24",
        db_pool_recycle="3600",
        db_pool_pre_ping="false",
        db_probe_timeout_seconds="4.5",
        s3_probe_timeout_seconds="8.0",
        role_active="false",
        role_prefix="acme:",
        role_read_roles="viewer",
        role_write_roles="editor",
        role_delete_roles="moderator",
        role_admin_roles="owner",
        role_hierarchy="owner>editor>viewer",
        default_storage_backend="filesystem",
        s3_secure="false",
        s3_addressing_style="path",
        filesystem_root="/srv/data",
        include_vscode="no",
        include_devcontainer="no",
        create_dotenv_file="no",
    )

    assert project.name == "acme-platform-api"
    assert (project / "src" / "platform_api" / "asgi.py").exists()
    assert not (project / "src" / "app").exists()
    assert not (project / ".vscode").exists()
    assert not (project / ".devcontainer").exists()
    assert not (project / ".env").exists()

    justfile = (project / "Justfile").read_text(encoding="utf-8")
    dockerfile = (project / "Dockerfile").read_text(encoding="utf-8")
    env_example = (project / ".env.example").read_text(encoding="utf-8")
    config_file = (project / "src" / "platform_api" / "config.py").read_text(encoding="utf-8")
    auth_settings = (project / "src" / "platform_api" / "core" / "core_auth" / "settings.py").read_text(encoding="utf-8")
    storage_settings = (project / "src" / "platform_api" / "core" / "core_storage" / "settings.py").read_text(encoding="utf-8")
    service_guide = (project / "src" / "platform_api" / "services" / "README.md").read_text(encoding="utf-8")
    test_file = (project / "tests" / "unit" / "test_public_registration.py").read_text(encoding="utf-8")

    assert 'HOST := env("HOST", "127.0.0.1")' in justfile
    assert 'PORT := env("PORT", "5055")' in justfile
    assert 'PROD_HOST := env("PROD_HOST", "127.0.0.1")' in justfile
    assert 'PROD_PORT := env("PROD_PORT", "9090")' in justfile
    assert 'platform_api.asgi:app' in justfile
    assert '"--host", "127.0.0.1", "--port", "9090"' in dockerfile
    assert 'LOG_LEVEL=DEBUG' in env_example
    assert 'API_PREFIX=/internal' in env_example
    assert 'CORS_ALLOWED_ORIGINS=https://example.com' in env_example
    assert 'AUTH_MODE=hs' in env_example
    assert 'AUTH_ALGORITHMS=HS256,RS256' in env_example
    assert 'DB_IP=db.internal' in env_example
    assert 'DB_PORT=15432' in env_example
    assert 'DB_DATABASE=acme_api' in env_example
    assert 'ROLE_PREFIX=acme:' in env_example
    assert 'ROLE_ADMIN_ROLES=owner' in env_example
    assert 'STORAGE_BACKEND=filesystem' in env_example
    assert 'FILESYSTEM_ROOT=/srv/data' in env_example
    assert 'SECRET_KEY=devsecret' in env_example
    assert 'LogLevel("DEBUG")' in config_file
    assert 'API_PREFIX: str = "/internal"' in config_file
    assert 'DB_IP: str = "db.internal"' in config_file
    assert 'MODE: StrictStr = Field(default="hs"' in auth_settings
    assert '_template_bool("false")' in auth_settings
    assert 'StorageBackend("filesystem")' in storage_settings
    assert 'FILESYSTEM_ROOT: str = "/srv/data"' in storage_settings
    assert 'src/platform_api/services/<service_name>/' in service_guide
    assert '{{ cookiecutter.api_prefix }}/<service_name>/' not in service_guide
    assert '/internal/<service_name>/' in service_guide
    assert '--host 127.0.0.1 --port 5055' in service_guide
    assert 'importlib.import_module("platform_api.core.core_api.public_v1")' in test_file
    assert stale_references(project) == []


@pytest.mark.parametrize(
    "extra_context",
    [
        {"project_slug": "Invalid Slug", "package_name": "valid_name"},
        {"project_slug": "valid-slug", "package_name": "invalid-name"},
        {"project_slug": "valid-slug", "package_name": "valid_name", "python_version": "3.10"},
    ],
)
def test_pre_gen_hook_rejects_invalid_values(tmp_path: Path, extra_context: dict[str, str]) -> None:
    with pytest.raises(FailedHookException):
        render_template(tmp_path, **extra_context)
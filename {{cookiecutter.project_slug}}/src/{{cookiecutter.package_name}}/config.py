from __future__ import annotations

from collections.abc import Iterable
from enum import Enum
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _env_files() -> tuple[str, ...]:
    return (".env", ".dev.env")


def _parse_list(value: object, *, fallback: list[str] | None = None) -> list[str]:
    if value in (None, ""):
        return list(fallback or [])
    if isinstance(value, str):
        return [item.strip() for item in value.replace(";", ",").split(",") if item.strip()]
    if isinstance(value, Iterable):
        return [str(item).strip() for item in value if str(item).strip()]
    raise TypeError("Expected a string or iterable of strings")


def _parse_bool_default(value: str) -> bool:
    return value.strip().lower() == "true"


def _parse_int_default(value: str) -> int:
    return int(value.strip())


def _parse_float_default(value: str) -> float:
    return float(value.strip())


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class AppSettings(BaseSettings):
    LOG_LEVEL: LogLevel = LogLevel("{{ cookiecutter.default_log_level }}")
    TEST_MODE: bool = Field(default_factory=lambda: _parse_bool_default("{{ cookiecutter.default_test_mode }}"))
    PROFILING_ENABLED: bool = Field(default_factory=lambda: _parse_bool_default("{{ cookiecutter.default_profiling_enabled }}"))
    APP_TITLE: str = "{{ cookiecutter.app_title }}"
    API_PREFIX: str = "{{ cookiecutter.api_prefix }}"
    AUTH_MODE: str = "{{ cookiecutter.default_auth_mode }}"
    auth_algorithms: list[str] = Field(
        default_factory=lambda: _parse_list("{{ cookiecutter.default_auth_algorithms }}", fallback=["RS256"]),
        validation_alias="AUTH_ALGORITHMS",
    )
    cors_allowed_origins: list[str] = Field(
        default_factory=lambda: _parse_list("{{ cookiecutter.default_cors_allowed_origins }}"),
        validation_alias="CORS_ALLOWED_ORIGINS",
    )
    cors_allow_methods: list[str] = Field(
        default_factory=lambda: _parse_list("{{ cookiecutter.default_cors_allow_methods }}", fallback=["*"]),
        validation_alias="CORS_ALLOW_METHODS",
    )
    cors_allow_headers: list[str] = Field(
        default_factory=lambda: _parse_list("{{ cookiecutter.default_cors_allow_headers }}", fallback=["*"]),
        validation_alias="CORS_ALLOW_HEADERS",
    )
    DB_PROBE_TIMEOUT_SECONDS: float = Field(default_factory=lambda: _parse_float_default("{{ cookiecutter.db_probe_timeout_seconds }}"))
    S3_PROBE_TIMEOUT_SECONDS: float = Field(default_factory=lambda: _parse_float_default("{{ cookiecutter.s3_probe_timeout_seconds }}"))

    model_config = SettingsConfigDict(env_file=_env_files(), case_sensitive=False, extra="ignore")

    @field_validator(
        "auth_algorithms",
        "cors_allowed_origins",
        "cors_allow_methods",
        "cors_allow_headers",
        mode="before",
    )
    @classmethod
    def _parse_string_lists(cls, value: object) -> list[str]:
        return _parse_list(value)


class DbSettings(BaseSettings):
    DB_ENABLED: bool = Field(default_factory=lambda: _parse_bool_default("{{ cookiecutter.db_enabled }}"))
    DB_PORT: int = Field(default_factory=lambda: _parse_int_default("{{ cookiecutter.db_port }}"))
    DB_USERNAME: str = "{{ cookiecutter.db_username }}"
    DB_PASSWORD: str = "{{ cookiecutter.db_password }}"
    DB_DATABASE: str = "{{ cookiecutter.db_database }}"
    DB_IP: str = "{{ cookiecutter.db_host }}"
    DB_ENGINE_ECHO: bool = Field(default_factory=lambda: _parse_bool_default("{{ cookiecutter.db_engine_echo }}"))
    DB_AUTO_CREATE_TABLES: bool = Field(default_factory=lambda: _parse_bool_default("{{ cookiecutter.db_auto_create_tables }}"))
    DB_POOL_SIZE: int = Field(default_factory=lambda: _parse_int_default("{{ cookiecutter.db_pool_size }}"))
    DB_MAX_OVERFLOW: int = Field(default_factory=lambda: _parse_int_default("{{ cookiecutter.db_max_overflow }}"))
    DB_POOL_RECYCLE: int = Field(default_factory=lambda: _parse_int_default("{{ cookiecutter.db_pool_recycle }}"))
    DB_POOL_PRE_PING: bool = Field(default_factory=lambda: _parse_bool_default("{{ cookiecutter.db_pool_pre_ping }}"))

    model_config = SettingsConfigDict(env_file=_env_files(), case_sensitive=False, extra="ignore")


@lru_cache(maxsize=1)
def get_app_settings() -> AppSettings:
    return AppSettings()


@lru_cache(maxsize=1)
def get_db_settings() -> DbSettings:
    return DbSettings()


def reload_app_settings() -> AppSettings:
    get_app_settings.cache_clear()
    return get_app_settings()


def reload_db_settings() -> DbSettings:
    get_db_settings.cache_clear()
    return get_db_settings()

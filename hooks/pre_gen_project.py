from __future__ import annotations

import keyword
import re
import sys

PROJECT_SLUG = "{{ cookiecutter.project_slug }}"
PACKAGE_NAME = "{{ cookiecutter.package_name }}"
PYTHON_VERSION = "{{ cookiecutter.python_version }}"
APP_TITLE = "{{ cookiecutter.app_title }}"
API_PREFIX = "{{ cookiecutter.api_prefix }}"
DEFAULT_HOST = "{{ cookiecutter.default_host }}"
PROD_HOST = "{{ cookiecutter.prod_host }}"
DB_DATABASE = "{{ cookiecutter.db_database }}"
DEFAULT_AUTH_ALGORITHMS = "{{ cookiecutter.default_auth_algorithms }}"

BOOLEAN_FIELDS = {
    "default_test_mode": "{{ cookiecutter.default_test_mode }}",
    "default_profiling_enabled": "{{ cookiecutter.default_profiling_enabled }}",
    "auth_validate_signature": "{{ cookiecutter.auth_validate_signature }}",
    "auth_verify_signature": "{{ cookiecutter.auth_verify_signature }}",
    "auth_verify_exp": "{{ cookiecutter.auth_verify_exp }}",
    "auth_verify_iss": "{{ cookiecutter.auth_verify_iss }}",
    "auth_verify_aud": "{{ cookiecutter.auth_verify_aud }}",
    "auth_disable_ssl_verify": "{{ cookiecutter.auth_disable_ssl_verify }}",
    "db_enabled": "{{ cookiecutter.db_enabled }}",
    "db_engine_echo": "{{ cookiecutter.db_engine_echo }}",
    "db_auto_create_tables": "{{ cookiecutter.db_auto_create_tables }}",
    "db_pool_pre_ping": "{{ cookiecutter.db_pool_pre_ping }}",
    "role_active": "{{ cookiecutter.role_active }}",
    "s3_secure": "{{ cookiecutter.s3_secure }}",
}

YES_NO_FIELDS = {
    "include_vscode": "{{ cookiecutter.include_vscode }}",
    "include_devcontainer": "{{ cookiecutter.include_devcontainer }}",
    "create_dotenv_file": "{{ cookiecutter.create_dotenv_file }}",
}

PORT_FIELDS = {
    "dev_port": "{{ cookiecutter.dev_port }}",
    "prod_port": "{{ cookiecutter.prod_port }}",
    "db_port": "{{ cookiecutter.db_port }}",
}

INTEGER_FIELDS = {
    "auth_clock_skew_secs": "{{ cookiecutter.auth_clock_skew_secs }}",
    "db_pool_size": "{{ cookiecutter.db_pool_size }}",
    "db_max_overflow": "{{ cookiecutter.db_max_overflow }}",
    "db_pool_recycle": "{{ cookiecutter.db_pool_recycle }}",
}

FLOAT_FIELDS = {
    "db_probe_timeout_seconds": "{{ cookiecutter.db_probe_timeout_seconds }}",
    "s3_probe_timeout_seconds": "{{ cookiecutter.s3_probe_timeout_seconds }}",
}

PROJECT_SLUG_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
PYTHON_VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)$")


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def validate_project_slug() -> None:
    if not PROJECT_SLUG_PATTERN.fullmatch(PROJECT_SLUG):
        fail(
            "project_slug must contain only lowercase letters, numbers, and hyphens, "
            "and must start/end with an alphanumeric character."
        )


def validate_package_name() -> None:
    if not PACKAGE_NAME.isidentifier():
        fail("package_name must be a valid Python identifier.")
    if "-" in PACKAGE_NAME:
        fail("package_name must not contain hyphens.")
    if keyword.iskeyword(PACKAGE_NAME):
        fail("package_name must not be a Python keyword.")


def validate_python_version() -> None:
    match = PYTHON_VERSION_PATTERN.fullmatch(PYTHON_VERSION)
    if match is None:
        fail("python_version must use 'major.minor' format, for example '3.13'.")

    assert match is not None
    major = int(match.group(1))
    minor = int(match.group(2))
    if major != 3 or minor < 12:
        fail("python_version must be Python 3.12 or newer for this template.")


def _parse_int(field_name: str, value: str) -> int:
    try:
        return int(value)
    except ValueError as err:
        fail(f"{field_name} must be an integer.")
        raise AssertionError from err


def _parse_float(field_name: str, value: str) -> float:
    try:
        return float(value)
    except ValueError as err:
        fail(f"{field_name} must be a number.")
        raise AssertionError from err


def validate_non_empty_strings() -> None:
    for field_name, value in {
        "app_title": APP_TITLE,
        "default_host": DEFAULT_HOST,
        "prod_host": PROD_HOST,
        "db_database": DB_DATABASE,
    }.items():
        if not value.strip():
            fail(f"{field_name} must not be empty.")


def validate_api_prefix() -> None:
    if API_PREFIX and not API_PREFIX.startswith("/"):
        fail("api_prefix must start with '/'.")


def validate_boolean_fields() -> None:
    allowed = {"true", "false"}
    for field_name, value in BOOLEAN_FIELDS.items():
        if value not in allowed:
            fail(f"{field_name} must be one of: true, false.")


def validate_yes_no_fields() -> None:
    allowed = {"yes", "no"}
    for field_name, value in YES_NO_FIELDS.items():
        if value not in allowed:
            fail(f"{field_name} must be one of: yes, no.")


def validate_ports() -> None:
    for field_name, value in PORT_FIELDS.items():
        parsed = _parse_int(field_name, value)
        if not 1 <= parsed <= 65535:
            fail(f"{field_name} must be between 1 and 65535.")


def validate_integers() -> None:
    for field_name, value in INTEGER_FIELDS.items():
        parsed = _parse_int(field_name, value)
        if parsed < 0:
            fail(f"{field_name} must be zero or greater.")

    if _parse_int("db_pool_size", INTEGER_FIELDS["db_pool_size"]) < 1:
        fail("db_pool_size must be at least 1.")


def validate_floats() -> None:
    for field_name, value in FLOAT_FIELDS.items():
        parsed = _parse_float(field_name, value)
        if parsed <= 0:
            fail(f"{field_name} must be greater than 0.")


def validate_auth_algorithms() -> None:
    entries = [entry.strip() for entry in DEFAULT_AUTH_ALGORITHMS.replace(";", ",").split(",") if entry.strip()]
    if not entries:
        fail("default_auth_algorithms must contain at least one algorithm.")


if __name__ == "__main__":
    validate_project_slug()
    validate_package_name()
    validate_python_version()
    validate_non_empty_strings()
    validate_api_prefix()
    validate_boolean_fields()
    validate_yes_no_fields()
    validate_ports()
    validate_integers()
    validate_floats()
    validate_auth_algorithms()
    sys.exit(0)

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
}

INTEGER_FIELDS = {
    "auth_clock_skew_secs": "{{ cookiecutter.auth_clock_skew_secs }}",
}

FLOAT_FIELDS = {
    "db_probe_timeout_seconds": "{{ cookiecutter.db_probe_timeout_seconds }}",
    "s3_probe_timeout_seconds": "{{ cookiecutter.s3_probe_timeout_seconds }}",
}

# Optional DB fields (may be absent from cookiecutter.json; use get() so extra_context can still provide values)
DB_HOST = "{{ cookiecutter.get('db_host', '') }}"
DB_PORT = "{{ cookiecutter.get('db_port', '') }}"
DB_USERNAME = "{{ cookiecutter.get('db_username', '') }}"
DB_PASSWORD = "{{ cookiecutter.get('db_password', '') }}"
DB_ENGINE_ECHO = "{{ cookiecutter.get('db_engine_echo', '') }}"
DB_AUTO_CREATE_TABLES = "{{ cookiecutter.get('db_auto_create_tables', '') }}"
DB_POOL_SIZE = "{{ cookiecutter.get('db_pool_size', '') }}"
DB_MAX_OVERFLOW = "{{ cookiecutter.get('db_max_overflow', '') }}"
DB_POOL_RECYCLE = "{{ cookiecutter.get('db_pool_recycle', '') }}"
DB_POOL_PRE_PING = "{{ cookiecutter.get('db_pool_pre_ping', '') }}"

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
    


def validate_floats() -> None:
    for field_name, value in FLOAT_FIELDS.items():
        parsed = _parse_float(field_name, value)
        if parsed <= 0:
            fail(f"{field_name} must be greater than 0.")


def validate_auth_algorithms() -> None:
    entries = [entry.strip() for entry in DEFAULT_AUTH_ALGORITHMS.replace(";", ",").split(",") if entry.strip()]
    if not entries:
        fail("default_auth_algorithms must contain at least one algorithm.")


def _input_default(prompt: str, default: str) -> str:
    try:
        value = input(f"{prompt} [{default}]: ").strip()
    except (EOFError, KeyboardInterrupt):
        value = ""
    return value or default


def _prompt_db_and_replace_placeholders() -> None:
    """Prompt for optional DB settings (only if DB_ENABLED=true) and replace cookiecutter placeholders
    in template files so they won't be asked when DB is disabled.
    """
    from pathlib import Path

    template_root = Path(__file__).resolve().parents[1]

    db_keys = [
        "db_host",
        "db_port",
        "db_username",
        "db_password",
        "db_database",
        "db_engine_echo",
        "db_auto_create_tables",
        "db_pool_size",
        "db_max_overflow",
        "db_pool_recycle",
        "db_pool_pre_ping",
    ]

    final: dict[str, str] = {}
    if "db_enabled" in BOOLEAN_FIELDS and BOOLEAN_FIELDS["db_enabled"] == "true":
        # Use values provided via extra_context (rendered into DB_* constants) if present,
        # otherwise interactively ask the user for the value.
        final["db_host"] = DB_HOST or _input_default("Database host (DB_IP)", "localhost")
        final["db_port"] = DB_PORT or _input_default("Database port (DB_PORT)", "5432")
        final["db_username"] = DB_USERNAME or _input_default("Database username (DB_USERNAME)", "postgres")
        final["db_password"] = DB_PASSWORD or _input_default("Database password (DB_PASSWORD)", "postgres")
        final["db_database"] = DB_DATABASE or _input_default("Database name (DB_DATABASE)", f"{PACKAGE_NAME}_db")
        final["db_engine_echo"] = DB_ENGINE_ECHO or _input_default("DB engine echo (db_engine_echo)", "false")
        final["db_auto_create_tables"] = DB_AUTO_CREATE_TABLES or _input_default("DB auto create tables (db_auto_create_tables)", "false")
        final["db_pool_size"] = DB_POOL_SIZE or _input_default("DB pool size (db_pool_size)", "5")
        final["db_max_overflow"] = DB_MAX_OVERFLOW or _input_default("DB max overflow (db_max_overflow)", "10")
        final["db_pool_recycle"] = DB_POOL_RECYCLE or _input_default("DB pool recycle (db_pool_recycle)", "1800")
        final["db_pool_pre_ping"] = DB_POOL_PRE_PING or _input_default("DB pool pre-ping (db_pool_pre_ping)", "true")
    else:
        for k in db_keys:
            final[k] = ""

    # Build placeholder patterns and replace across template files (skip hooks/ and binary files)
    patterns: list[tuple[str, str]] = []
    for k, v in final.items():
        patterns.append((f"{{{{ cookiecutter.{k} }}}}", v))
        patterns.append((f"{{{{ cookiecutter.get('{k}', '') }}}}", v))
        patterns.append((f'{{{{ cookiecutter.get("{k}", "") }}}}', v))

    binary_exts = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".zip", ".tar", ".gz", ".whl", ".egg"}

    for path in template_root.rglob("*"):
        if not path.is_file():
            continue
        if "hooks" in path.parts:
            continue
        if path.suffix.lower() in binary_exts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        new_text = text
        for pat, val in patterns:
            if pat in new_text:
                new_text = new_text.replace(pat, val)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")


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
    # If DB is enabled, prompt for DB details (only when not provided via extra_context) and
    # replace any cookiecutter DB placeholders in the template so users who chose not to
    # include a DB won't be asked about DB host/credentials later.
    try:
        _prompt_db_and_replace_placeholders()
    except Exception:
        # Never fail generation because of non-critical hook issues; show a warning instead.
        print("WARNING: failed to run optional DB placeholder replacement hook")
    sys.exit(0)

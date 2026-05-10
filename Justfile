set shell := ["bash", "-euo", "pipefail", "-c"]

@default:
    just --list

test:
    uv run pytest

render-default out_dir=".rendered":
    rm -rf {{out_dir}}/default
    uv run cookiecutter . --no-input --output-dir {{out_dir}} project_name="FastAPI Cookiecutter App" project_slug="fastapi-cookiecutter-app" package_name="fastapi_cookiecutter_app" app_title="FastAPI Cookiecutter App"

render-custom out_dir=".rendered":
    rm -rf {{out_dir}}/custom
    uv run cookiecutter . --no-input --output-dir {{out_dir}} project_name="Acme Platform API" project_slug="acme-platform-api" package_name="platform_api" app_title="Acme Platform API" default_host="127.0.0.1" dev_port="5055" prod_host="127.0.0.1" prod_port="9090" api_prefix="/internal" default_log_level="DEBUG" default_auth_mode="hs" default_auth_algorithms="HS256,RS256" db_enabled="true" db_host="db.internal" db_port="15432" db_username="acme" db_password="secret" db_database="acme_api" db_engine_echo="true" db_auto_create_tables="true" db_pool_size="12" db_max_overflow="24" db_pool_recycle="3600" db_pool_pre_ping="false" db_probe_timeout_seconds="4.5" s3_probe_timeout_seconds="8.0" role_active="false" role_prefix="acme:" role_read_roles="viewer" role_write_roles="editor" role_delete_roles="moderator" role_admin_roles="owner" role_hierarchy="owner>editor>viewer" default_storage_backend="filesystem" s3_secure="false" s3_addressing_style="path" filesystem_root="/srv/data" include_vscode="no" include_devcontainer="no" create_dotenv_file="no"

clean:
    rm -rf .rendered .pytest_cache .ruff_cache .mypy_cache .venv

# FastAPI Cookiecutter Template

This repository is a **Cookiecutter template** for bootstrapping a FastAPI project with a `src/` layout, a configurable Python import root, VS Code/devcontainer support, and the existing core helpers from this scaffold.

## Quick start

1. Install Cookiecutter (or just use `uv`).
2. Render the template.
3. Enter the generated project and sync dependencies.

The post-generation hook automatically creates a local `.env` from `.env.example` using safe placeholder values, so the rendered project is ready to boot without a manual copy step.

### Render from the local checkout

```text
uv run cookiecutter .
```

### Render from a Git URL

```text
cookiecutter <your-git-url>
```

## Template variables

- Core identity:
  - `project_name`
  - `project_slug`
  - `package_name`
  - `project_description`
  - `author_name`
  - `python_version`
  - `app_title`
- Runtime defaults:
  - `default_host`, `dev_port`, `prod_host`, `prod_port`
  - `api_prefix`, `default_log_level`, `default_test_mode`, `default_profiling_enabled`
  - `default_cors_allowed_origins`, `default_cors_allow_methods`, `default_cors_allow_headers`
- Auth / roles:
  - `default_auth_mode`, `default_auth_algorithms`
  - `auth_validate_signature`, `auth_verify_signature`, `auth_verify_exp`, `auth_verify_iss`, `auth_verify_aud`, `auth_disable_ssl_verify`, `auth_clock_skew_secs`
  - `role_active`, `role_prefix`, `role_read_roles`, `role_write_roles`, `role_delete_roles`, `role_admin_roles`, `role_hierarchy`
- Database / storage:
  - `db_enabled`, `db_host`, `db_port`, `db_username`, `db_password`, `db_database`
  - `db_engine_echo`, `db_auto_create_tables`, `db_pool_size`, `db_max_overflow`, `db_pool_recycle`, `db_pool_pre_ping`
  - `db_probe_timeout_seconds`, `s3_probe_timeout_seconds`
  - `default_storage_backend`, `s3_secure`, `s3_addressing_style`, `filesystem_root`
- Generated assets:
  - `include_vscode`, `include_devcontainer`, `create_dotenv_file`
  - `devcontainer_node_version`, `devcontainer_postgres_image`
  - `dev_secret_key`

If you want to tweak absolutely every generated default, start with `cookiecutter.json` — the template now exposes the main runtime, auth, database, storage, Docker, VS Code, and devcontainer defaults there.

## What gets generated

The rendered project lives under:

```text
{{cookiecutter.project_slug}}/
```

Inside that generated project, the Python package root is:

```text
src/{{cookiecutter.package_name}}/
```

## Repository decisions baked into this conversion

- `.claude/` stays at the **template repo root only** and is **not** included in generated projects.
- `.vscode/` and `.devcontainer/` can be included or omitted per render.
- `uv.lock` is intentionally **not** shipped in generated projects.
- The root of this repository now contains **template-maintenance** files only.

## Maintenance workflow

Install the maintainer dependencies:

```text
uv sync
```

Run the template smoke tests:

```text
uv run pytest
```

Or use the lightweight helper tasks:

```text
just test
just render-default
just render-custom
```

## Layout

- `cookiecutter.json` — template variables and defaults.
- `hooks/` — pre/post generation hooks.
- `tests/` — template smoke tests.
- `{{cookiecutter.project_slug}}/` — the generated project scaffold.

## Notes

- The generated project includes a project README with rendered values.
- The generated project’s import root is fully parameterized; this template does **not** assume `app` anymore.
- The generated project also includes a starter `.env`, created automatically from `.env.example`.
- The Docker and Justfile entrypoints were normalized to the `src/{{cookiecutter.package_name}}` layout.
- `.vscode/` and `.devcontainer/` can now be included or omitted via Cookiecutter switches.

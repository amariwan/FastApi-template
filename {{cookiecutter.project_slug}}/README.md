# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## Quick start

1. Sync dependencies. {% if cookiecutter.create_dotenv_file == "yes" -%}
1. Review the generated `.env` placeholders if needed. {% else -%}
1. Optionally copy `.env.example` to `.env` and adjust it. {% endif -%}
1. Start the development server.

```text
{% if cookiecutter.create_dotenv_file == "no" -%}
cp .env.example .env
{% endif -%}
uv sync
just dev
```

Default development bind: `{{ cookiecutter.default_host }}:{{ cookiecutter.dev_port }}`. Default production bind: `{{ cookiecutter.prod_host }}:{{ cookiecutter.prod_port }}`. Global API prefix: `{{ cookiecutter.api_prefix }}`.

{% if cookiecutter.create_dotenv_file == "yes" -%} The template creates `.env` automatically from `.env.example` during generation. {% endif -%}

The ASGI entrypoint lives at `src/{{ cookiecutter.package_name }}/asgi.py` and the import path is `{{ cookiecutter.package_name }}.asgi:app`.

## Included tooling

- `Justfile` for common dev/test/lint commands. {% if cookiecutter.include_vscode == "yes" -%}
- `.vscode/` launch/tasks/settings for local development. {% endif -%} {% if cookiecutter.include_devcontainer == "yes" -%}
- `.devcontainer/` for containerized development. {% endif -%}
- `Dockerfile` for a simple production image.

## Project layout

```text
src/{{ cookiecutter.package_name }}/
tests/
```

## Useful commands

```text
just dev
just test
just lint
just check
```

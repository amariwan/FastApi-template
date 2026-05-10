# FastAPI Cookiecutter

A modern, production-ready [Cookiecutter](https://github.com/cookiecutter/cookiecutter) template for building configurable FastAPI services with a `src/` layout, typed settings, optional VS Code/devcontainer scaffolding, and render-time control over nearly every default.

## ✨ Features

### Backend (FastAPI)

- **Modern FastAPI Setup**: FastAPI-based service scaffold with ASGI entrypoint and clean `src/` package layout
- **Typed Configuration**: Central Pydantic Settings for app, auth, roles, database, and storage
- **Built-in Core APIs**: Public, templates, configuration, and advanced endpoints included out of the box
- **Authentication Foundation**: JWT/JWKS or shared-secret auth modes with configurable verification flags
- **Role & Permission Defaults**: Render role prefixes, role groups, and inheritance hierarchy directly from Cookiecutter prompts
- **Database-Ready Core**: Async SQLAlchemy-oriented database foundation with configurable pool and probe defaults
- **Storage Abstraction**: S3 or filesystem backends with generated runtime configuration
- **Service-Oriented Structure**: Generated service guide and `services/` layout for modular feature packages

### Developer Experience

- **uv + just**: Fast dependency management and ergonomic day-to-day commands
- **Code Quality**: Ruff, mypy, pyright, and pytest wiring included
- **Optional VS Code Setup**: Launch configs, tasks, and editor settings can be generated or omitted
- **Optional Devcontainer**: Containerized workspace with configurable Node/Postgres defaults
- **Starter Environment Files**: `.env.example` plus optional auto-generated `.env`
- **Docker Runtime Image**: App image scaffold with rendered host/port defaults

### Template Power

- **Fully Configurable Defaults**: Host, ports, API prefix, log level, auth mode, DB settings, storage backend, and more
- **Custom Python Import Root**: Render `src/<package_name>/` instead of a hard-coded `src/app`
- **Prompt-Driven Interface**: `cookiecutter.json` is the source of truth for the generated project contract
- **Hooks Included**: Pre-generation validation and post-generation cleanup/bootstrap are built in
- **Optional Generated Assets**: Toggle `.vscode/`, `.devcontainer/`, and starter `.env` creation at render time
- **Template Smoke Tests**: Maintainer tests verify default and custom renders continuously

## 🚀 Quick Start

### Prerequisites

Choose one approach:

**Local Tooling Approach:**

- Python 3.12+
- Cookiecutter 2.0+
- `uv` recommended

**Containerized Workspace Approach:**

- Docker
- VS Code with Dev Containers support (if you render `.devcontainer/`)
- Cookiecutter 2.0+

### Installation

1. Install Cookiecutter:

```bash
pip install cookiecutter

# or
uv tool install cookiecutter
```

1. Generate your project:

```bash
cookiecutter <your-git-url>

# or from a local clone
uv run cookiecutter .
```

1. Answer the prompts:

```markdown
project_name [FastAPI Cookiecutter App]: Acme Platform API
project_slug [acme-platform-api]: acme-platform-api
package_name [acme_platform_api]: platform_api
author_name [Your Name]: Jane Doe
python_version [3.13]: 3.13
dev_port [5000]: 5055
api_prefix [/api]: /internal
default_auth_mode [jwks/hs]: hs
default_storage_backend [s3/filesystem]: filesystem
include_vscode [yes/no]: yes
include_devcontainer [yes/no]: no
...
```

1. Navigate to your project:

```bash
cd acme-platform-api
```

1. Start developing:

```bash
uv sync
just dev
```

1. Access the generated app (default values shown):

```text
API root:           http://localhost:5000/
Ping:               http://localhost:5000/public/ping
Config snapshot:    http://localhost:5000/api/config
Templates listing:  http://localhost:5000/api/templates
Feature summary:    http://localhost:5000/api/advanced/features
```

### Containerized Workspace (Optional)

If you render the project with `include_devcontainer=yes`, you also get a ready-to-open development container setup:

1. Generate the project with the devcontainer option enabled
2. Open the folder in VS Code
3. Reopen in container
4. Use the generated forwarded ports and optional Postgres service

### Local Development (Advanced)

If you prefer local development without a devcontainer:

1. Review the generated `.env` (or copy `.env.example` if you disabled auto-generation)
2. Run `uv sync`
3. Start the app with `just dev`
4. Run tests in another terminal with `just test`
5. If you enabled database-backed features, make sure your configured DB/storage services are reachable

## 📦 What You Get

```text
your_project/
├── src/
│   └── your_package/
│       ├── asgi.py
│       ├── config.py
│       ├── views.py
│       ├── core/
│       │   ├── core_api/
│       │   ├── core_auth/
│       │   ├── core_db/
│       │   ├── core_extensions/
│       │   ├── core_messages/
│       │   ├── core_middleware/
│       │   └── core_storage/
│       ├── services/
│       ├── shared/
│       └── utils/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── Dockerfile
├── Justfile
├── .env.example
├── .vscode/            # optional
├── .devcontainer/      # optional
├── pyproject.toml
├── pytest.ini
├── mypy.ini
└── ruff.toml
```

## 🛠️ Configuration Options

### Required

- **project_name**: Human-readable project name
- **project_slug**: Directory-friendly render target
- **package_name**: Python import/package root under `src/`
- **author_name**: Author metadata
- **python_version**: Target Python version for the generated project

### Common Runtime Options

- **app_title**: FastAPI application title
- **default_host / dev_port / prod_host / prod_port**: Default bind configuration
- **api_prefix**: Prefix for non-public routers
- **default_log_level**: Generated logging default
- **default_test_mode / default_profiling_enabled**: Runtime behavior toggles
- **default_cors_allowed_origins / methods / headers**: Global CORS defaults

### Infrastructure Options

- **default_auth_mode / default_auth_algorithms**: Auth mode and token algorithm defaults
- **auth_\***: Signature and token verification flags
- **db_\***: Database host, port, credentials, pool settings, and probe timeouts
- **role_\***: Role activation, prefixes, groups, and hierarchy
- **default_storage_backend / s3_\* / filesystem_root**: Storage selection and defaults

### Optional Generated Assets

- **include_vscode**: Include `.vscode/` launch/tasks/settings
- **include_devcontainer**: Include `.devcontainer/` workspace config
- **create_dotenv_file**: Auto-create `.env` from `.env.example`
- **devcontainer_node_version**: Node version inside the devcontainer
- **devcontainer_postgres_image**: Postgres image for the optional devcontainer stack

For the complete prompt interface, see `cookiecutter.json`.

## 📚 Documentation

After generating your project, you'll find:

- `README.md` — generated project-specific documentation
- `src/<package_name>/services/README.md` — service/module architecture guide
- `cookiecutter.json` — the full template variable contract
- `hooks/` — pre/post generation hook logic for validation and setup

## 🧪 Testing

The template includes maintainer smoke tests and generated project test wiring:

```bash
# Maintainer tests for this template repo
uv sync
uv run pytest

# Generated project tests
just test
just test-unit
just test-integration
just test-e2e
```

## 🎯 Key Features Explained

### Fully Configurable Defaults

This template is designed so the generated scaffold is not stuck with hard-coded assumptions like `src/app`, fixed ports, fixed auth mode, or a single storage backend. The Cookiecutter prompts define the project contract, and the generated code, Docker image, editor config, and environment defaults follow that contract.

### Config-First FastAPI Foundation

The generated app comes with typed settings, reusable auth/storage/database foundations, and a small set of example endpoints so you can start from something more realistic than an empty app factory.

### Optional Editor & Container Scaffolding

If you want a lean generated project, you can skip `.vscode/` and `.devcontainer/`. If you want a batteries-included developer experience, turn them on and get launch configs, tasks, and a containerized workspace out of the box.

## 🤝 Contributing

Contributions are welcome. If you want to improve the template:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-improvement`)
3. Commit your changes (`git commit -m 'Improve template README or scaffold'`)
4. Run the maintainer tests (`uv run pytest`)
5. Open a Pull Request

## 📄 License

This repository currently does not include a `LICENSE` file. If you plan to publish or redistribute the template broadly, add one explicitly.

## 🙏 Acknowledgments

- Inspired by the broader [Cookiecutter](https://github.com/cookiecutter/cookiecutter) ecosystem
- Built around a modern FastAPI + typed-settings + render-time-configuration workflow

## 🔗 Links

- [Cookiecutter GitHub](https://github.com/cookiecutter/cookiecutter)
- [Cookiecutter Documentation](https://cookiecutter.readthedocs.io/)

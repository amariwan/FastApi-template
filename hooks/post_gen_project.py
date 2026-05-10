from __future__ import annotations

import shutil
from pathlib import Path


CREATE_DOTENV_FILE = "{{ cookiecutter.create_dotenv_file }}"
INCLUDE_VSCODE = "{{ cookiecutter.include_vscode }}"
INCLUDE_DEVCONTAINER = "{{ cookiecutter.include_devcontainer }}"


def main() -> None:
    project_dir = Path.cwd()
    project_name = project_dir.name
    python_version = "{{ cookiecutter.python_version }}"

    dockerfile_path = project_dir / "Dockerfile"
    if dockerfile_path.exists() and python_version != "3.13":
        dockerfile_text = dockerfile_path.read_text(encoding="utf-8")
        dockerfile_text = dockerfile_text.replace(
            "FROM astral/uv:python3.13-bookworm-slim",
            f"FROM astral/uv:python{python_version}-bookworm-slim",
            1,
        )
        dockerfile_path.write_text(dockerfile_text, encoding="utf-8")

    if INCLUDE_VSCODE == "no":
        shutil.rmtree(project_dir / ".vscode", ignore_errors=True)

    if INCLUDE_DEVCONTAINER == "no":
        shutil.rmtree(project_dir / ".devcontainer", ignore_errors=True)

    env_example_path = project_dir / ".env.example"
    env_path = project_dir / ".env"
    if CREATE_DOTENV_FILE == "yes" and env_example_path.exists() and not env_path.exists():
        shutil.copyfile(env_example_path, env_path)

    print()
    print(f"Generated project: {project_name}")
    print("Next steps:")
    print(f"  cd {project_name}")
    if CREATE_DOTENV_FILE == "yes":
        print("  # .env was created from .env.example with your template defaults")
    else:
        print("  cp .env.example .env  # optional, if you want a local env file")
    print("  uv sync")
    print("  just dev")
    print()
    print("Tip: the Python package root lives under src/ and is already wired into the tooling.")


if __name__ == "__main__":
    main()

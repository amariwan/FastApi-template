import builtins

from fastapi import FastAPI

from {{ cookiecutter.package_name }}.core.core_api import healthcheck
from {{ cookiecutter.package_name }}.core.core_extensions.loader import ServiceRegistration


def test_collect_service_runtime_configs_uses_registration_hook(monkeypatch) -> None:
    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "{{ cookiecutter.package_name }}.services.docgen.config" or name.startswith("{{ cookiecutter.package_name }}.services.docgen.config."):
            raise ModuleNotFoundError("No module named '{{ cookiecutter.package_name }}.services.docgen.config'")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    app = FastAPI()
    app.state.service_registrations = [
        ServiceRegistration(
            name="docgen",
            runtime_config_hook=lambda: {"render": {"default_output_format": "pdf"}},
        )
    ]

    request = type("Request", (), {"app": app})()

    assert healthcheck._collect_runtime_config_sections(request) == {"render": {"default_output_format": "pdf"}}


def test_collect_liveness_checks_does_not_probe_external_dependencies(monkeypatch) -> None:
    def fail_db(*args, **kwargs):
        raise AssertionError("db probe")

    def fail_storage(*args, **kwargs):
        raise AssertionError("storage probe")

    monkeypatch.setattr(healthcheck, "check_db", fail_db)
    monkeypatch.setattr(healthcheck, "check_storage", fail_storage)

    app = FastAPI()
    request = type("Request", (), {"app": app})()

    result = healthcheck._collect_liveness_checks(request)

    assert result["app"].status == "ok"
    assert result["app"].message == "application settings loaded"
    assert list(result) == ["app"]

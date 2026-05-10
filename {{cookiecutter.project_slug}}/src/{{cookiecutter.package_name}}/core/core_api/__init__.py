"""Core API routers exposed by the template application."""

from . import advanced_v1, config_v1, healthcheck, public_v1, templates_v1

__all__ = ["advanced_v1", "config_v1", "healthcheck", "public_v1", "templates_v1"]

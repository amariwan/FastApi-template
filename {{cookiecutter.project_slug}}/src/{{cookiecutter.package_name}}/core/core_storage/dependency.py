"""FastAPI dependency for storage injection."""

from typing import Annotated

from fastapi import Depends

from {{ cookiecutter.package_name }}.core.core_storage.base import StorageClient
from {{ cookiecutter.package_name }}.core.core_storage.factory import get_storage_client

StorageDep = Annotated[StorageClient, Depends(get_storage_client)]

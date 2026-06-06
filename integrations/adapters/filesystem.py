"""Filesystem adapter — scan generated/ workspace."""

from __future__ import annotations

from pathlib import Path

from integrations.adapters.base import RegistryAdapter
from registry.models import RegistryManifest


class FilesystemAdapter(RegistryAdapter):
    """Discover artifacts and services from iterun workspace files."""

    def collect(self, workspace: Path) -> RegistryManifest:
        from registry.discover import discover_workspace

        return discover_workspace(workspace)

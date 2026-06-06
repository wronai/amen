"""Docker adapter — enrich registry with running container state."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from integrations.adapters.filesystem import FilesystemAdapter
from registry.models import LifecyclePhase, RegistryManifest


class DockerAdapter(FilesystemAdapter):
    """Merge docker ps / compose state into registry manifest."""

    def collect(self, workspace: Path) -> RegistryManifest:
        manifest = super().collect(workspace)
        return self.enrich(manifest, workspace)

    def enrich(self, manifest: RegistryManifest, workspace: Path) -> RegistryManifest:
        running = _running_iterun_containers()
        if not running:
            return manifest
        any_running = self._merge_container_state(manifest, running)
        if any_running and manifest.status.phase == LifecyclePhase.PLANNED:
            manifest.status.phase = LifecyclePhase.RUNNING
        return manifest

    def _merge_container_state(
        self, manifest: RegistryManifest, running: list[dict]
    ) -> bool:
        services = manifest.spec.get("services") or []
        any_running = False
        intent = manifest.metadata.name
        for svc in services:
            matches = _match_service_containers(svc.get("name", ""), intent, running)
            if not matches:
                continue
            any_running = True
            _apply_container_to_service(svc, matches[0])
        manifest.spec["services"] = services
        return any_running


def _match_service_containers(name: str, intent: str, running: list[dict]) -> list[dict]:
    return [
        c
        for c in running
        if c.get("Labels", {}).get("dev.iterun.service") == name
        or c.get("Labels", {}).get("dev.iterun.intent") == intent
        or name in (c.get("Names") or [""])[0]
    ]


def _apply_container_to_service(svc: dict, container: dict) -> None:
    svc["container_id"] = container.get("ID") or container.get("Id")
    svc["image"] = container.get("Image")
    labels = container.get("Labels") or {}
    svc.setdefault("labels", {}).update(
        {k: v for k, v in labels.items() if k.startswith("dev.iterun.")}
    )


def _running_iterun_containers() -> list[dict]:
    try:
        proc = subprocess.run(
            ["docker", "ps", "--format", "{{json .}}"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if proc.returncode != 0:
            return []
        out = []
        for line in proc.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return [
            c
            for c in out
            if "dev.iterun." in json.dumps(c.get("Labels") or {})
            or "intent-" in (c.get("Names") or [""])[0]
        ]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []

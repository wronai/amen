"""Discover artifacts and services from an iterun workspace."""

from __future__ import annotations

from pathlib import Path

from registry.discover_artifacts import discover_artifacts
from registry.discover_context import WorkspaceContext, load_workspace_context
from registry.discover_services import build_single_service, build_stack_services
from registry.models import RegistryManifest, RegistryMetadata, RegistryStatus


def _build_services(ctx: WorkspaceContext):
    if ctx.is_stack and ctx.stack_services:
        return build_stack_services(
            intent_name=ctx.intent_name,
            intent_id=ctx.intent_id,
            stack_services=ctx.stack_services,
            stack_urls=ctx.stack_urls,
            container_id=ctx.container_id,
            workspace=ctx.workspace,
        )
    return build_single_service(
        intent_name=ctx.intent_name,
        intent_id=ctx.intent_id,
        intent_doc=ctx.intent_doc,
        endpoints=ctx.endpoints,
        container_id=ctx.container_id,
        workspace=ctx.workspace,
    )


def discover_workspace(workspace: str | Path) -> RegistryManifest:
    """Build registry manifest by scanning workspace artifacts."""
    ctx = load_workspace_context(workspace)
    services = _build_services(ctx)
    artifacts = discover_artifacts(ctx.workspace)

    return RegistryManifest(
        metadata=RegistryMetadata(
            name=ctx.intent_name,
            intent_id=ctx.intent_id,
            workspace=str(ctx.workspace),
            prompt=ctx.prompt,
            is_stack=ctx.is_stack,
        ),
        spec={
            "deployment": ctx.deployment.value,
            "services": [s.model_dump(mode="json") for s in services],
            "artifacts": [a.model_dump(mode="json") for a in artifacts],
        },
        status=RegistryStatus(
            phase=ctx.phase,
            success=ctx.session.get("success") if ctx.session else None,
            session_path=str(ctx.workspace / "session.json")
            if (ctx.workspace / "session.json").is_file()
            else None,
            verification=(ctx.session or {}).get("verification"),
            endpoints=ctx.endpoints,
        ),
    )

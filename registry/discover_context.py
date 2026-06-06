"""Load workspace context for registry discovery."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from registry.discover_io import intent_from_workspace, load_session, load_stack_urls, phase_from_session
from registry.models import DeploymentKind, LifecyclePhase


@dataclass
class WorkspaceContext:
    workspace: Path
    session: dict[str, Any] | None
    intent_doc: dict[str, Any]
    intent_name: str
    intent_id: str | None
    is_stack: bool
    deployment: DeploymentKind
    stack_services: dict[str, Any]
    stack_urls: dict[str, str]
    endpoints: list[str]
    container_id: str | None
    phase: LifecyclePhase
    prompt: str | None


def _intent_identity(
    ws: Path,
    intent_doc: dict[str, Any],
    session: dict[str, Any] | None,
) -> tuple[str, str | None]:
    intent_section = intent_doc.get("INTENT") or intent_doc.get("intent") or {}
    intent_name = intent_section.get("name") or ws.name
    intent_id = intent_section.get("id") or (session or {}).get("generate", {}).get("ir", {}).get("id")
    return intent_name, intent_id


def _stack_metadata(intent_doc: dict[str, Any], ws: Path) -> tuple[bool, dict[str, Any]]:
    stack_section = intent_doc.get("STACK") or {}
    stack_services = (stack_section.get("services") or {}) if isinstance(stack_section, dict) else {}
    is_stack = bool(stack_services) or (ws / "docker-compose.yaml").is_file()
    return is_stack, stack_services


def _workspace_prompt(ws: Path, session: dict[str, Any] | None) -> str | None:
    prompt_path = ws / "prompt.txt"
    return (session or {}).get("prompt") or (
        prompt_path.read_text(encoding="utf-8") if prompt_path.is_file() else None
    )


def load_workspace_context(workspace: str | Path) -> WorkspaceContext:
    ws = Path(workspace).resolve()
    session = load_session(ws)
    intent_doc = intent_from_workspace(ws) or {}
    intent_name, intent_id = _intent_identity(ws, intent_doc, session)
    is_stack, stack_services = _stack_metadata(intent_doc, ws)
    execution = (session or {}).get("execution") or {}

    return WorkspaceContext(
        workspace=ws,
        session=session,
        intent_doc=intent_doc,
        intent_name=intent_name,
        intent_id=intent_id,
        is_stack=is_stack,
        deployment=DeploymentKind.STACK if is_stack else DeploymentKind.SINGLE,
        stack_services=stack_services,
        stack_urls=load_stack_urls(ws),
        endpoints=list(execution.get("endpoints") or []),
        container_id=execution.get("container_id"),
        phase=phase_from_session(session),
        prompt=_workspace_prompt(ws, session),
    )

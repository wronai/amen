"""Pack iterun workspace into a single markpact README (portable stack artifact)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ir.models import IntentIR

STACK_MARKPACT = "stack.markpact.md"
PACK_EXCLUDE = {
    "session.json",
    "execution.json",
    "container.log",
    "verify.rounds.json",
    "iterun.registry.json",
    "otel.resources.json",
    "catalog",
    ".pactown-sandboxes",
    "pactown.yaml",
    STACK_MARKPACT,
}


def _run_command_for_ir(ir: IntentIR) -> str | None:
    if ir.stack and ir.stack.services:
        return "docker compose -f docker-compose.yaml up --build -d"
    impl = ir.implementation
    if impl.framework == "fastapi":
        return "uvicorn app:app --host 0.0.0.0 --port ${MARKPACT_PORT:-8000}"
    if impl.framework == "flask":
        return "flask run --host 0.0.0.0 --port ${MARKPACT_PORT:-5000}"
    if impl.framework == "express" or impl.language == "node":
        return "node app.js"
    if impl.language == "python":
        return "python app.py"
    return None


def _service_run_command(svc) -> str | None:
    if svc.framework == "fastapi":
        return "uvicorn app:app --host 0.0.0.0 --port ${MARKPACT_PORT:-8000}"
    if svc.framework == "express" or svc.language == "node":
        return "node app.js"
    return None


def _pack_service_readmes(
    ws: Path,
    ir: IntentIR,
    title: str,
    pack_directory,
) -> dict[str, str]:
    written: dict[str, str] = {}
    for svc in ir.stack.services:
        svc_dir = ws / "services" / svc.name
        if not svc_dir.is_dir():
            continue
        svc_pack = pack_directory(
            svc_dir,
            output=svc_dir / "README.md",
            title=svc.name,
            description=f"Service {svc.name} from {title}",
            run_command=_service_run_command(svc),
            exclude=PACK_EXCLUDE.copy(),
            verbose=False,
        )
        if svc_pack.success:
            written[f"services/{svc.name}/README.md"] = str(svc_pack.output_path)
    return written


def pack_workspace(
    workspace: str | Path,
    ir: IntentIR | None = None,
    *,
    output_name: str = STACK_MARKPACT,
    pack_services: bool = True,
) -> dict[str, Any]:
    """Pack generated/ into stack.markpact.md (+ per-service README for pactown)."""
    ws = Path(workspace).resolve()
    try:
        from markpact.packer import pack_directory
    except ImportError as e:
        return {
            "success": False,
            "error": "markpact not installed: pip install markpact or pip install -e '.[runtime]'",
            "detail": str(e),
        }

    title = ir.intent.name if ir else ws.name
    desc = ir.intent.goal if ir and ir.intent.goal else f"ITERUN generated stack: {title}"
    result = pack_directory(
        ws,
        output=ws / output_name,
        title=title,
        description=desc,
        run_command=_run_command_for_ir(ir) if ir else None,
        exclude=PACK_EXCLUDE.copy(),
        verbose=False,
    )

    written: dict[str, str] = {}
    if result.success:
        written[output_name] = str(result.output_path)
    if pack_services and ir and ir.stack and ir.stack.services:
        written.update(_pack_service_readmes(ws, ir, title, pack_directory))

    return {
        "success": result.success,
        "message": result.message,
        "files_packed": result.files_packed,
        "output": str(result.output_path) if result.success else None,
        "written": written,
    }

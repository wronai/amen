"""Persist full run session (prompt → generate → execute → verify) under workspace."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from generator.results import PipelineResult


def write_session_artifacts(
    workspace: Path | str,
    result: PipelineResult,
    *,
    container_logs: str | None = None,
) -> dict[str, str]:
    """Write session.json, execution.json, prompt.txt, optional container.log."""
    ws = Path(workspace)
    ws.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}

    (ws / "prompt.txt").write_text(result.prompt, encoding="utf-8")
    written["prompt.txt"] = str(ws / "prompt.txt")

    session: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **result.to_dict(),
    }
    if container_logs:
        session["container_logs_tail"] = container_logs

    session_path = ws / "session.json"
    session_path.write_text(json.dumps(session, indent=2), encoding="utf-8")
    written["session.json"] = str(session_path)

    if result.execution:
        exec_payload = dict(result.execution)
        if container_logs:
            exec_payload["container_logs_tail"] = container_logs
        exec_path = ws / "execution.json"
        exec_path.write_text(json.dumps(exec_payload, indent=2), encoding="utf-8")
        written["execution.json"] = str(exec_path)

    if container_logs:
        log_path = ws / "container.log"
        log_path.write_text(container_logs, encoding="utf-8")
        written["container.log"] = str(log_path)

    return written

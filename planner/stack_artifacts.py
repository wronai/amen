"""Write STACK plan output: services/*/Dockerfile + docker-compose.yaml."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ir.models import IntentIR
from planner.simulator import DryRunResult


def write_stack_artifacts(
    workspace: Path | str,
    ir: IntentIR,
    plan_result: DryRunResult,
) -> dict[str, str]:
    ws = Path(workspace)
    ws.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}

    plan_payload = {"intent": ir.to_dict(), "plan": plan_result.to_dict()}
    plan_file = ws / "plan.result.json"
    plan_file.write_text(json.dumps(plan_payload, indent=2), encoding="utf-8")
    written["plan.result.json"] = str(plan_file)

    if plan_result.compose_yaml:
        compose_path = ws / "docker-compose.yaml"
        compose_path.write_text(plan_result.compose_yaml, encoding="utf-8")
        written["docker-compose.yaml"] = str(compose_path)

    for svc_name, art in (plan_result.service_artifacts or {}).items():
        if art.get("image"):
            continue
        svc_dir = ws / "services" / svc_name
        svc_dir.mkdir(parents=True, exist_ok=True)

        lang = art.get("language", "python")
        app_name = "app.py" if lang == "python" else "app.js"
        if art.get("code"):
            app_path = svc_dir / app_name
            app_path.write_text(art["code"], encoding="utf-8")
            written[f"services/{svc_name}/{app_name}"] = str(app_path)

        if art.get("dockerfile"):
            df_path = svc_dir / "Dockerfile"
            df_path.write_text(art["dockerfile"], encoding="utf-8")
            written[f"services/{svc_name}/Dockerfile"] = str(df_path)

        if lang == "node":
            pkg_path = svc_dir / "package.json"
            pkg_path.write_text(
                json.dumps(
                    {
                        "name": svc_name,
                        "version": "1.0.0",
                        "main": "app.js",
                        "dependencies": {"express": "^4.18.0"},
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            written[f"services/{svc_name}/package.json"] = str(pkg_path)

    return written

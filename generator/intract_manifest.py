"""Generate intract.yaml contract manifest from iterun intent.yaml (+ optional prompt)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml


def _slug(path: str) -> str:
    slug = re.sub(r"[{}]", "", path).strip("/").replace("/", "_") or "root"
    return re.sub(r"[^\w]+", "_", slug)


def _safe_id(name: str) -> str:
    return re.sub(r"[^\w]+", "_", name).strip("_").lower()


def _parse_action_strings(actions: list[Any]) -> list[tuple[str, str]]:
    parsed: list[tuple[str, str]] = []
    for action in actions:
        if not isinstance(action, str):
            continue
        match = re.match(
            r"api\.expose\s+(GET|POST|PUT|PATCH|DELETE)\s+(\S+)",
            action.strip(),
            re.IGNORECASE,
        )
        if match:
            parsed.append((match.group(1).upper(), match.group(2)))
    return parsed


def parse_api_actions(intent_data: dict[str, Any]) -> list[tuple[str, str]]:
    parsed = _parse_action_strings(
        (intent_data.get("IMPLEMENTATION", {}) or {}).get("actions", []) or []
    )
    stack = intent_data.get("STACK") or {}
    for _name, svc in (stack.get("services") or {}).items():
        if not isinstance(svc, dict):
            continue
        if not svc.get("host_port"):
            continue
        parsed.extend(_parse_action_strings(svc.get("actions", []) or []))
    return parsed


def build_intract_manifest(
    intent_data: dict[str, Any],
    *,
    prompt: str | None = None,
) -> dict[str, Any]:
    intent = intent_data.get("INTENT", {}) or {}
    name = str(intent.get("name", "service"))
    goal = str(intent.get("goal", "") or "").strip()
    safe = _safe_id(name)

    requires = [f"implement.{_slug(path)}" for _, path in parse_api_actions(intent_data)]
    meaning = goal or (prompt.strip().splitlines()[0] if prompt else f"Contract for {name}")

    return {
        "project": {"name": f"iterun-{safe}"},
        "contracts": [
            {
                "id": f"api.{safe}",
                "scope": "project",
                "intent": f"ship:{safe}",
                "priority": 1,
                "domain": "api",
                "require": requires,
                "validate": ["required_intents"],
                "meaning": meaning,
            }
        ],
        "files": {
            "openapi.yaml": [
                {
                    "scope": "artifact",
                    "intent": "document:public_api",
                    "priority": 2,
                    "domain": "api",
                    "validate": ["input_presence", "output_presence"],
                }
            ],
            "Dockerfile": [
                {
                    "scope": "artifact",
                    "intent": "deploy:container_image",
                    "priority": 1,
                    "domain": "devops",
                    "validate": ["no_forbidden_effect"],
                }
            ],
        },
    }


def intent_to_intract_dict(
    intent_path: Path | str,
    *,
    prompt: str | None = None,
) -> dict[str, Any]:
    data = yaml.safe_load(Path(intent_path).read_text(encoding="utf-8")) or {}
    return build_intract_manifest(data, prompt=prompt)


def write_intract_manifest(
    intent_path: Path | str,
    output_path: Path | str,
    *,
    prompt: str | None = None,
) -> Path:
    manifest = intent_to_intract_dict(intent_path, prompt=prompt)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return out

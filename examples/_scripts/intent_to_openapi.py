#!/usr/bin/env python3
"""Emit OpenAPI 3.1 with x-intract contracts from iterun intent.yaml."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml


def _slug(path: str) -> str:
    slug = re.sub(r"[{}]", "", path).strip("/").replace("/", "_") or "root"
    return re.sub(r"[^\w]+", "_", slug)


def intent_to_openapi(intent_path: Path) -> dict:
    data = yaml.safe_load(intent_path.read_text(encoding="utf-8")) or {}
    intent = data.get("INTENT", {}) or {}
    actions = (data.get("IMPLEMENTATION", {}) or {}).get("actions", []) or []

    paths: dict = {}
    for action in actions:
        if not isinstance(action, str):
            continue
        match = re.match(
            r"api\.expose\s+(GET|POST|PUT|PATCH|DELETE)\s+(\S+)",
            action.strip(),
            re.IGNORECASE,
        )
        if not match:
            continue
        method, route = match.group(1).lower(), match.group(2)
        slug = _slug(route)
        operation = {
            "summary": f"{method.upper()} {route}",
            "x-intract": {
                "scope": "endpoint",
                "intent": f"implement:{slug}",
                "priority": 1,
                "domain": "api",
                "validate": ["input_presence", "output_presence"],
                "meaning": f"Prompt contract for {method.upper()} {route}",
            },
            "responses": {
                "200": {"description": "OK"},
            },
        }
        paths.setdefault(route, {})[method] = operation

    return {
        "openapi": "3.1.0",
        "info": {
            "title": intent.get("name", "iterun-service"),
            "description": intent.get("goal", ""),
            "version": "1.0.0",
        },
        "paths": paths,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("intent", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()

    spec = intent_to_openapi(args.intent)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()

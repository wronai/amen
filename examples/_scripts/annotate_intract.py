#!/usr/bin/env python3
"""Inject @intract.v1 comments into iterun-generated app.py / app.js from intent.yaml."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml


def _slug(path: str) -> str:
    slug = re.sub(r"[{}]", "", path).strip("/").replace("/", "_") or "root"
    return re.sub(r"[^\w]+", "_", slug)


def _actions(intent_path: Path) -> list[tuple[str, str]]:
    data = yaml.safe_load(intent_path.read_text(encoding="utf-8")) or {}
    actions = (data.get("IMPLEMENTATION", {}) or {}).get("actions", []) or []
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


def _comment(method: str, path: str) -> str:
    slug = _slug(path)
    return (
        f"# @intract.v1 scope:endpoint intent:implement:{slug} priority:1 domain:api "
        f'validate:input_presence,output_presence meaning:"{method} {path}"'
    )


def annotate_python(app_path: Path, intent_path: Path) -> None:
    routes = _actions(intent_path)
    lines = app_path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    route_idx = 0

    for line in lines:
        match = re.match(r'@app\.(get|post|put|patch|delete)\("([^"]+)"\)', line, re.I)
        if match and route_idx < len(routes):
            method, path = routes[route_idx]
            if match.group(2) == path:
                out.append(_comment(method, path))
                route_idx += 1
        out.append(line)

    app_path.write_text("\n".join(out) + "\n", encoding="utf-8")


def annotate_express(app_path: Path, intent_path: Path) -> None:
    routes = _actions(intent_path)
    lines = app_path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    route_idx = 0

    for line in lines:
        match = re.match(r"app\.(get|post|put|patch|delete)\('([^']+)'", line, re.I)
        if not match:
            match = re.match(r'app\.(get|post|put|patch|delete)\("([^"]+)"', line, re.I)
        if match and route_idx < len(routes):
            method, path = routes[route_idx]
            if match.group(2) == path:
                out.append(_comment(method, path).replace("# ", "// "))
                route_idx += 1
        out.append(line)

    app_path.write_text("\n".join(out) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("intent", type=Path)
    parser.add_argument("app", type=Path)
    args = parser.parse_args()

    if args.app.suffix == ".py":
        annotate_python(args.app, args.intent)
    elif args.app.suffix == ".js":
        annotate_express(args.app, args.intent)
    else:
        raise SystemExit(f"Unsupported app file: {args.app}")
    print(args.app)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Verify generated intent + live service match expectations.yaml (from prompt)."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import yaml


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _parse_actions(intent_data: dict[str, Any]) -> list[tuple[str, str]]:
    actions = (intent_data.get("IMPLEMENTATION", {}) or {}).get("actions", []) or []
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


def _http_probe(base_url: str, method: str, path: str, timeout: float = 10.0) -> tuple[int, dict[str, Any]]:
    url = f"{base_url.rstrip('/')}{path}"
    req = urllib.request.Request(url, method=method.upper())
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        status = resp.status
        body = resp.read().decode("utf-8")
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {"text": body[:500]}
        return status, data


def verify(
    expectations_path: Path,
    intent_path: Path,
    base_url: str | None,
) -> list[str]:
    errors: list[str] = []
    expectations = _load_yaml(expectations_path)
    intent_data = _load_yaml(intent_path)

    expected_name = expectations.get("name")
    actual_name = (intent_data.get("INTENT", {}) or {}).get("name")
    if expected_name and actual_name != expected_name:
        errors.append(f"intent name: expected {expected_name!r}, got {actual_name!r}")

    expected_fw = expectations.get("framework")
    actual_fw = (intent_data.get("IMPLEMENTATION", {}) or {}).get("framework")
    if expected_fw and actual_fw != expected_fw:
        errors.append(f"framework: expected {expected_fw!r}, got {actual_fw!r}")

    parsed_actions = {(m, p) for m, p in _parse_actions(intent_data)}
    for endpoint in expectations.get("endpoints", []) or []:
        key = (endpoint["method"].upper(), endpoint["path"])
        if key not in parsed_actions:
            errors.append(f"missing in iterun.yaml: {key[0]} {key[1]}")

    if base_url:
        for endpoint in expectations.get("endpoints", []) or []:
            method = endpoint["method"].upper()
            path = endpoint["path"]
            expected_status = int(endpoint.get("status", 200))
            path_for_probe = re.sub(r"\{[^}]+\}", "1", path)
            try:
                status, data = _http_probe(base_url, method, path_for_probe)
            except urllib.error.HTTPError as exc:
                status = exc.code
                data = {}
            except Exception as exc:
                errors.append(f"probe failed {method} {path}: {exc}")
                continue

            if status != expected_status:
                errors.append(
                    f"HTTP {method} {path}: expected status {expected_status}, got {status}"
                )
                continue

            for field in endpoint.get("json_fields", []) or []:
                if field not in data:
                    errors.append(f"HTTP {method} {path}: missing json field {field!r}")

            for needle in endpoint.get("body_contains", []) or []:
                blob = json.dumps(data)
                if needle not in blob:
                    errors.append(
                        f"HTTP {method} {path}: response missing {needle!r}"
                    )

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("expectations", type=Path)
    parser.add_argument("intent", type=Path)
    parser.add_argument("--url", default=None, help="Live service base URL")
    args = parser.parse_args()

    errors = verify(args.expectations, args.intent, args.url)
    if errors:
        for err in errors:
            print(f"FAIL: {err}", file=sys.stderr)
        sys.exit(1)
    print("OK expectations verified")


if __name__ == "__main__":
    main()

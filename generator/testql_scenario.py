"""Generate TestQL scenario from iterun intent.yaml (contract → HTTP probes)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from generator.intract_manifest import parse_api_actions


def _probe_path(path: str) -> str:
    return re.sub(r"\{[^}]+\}", "1", path)


def build_testql_scenario(
    intent_data: dict[str, Any],
    *,
    intent_name: str | None = None,
) -> str:
    intent = intent_data.get("INTENT", {}) or {}
    name = intent_name or str(intent.get("name", "service"))
    actions = parse_api_actions(intent_data)

    api_rows: list[str] = []
    for method, path in actions:
        probe = _probe_path(path)
        if method == "GET":
            api_rows.append(f"  {method},  {probe},  200,  status,  ok")
        else:
            api_rows.append(f"  {method},  {probe},  200")

    api_block = "\n".join(api_rows) if api_rows else "  GET,  /ping,  200,  status,  ok"
    count = len(api_rows) or 1

    return f"""# SCENARIO: iterun contract verify — {name}
# TYPE: api
# GENERATED: true

CONFIG[3]{{key, value}}:
  api_url, $TARGET_URL
  timeout_ms, 20000
  retry_count, 4

WAIT 2500

API[{count}]{{method, endpoint, status, assert_key, assert_value}}:
{api_block}

ASSERT[2]{{field, operator, expected}}:
  _status, >=, 200
  _status, <, 500
"""


def write_testql_scenario(
    intent_path: Path | str,
    output_path: Path | str,
) -> Path:
    data = yaml.safe_load(Path(intent_path).read_text(encoding="utf-8")) or {}
    content = build_testql_scenario(data)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    return out

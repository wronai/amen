"""Tests for TestQL scenario generation."""

from pathlib import Path

import yaml

from generator.testql_scenario import build_testql_scenario, write_testql_scenario

SAMPLE = """
INTENT:
  name: ping-smoke
IMPLEMENTATION:
  actions:
    - api.expose GET /ping
    - api.expose GET /health
"""


def test_build_testql_contains_endpoints():
    data = yaml.safe_load(SAMPLE)
    text = build_testql_scenario(data)
    assert "/ping" in text
    assert "/health" in text
    assert "GENERATED: true" in text
    assert "API[2]" in text


def test_write_testql_scenario(tmp_path: Path):
    intent = tmp_path / "intent.yaml"
    intent.write_text(SAMPLE, encoding="utf-8")
    out = write_testql_scenario(intent, tmp_path / "service.testql.toon.yaml")
    assert out.name == "service.testql.toon.yaml"
    assert "GET" in out.read_text(encoding="utf-8")

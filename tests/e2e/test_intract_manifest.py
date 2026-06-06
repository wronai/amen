"""Tests for intract.yaml generation from intent."""

from pathlib import Path

import yaml

from generator.intract_manifest import build_intract_manifest, write_intract_manifest


SAMPLE_INTENT = """
INTENT:
  name: ping-smoke
  goal: Minimal health API

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /ping
    - api.expose GET /health
"""


def test_build_intract_manifest_require_list():
    data = yaml.safe_load(SAMPLE_INTENT)
    manifest = build_intract_manifest(data, prompt="Create ping API")

    assert manifest["project"]["name"] == "iterun-ping_smoke"
    contract = manifest["contracts"][0]
    assert "implement.ping" in contract["require"]
    assert "implement.health" in contract["require"]
    assert "ping" in contract["meaning"].lower() or "health" in contract["meaning"].lower()


def test_write_intract_manifest(tmp_path: Path):
    intent = tmp_path / "intent.yaml"
    intent.write_text(SAMPLE_INTENT, encoding="utf-8")
    out = write_intract_manifest(intent, tmp_path / "intract.yaml", prompt="x")
    assert out.is_file()
    loaded = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert loaded["files"]["openapi.yaml"]

"""Tests for pipeline repair prompt and expectations integration."""

from pathlib import Path

import yaml

from generator.pipeline import _build_repair_prompt, _expectations_summary


def test_expectations_summary_lists_endpoints(tmp_path: Path):
    exp = tmp_path / "expectations.yaml"
    exp.write_text(
        yaml.dump({
            "name": "user-api",
            "framework": "fastapi",
            "endpoints": [
                {"method": "GET", "path": "/ping"},
                {"method": "POST", "path": "/users"},
            ],
        }),
        encoding="utf-8",
    )
    summary = _expectations_summary(tmp_path)
    assert "user-api" in summary
    assert "GET /ping" in summary
    assert "POST /users" in summary


def test_build_repair_prompt_includes_expectations(tmp_path: Path):
    (tmp_path / "expectations.yaml").write_text(
        "framework: fastapi\nendpoints:\n  - method: GET\n    path: /health\n",
        encoding="utf-8",
    )
    prompt = _build_repair_prompt(
        "Make an API",
        ["expectations missing in iterun.yaml: GET /health"],
        tmp_path,
    )
    assert "Make an API" in prompt
    assert "GET /health" in prompt
    assert "Contract expectations" in prompt

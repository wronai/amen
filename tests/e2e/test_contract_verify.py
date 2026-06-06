"""Tests for contract verify readiness probing."""

from unittest.mock import patch

import yaml

from generator.contract_verify import readiness_paths, wait_for_service


SAMPLE_LIVE_READY = """
INTENT:
  name: items-api
IMPLEMENTATION:
  actions:
    - api.expose GET /live
    - api.expose GET /ready
    - api.expose GET /api/v1/items
"""


def test_readiness_paths_from_intent():
    data = yaml.safe_load(SAMPLE_LIVE_READY)
    paths = readiness_paths(data)
    assert "/live" in paths
    assert "/ready" in paths
    assert "/api/v1/items" in paths
    assert "/ping" not in paths


def test_wait_for_service_accepts_http_404_as_up():
    data = yaml.safe_load(SAMPLE_LIVE_READY)
    with patch(
        "generator.contract_verify._endpoint_responding",
        side_effect=lambda _url, path: path == "/live",
    ):
        assert wait_for_service("http://localhost:9999", attempts=1, intent_data=data)


def test_wait_for_service_default_includes_live_ready():
    paths = readiness_paths(None)
    assert "/live" in paths
    assert "/ready" in paths

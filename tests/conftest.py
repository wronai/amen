"""
Pytest configuration for INTENT-ITERATIVE tests.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def project_root():
    """Return project root path."""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_dsl():
    """Return sample DSL content for testing."""
    return """
INTENT:
  name: test-api
  goal: Test API service

ENVIRONMENT:
  runtime: docker
  base_image: python:3.12-slim

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /ping
    - api.expose GET /health

EXECUTION:
  mode: dry-run
"""


@pytest.fixture
def sample_ir():
    """Return sample IR for testing."""
    from ir.models import IntentIR, Intent, Environment, Implementation, Action, ActionType
    
    ir = IntentIR()
    ir.intent = Intent(name="test", goal="Test goal")
    ir.implementation = Implementation(
        language="python",
        framework="fastapi",
        actions=[
            Action(type=ActionType.API_EXPOSE, method="GET", target="/ping")
        ]
    )
    return ir

"""Pipeline result types (shared without importing pipeline integrations)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from generator.intent_generator import GenerateResult


@dataclass
class PipelineResult:
    success: bool
    prompt: str
    generate: GenerateResult | None = None
    plan: dict[str, Any] | None = None
    execution: dict[str, Any] | None = None
    verification: dict[str, Any] | None = None
    verify_iterations: int = 0
    yaml_path: str | None = None
    workspace: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "prompt": self.prompt,
            "generate": self.generate.to_dict() if self.generate else None,
            "plan": self.plan,
            "execution": self.execution,
            "verification": self.verification,
            "verify_iterations": self.verify_iterations,
            "yaml_path": self.yaml_path,
            "workspace": self.workspace,
            "error": self.error,
        }

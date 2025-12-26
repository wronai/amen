"""
INTENT-ITERATIVE: Intermediate Representation (IR) Models
Canonical data structures for the entire system.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import json
import uuid
from datetime import datetime


class ExecutionMode(Enum):
    DRY_RUN = "dry-run"
    TRANSACTIONAL = "transactional"


class RuntimeType(Enum):
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    LOCAL = "local"


class ActionType(Enum):
    API_EXPOSE = "api.expose"
    DB_CREATE = "db.create"
    DB_ADD_COLUMN = "db.add_column"
    SHELL_EXEC = "shell.exec"
    REST_CALL = "rest.call"
    FILE_CREATE = "file.create"


@dataclass
class Action:
    """Single action in the implementation plan."""
    type: ActionType
    method: Optional[str] = None  # GET, POST, etc.
    target: Optional[str] = None  # endpoint, table, file
    params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "method": self.method,
            "target": self.target,
            "params": self.params
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Action":
        return cls(
            type=ActionType(data["type"]),
            method=data.get("method"),
            target=data.get("target"),
            params=data.get("params", {})
        )


@dataclass
class Environment:
    """Runtime environment configuration."""
    runtime: RuntimeType = RuntimeType.DOCKER
    base_image: str = "python:3.12-slim"
    services: List[str] = field(default_factory=list)
    ports: List[int] = field(default_factory=list)
    volumes: List[str] = field(default_factory=list)
    env_vars: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "runtime": self.runtime.value,
            "base_image": self.base_image,
            "services": self.services,
            "ports": self.ports,
            "volumes": self.volumes,
            "env_vars": self.env_vars
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Environment":
        return cls(
            runtime=RuntimeType(data.get("runtime", "docker")),
            base_image=data.get("base_image", "python:3.12-slim"),
            services=data.get("services", []),
            ports=data.get("ports", []),
            volumes=data.get("volumes", []),
            env_vars=data.get("env_vars", {})
        )


@dataclass
class Implementation:
    """Implementation details."""
    language: str = "python"
    framework: Optional[str] = None
    actions: List[Action] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "language": self.language,
            "framework": self.framework,
            "actions": [a.to_dict() for a in self.actions]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Implementation":
        return cls(
            language=data.get("language", "python"),
            framework=data.get("framework"),
            actions=[Action.from_dict(a) for a in data.get("actions", [])]
        )


@dataclass
class Intent:
    """Main intent definition."""
    name: str
    goal: str
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "goal": self.goal,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Intent":
        return cls(
            name=data["name"],
            goal=data["goal"],
            description=data.get("description")
        )


@dataclass
class IntentIR:
    """
    Complete Intermediate Representation for an intent.
    This is the canonical representation used by all system modules.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    version: int = 1
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    intent: Intent = field(default_factory=lambda: Intent(name="", goal=""))
    environment: Environment = field(default_factory=Environment)
    implementation: Implementation = field(default_factory=Implementation)
    execution_mode: ExecutionMode = ExecutionMode.DRY_RUN
    
    # Execution state
    amen_approved: bool = False
    iteration_count: int = 0
    iteration_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Generated artifacts
    generated_code: Optional[str] = None
    dockerfile: Optional[str] = None
    dry_run_logs: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "intent": self.intent.to_dict(),
            "environment": self.environment.to_dict(),
            "implementation": self.implementation.to_dict(),
            "execution_mode": self.execution_mode.value,
            "amen_approved": self.amen_approved,
            "iteration_count": self.iteration_count,
            "iteration_history": self.iteration_history,
            "generated_code": self.generated_code,
            "dockerfile": self.dockerfile,
            "dry_run_logs": self.dry_run_logs
        }
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntentIR":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            version=data.get("version", 1),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            intent=Intent.from_dict(data.get("intent", {})),
            environment=Environment.from_dict(data.get("environment", {})),
            implementation=Implementation.from_dict(data.get("implementation", {})),
            execution_mode=ExecutionMode(data.get("execution_mode", "dry-run")),
            amen_approved=data.get("amen_approved", False),
            iteration_count=data.get("iteration_count", 0),
            iteration_history=data.get("iteration_history", []),
            generated_code=data.get("generated_code"),
            dockerfile=data.get("dockerfile"),
            dry_run_logs=data.get("dry_run_logs", [])
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "IntentIR":
        return cls.from_dict(json.loads(json_str))
    
    def add_iteration(self, changes: Dict[str, Any], source: str = "user"):
        """Record an iteration in history."""
        self.iteration_count += 1
        self.updated_at = datetime.now().isoformat()
        self.iteration_history.append({
            "iteration": self.iteration_count,
            "timestamp": self.updated_at,
            "source": source,
            "changes": changes
        })
    
    def approve_amen(self):
        """Approve execution (AMEN boundary)."""
        self.amen_approved = True
        self.execution_mode = ExecutionMode.TRANSACTIONAL
        self.updated_at = datetime.now().isoformat()

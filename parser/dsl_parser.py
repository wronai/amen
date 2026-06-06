"""
ITERUN: DSL Parser
Parses YAML DSL files into Intermediate Representation (IR).
"""

import yaml
import re
from typing import Dict, Any, List, Tuple
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from ir.models import (
    IntentIR, Intent, Environment, Implementation, Action,
    ExecutionMode, RuntimeType, ActionType, Stack, StackService,
)


class ParseError(Exception):
    """Raised when DSL parsing fails."""
    def __init__(self, message: str, line: int = None):
        self.message = message
        self.line = line
        super().__init__(f"Parse error{f' at line {line}' if line else ''}: {message}")


class ValidationError(Exception):
    """Raised when DSL validation fails."""
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"Validation failed: {'; '.join(errors)}")


class DSLParser:
    """
    Parser for ITERUN DSL format.
    
    Example DSL:
    ```yaml
    INTENT:
      name: my-api
      goal: Create REST API
    
    ENVIRONMENT:
      runtime: docker
      base_image: python:3.12
    
    IMPLEMENTATION:
      language: python
      framework: fastapi
      actions:
        - api.expose GET /ping
        - api.expose POST /users
    
    EXECUTION:
      mode: dry-run
    ```
    """
    
    # Action pattern: type METHOD target [params...]
    ACTION_PATTERN = re.compile(
        r'^(?P<type>[\w.]+)\s+'
        r'(?:(?P<method>GET|POST|PUT|DELETE|PATCH)\s+)?'
        r'(?P<target>\S+)'
        r'(?:\s+(?P<params>.+))?$'
    )
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def parse_file(self, filepath: str) -> IntentIR:
        """Parse DSL file and return IR."""
        with open(filepath, 'r') as f:
            content = f.read()
        return self.parse(content)
    
    def parse(self, dsl_content: str) -> IntentIR:
        """Parse DSL string and return IR."""
        self.errors = []
        self.warnings = []
        
        try:
            data = yaml.safe_load(dsl_content)
        except yaml.YAMLError as e:
            raise ParseError(f"Invalid YAML: {e}")
        
        if not data:
            raise ParseError("Empty DSL content")
        
        # Parse sections
        ir = IntentIR()
        
        if "INTENT" in data:
            ir.intent = self._parse_intent(data["INTENT"])
        else:
            self.errors.append("Missing required section: INTENT")
        
        if "ENVIRONMENT" in data:
            ir.environment = self._parse_environment(data["ENVIRONMENT"])
        
        if "IMPLEMENTATION" in data:
            ir.implementation = self._parse_implementation(data["IMPLEMENTATION"])

        if "STACK" in data:
            ir.stack = self._parse_stack(data["STACK"])
        
        if "EXECUTION" in data:
            ir.execution_mode = self._parse_execution(data["EXECUTION"])
        
        # Validate
        self._validate(ir)
        
        if self.errors:
            raise ValidationError(self.errors)
        
        return ir
    
    def _parse_intent(self, data: Dict[str, Any]) -> Intent:
        """Parse INTENT section."""
        if not isinstance(data, dict):
            self.errors.append("INTENT must be a dictionary")
            return Intent(name="", goal="")
        
        name = data.get("name", "")
        goal = data.get("goal", "")
        
        if not name:
            self.errors.append("INTENT.name is required")
        if not goal:
            self.errors.append("INTENT.goal is required")
        
        return Intent(
            name=name,
            goal=goal,
            description=data.get("description")
        )
    
    def _parse_environment(self, data: Dict[str, Any]) -> Environment:
        """Parse ENVIRONMENT section."""
        if not isinstance(data, dict):
            self.errors.append("ENVIRONMENT must be a dictionary")
            return Environment()
        
        runtime_str = data.get("runtime", "docker")
        try:
            runtime = RuntimeType(runtime_str)
        except ValueError:
            self.warnings.append(f"Unknown runtime '{runtime_str}', defaulting to docker")
            runtime = RuntimeType.DOCKER
        
        return Environment(
            runtime=runtime,
            base_image=data.get("base_image", "python:3.12-slim"),
            services=data.get("services", []),
            ports=data.get("ports", []),
            volumes=data.get("volumes", []),
            env_vars=data.get("env_vars", {})
        )
    
    def _parse_implementation(self, data: Dict[str, Any]) -> Implementation:
        """Parse IMPLEMENTATION section."""
        if not isinstance(data, dict):
            self.errors.append("IMPLEMENTATION must be a dictionary")
            return Implementation()
        
        actions = []
        for action_str in data.get("actions", []):
            action = self._parse_action(action_str)
            if action:
                actions.append(action)
        
        return Implementation(
            language=data.get("language", "python"),
            framework=data.get("framework"),
            actions=actions
        )
    
    def _parse_action(self, action_str: str) -> Action | None:
        """Parse single action string."""
        if isinstance(action_str, dict):
            # Handle dict format
            try:
                return Action(
                    type=ActionType(action_str.get("type", "")),
                    method=action_str.get("method"),
                    target=action_str.get("target"),
                    params=action_str.get("params", {})
                )
            except ValueError as e:
                self.errors.append(f"Invalid action type: {e}")
                return None
        
        # Parse string format: "api.expose GET /ping"
        match = self.ACTION_PATTERN.match(str(action_str).strip())
        if not match:
            self.errors.append(f"Invalid action format: '{action_str}'")
            return None
        
        action_type_str = match.group("type")
        try:
            action_type = ActionType(action_type_str)
        except ValueError:
            self.errors.append(f"Unknown action type: '{action_type_str}'")
            return None
        
        params = {}
        params_str = match.group("params")
        if params_str:
            # Simple key=value parsing
            for part in params_str.split():
                if "=" in part:
                    k, v = part.split("=", 1)
                    params[k] = v
                else:
                    params[part] = True
        
        return Action(
            type=action_type,
            method=match.group("method"),
            target=match.group("target"),
            params=params
        )
    
    def _parse_stack(self, data: Dict[str, Any]) -> Stack:
        if not isinstance(data, dict):
            self.errors.append("STACK must be a dictionary")
            return Stack()

        services_raw = data.get("services") or {}
        if not isinstance(services_raw, dict):
            self.errors.append("STACK.services must be a dictionary")
            return Stack(network=data.get("network", "app-net"))

        services: list[StackService] = []
        for name, svc_data in services_raw.items():
            if not isinstance(svc_data, dict):
                self.errors.append(f"STACK.services.{name} must be a dictionary")
                continue
            actions = []
            for action_str in svc_data.get("actions", []) or []:
                action = self._parse_action(action_str)
                if action:
                    actions.append(action)
            image = svc_data.get("image")
            language = svc_data.get("language")
            if not image and not language:
                self.errors.append(
                    f"STACK.services.{name}: require language or image"
                )
            services.append(
                StackService(
                    name=name,
                    language=language,
                    framework=svc_data.get("framework"),
                    image=image,
                    base_image=svc_data.get("base_image"),
                    port=int(svc_data.get("port", 8000)),
                    host_port=svc_data.get("host_port"),
                    depends_on=list(svc_data.get("depends_on", []) or []),
                    env_vars=dict(svc_data.get("env_vars", {}) or {}),
                    actions=actions,
                )
            )

        if len(services) < 2:
            self.errors.append("STACK requires at least 2 services")

        return Stack(network=data.get("network", "app-net"), services=services)

    def _parse_execution(self, data: Dict[str, Any]) -> ExecutionMode:
        """Parse EXECUTION section."""
        if not isinstance(data, dict):
            self.errors.append("EXECUTION must be a dictionary")
            return ExecutionMode.DRY_RUN
        
        mode_str = data.get("mode", "dry-run")
        try:
            return ExecutionMode(mode_str)
        except ValueError:
            self.warnings.append(f"Unknown execution mode '{mode_str}', defaulting to dry-run")
            return ExecutionMode.DRY_RUN
    
    def _validate_stack_services(self, ir: IntentIR) -> bool:
        if not ir.stack or not ir.stack.services:
            return False
        svc_names = {s.name for s in ir.stack.services}
        for svc in ir.stack.services:
            for dep in svc.depends_on:
                if dep not in svc_names:
                    self.errors.append(
                        f"STACK.services.{svc.name}: unknown depends_on {dep!r}"
                    )
            if svc.framework == "fastapi" and svc.language not in (None, "python"):
                self.errors.append(f"STACK.services.{svc.name}: FastAPI requires python")
            if svc.framework == "express" and svc.language not in (None, "node"):
                self.errors.append(f"STACK.services.{svc.name}: Express requires node")
        return not ir.implementation.actions

    def _validate_actions_required(self, ir: IntentIR) -> None:
        if not ir.stack and not ir.implementation.actions:
            self.errors.append("IMPLEMENTATION.actions or STACK.services is required")

    def _validate_dangerous_actions(self, ir: IntentIR) -> None:
        for action in ir.implementation.actions:
            if action.type == ActionType.SHELL_EXEC and "root" in str(action.params).lower():
                self.warnings.append(
                    f"Action '{action.target}' may run as root - review carefully"
                )

    def _validate_framework_compat(self, ir: IntentIR) -> None:
        impl = ir.implementation
        if impl.framework == "fastapi" and impl.language != "python":
            self.errors.append("FastAPI requires Python language")
        if impl.framework == "express" and impl.language != "node":
            self.errors.append("Express requires Node.js language")

    def _validate(self, ir: IntentIR):
        """Validate the parsed IR."""
        if self._validate_stack_services(ir):
            return
        self._validate_actions_required(ir)
        self._validate_dangerous_actions(ir)
        self._validate_framework_compat(ir)


def parse_dsl(content: str) -> IntentIR:
    """Convenience function to parse DSL content."""
    parser = DSLParser()
    return parser.parse(content)


def parse_dsl_file(filepath: str) -> IntentIR:
    """Convenience function to parse DSL file."""
    parser = DSLParser()
    return parser.parse_file(filepath)

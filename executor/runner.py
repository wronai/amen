"""
INTENT-ITERATIVE: Executor
Handles actual execution of approved intents (after AMEN boundary).
"""

import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from ir.models import IntentIR, ExecutionMode, RuntimeType
from config import get_config


class ExecutionError(Exception):
    """Raised when execution fails."""
    pass


class ExecutionResult:
    """Result of intent execution."""
    def __init__(self):
        self.success: bool = False
        self.logs: List[str] = []
        self.artifacts: Dict[str, str] = {}  # filename -> path
        self.container_id: Optional[str] = None
        self.endpoints: List[str] = []
        self.error: Optional[str] = None
        self.execution_time: float = 0.0
    
    def add_log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "logs": self.logs,
            "artifacts": self.artifacts,
            "container_id": self.container_id,
            "endpoints": self.endpoints,
            "error": self.error,
            "execution_time": self.execution_time
        }


class Executor:
    """
    Executes approved intents.
    Only runs after AMEN boundary is passed.
    """
    
    def __init__(self, workspace: str = None):
        self.config = get_config()
        workspace = workspace or self.config.workspace_dir
        self.workspace = Path(workspace) if workspace else Path(tempfile.mkdtemp(prefix="intent-"))
        self.workspace.mkdir(parents=True, exist_ok=True)
    
    def execute(self, ir: IntentIR, skip_amen_check: bool = None) -> ExecutionResult:
        """Execute an approved intent."""
        result = ExecutionResult()
        start_time = datetime.now()
        
        # Check if we should skip AMEN check
        skip_check = skip_amen_check if skip_amen_check is not None else self.config.skip_amen_confirmation
        
        # Check AMEN approval (unless skipped)
        if not skip_check:
            if not ir.amen_approved:
                result.error = "Intent not approved. Call approve_amen() first."
                result.add_log("ERROR: Execution blocked - AMEN boundary not passed")
                return result
            
            if ir.execution_mode != ExecutionMode.TRANSACTIONAL:
                result.error = "Intent is in dry-run mode. Change to transactional mode."
                result.add_log("ERROR: Execution blocked - still in dry-run mode")
                return result
        else:
            # Auto-approve if skipping check
            if not ir.amen_approved:
                ir.approve_amen()
                result.add_log("Auto-approved intent (SKIP_AMEN_CONFIRMATION=true)")
        
        result.add_log(f"Starting execution for: {ir.intent.name}")
        result.add_log(f"Workspace: {self.workspace}")
        
        try:
            # Write generated files
            self._write_artifacts(ir, result)
            
            # Execute based on runtime
            if ir.environment.runtime == RuntimeType.DOCKER:
                self._execute_docker(ir, result)
            elif ir.environment.runtime == RuntimeType.LOCAL:
                self._execute_local(ir, result)
            else:
                result.add_log(f"Runtime {ir.environment.runtime.value} not yet supported")
                result.error = f"Unsupported runtime: {ir.environment.runtime.value}"
            
            if not result.error:
                result.success = True
                result.add_log("Execution completed successfully")
        
        except Exception as e:
            result.error = str(e)
            result.add_log(f"ERROR: {e}")
        
        result.execution_time = (datetime.now() - start_time).total_seconds()
        return result
    
    def _write_artifacts(self, ir: IntentIR, result: ExecutionResult):
        """Write generated code and config files."""
        lang = ir.implementation.language
        
        # Main application file
        if ir.generated_code:
            if lang == "python":
                app_file = self.workspace / "app.py"
            elif lang == "node":
                app_file = self.workspace / "app.js"
            else:
                app_file = self.workspace / "app.txt"
            
            app_file.write_text(ir.generated_code)
            result.artifacts["app"] = str(app_file)
            result.add_log(f"Written: {app_file.name}")
        
        # Dockerfile
        if ir.dockerfile:
            dockerfile = self.workspace / "Dockerfile"
            dockerfile.write_text(ir.dockerfile)
            result.artifacts["Dockerfile"] = str(dockerfile)
            result.add_log("Written: Dockerfile")
        
        # Package files
        if lang == "node":
            package_json = self.workspace / "package.json"
            deps = {}
            if ir.implementation.framework == "express":
                deps["express"] = "^4.18.0"
            
            package_content = {
                "name": ir.intent.name,
                "version": "1.0.0",
                "main": "app.js",
                "dependencies": deps
            }
            
            import json
            package_json.write_text(json.dumps(package_content, indent=2))
            result.artifacts["package.json"] = str(package_json)
            result.add_log("Written: package.json")
    
    def _find_available_port(self, start_port: int = 8000) -> int:
        """Find an available port starting from start_port."""
        import socket
        port = start_port
        max_attempts = 100
        
        for _ in range(max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                port += 1
        
        return start_port + max_attempts  # Fallback
    
    def _execute_docker(self, ir: IntentIR, result: ExecutionResult):
        """Build and run Docker container."""
        prefix = self.config.container_prefix
        image_name = f"{prefix}-{ir.intent.name}:latest"
        container_name = f"{prefix}-{ir.intent.name}-{ir.id}"
        
        # Find available port
        requested_port = self.config.container_port
        if ir.environment.ports:
            requested_port = ir.environment.ports[0]
        
        host_port = self._find_available_port(requested_port)
        if host_port != requested_port:
            result.add_log(f"Port {requested_port} in use, using {host_port}")
        
        result.add_log(f"Building Docker image: {image_name}")
        
        # Build image
        build_cmd = ["docker", "build", "-t", image_name, str(self.workspace)]
        build_result = subprocess.run(
            build_cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if build_result.returncode != 0:
            result.error = f"Docker build failed: {build_result.stderr}"
            result.add_log(f"Build error: {build_result.stderr[:500]}")
            return
        
        result.add_log("Docker image built successfully")
        
        # Stop existing container with same name if exists
        subprocess.run(
            ["docker", "rm", "-f", container_name],
            capture_output=True,
            timeout=30
        )
        
        # Run container
        container_port = self.config.container_port
        run_cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "-p", f"{host_port}:{container_port}",
        ]
        
        # Add environment variables
        for key, value in ir.environment.env_vars.items():
            run_cmd.extend(["-e", f"{key}={value}"])
        
        # Add additional ports
        for port in ir.environment.ports:
            if port != container_port:
                extra_host_port = self._find_available_port(port)
                run_cmd.extend(["-p", f"{extra_host_port}:{port}"])
        
        run_cmd.append(image_name)
        
        result.add_log(f"Starting container: {container_name}")
        
        run_result = subprocess.run(
            run_cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if run_result.returncode != 0:
            result.error = f"Docker run failed: {run_result.stderr}"
            result.add_log(f"Run error: {run_result.stderr[:500]}")
            return
        
        result.container_id = run_result.stdout.strip()[:12]
        result.add_log(f"Container started: {result.container_id}")
        
        # Record endpoints
        result.endpoints.append(f"http://localhost:{host_port}")
        for action in ir.implementation.actions:
            if action.type.value == "api.expose":
                result.endpoints.append(f"http://localhost:{host_port}{action.target}")
    
    def _execute_local(self, ir: IntentIR, result: ExecutionResult):
        """Execute locally without Docker."""
        lang = ir.implementation.language
        app_file = result.artifacts.get("app")
        
        if not app_file:
            result.error = "No application file generated"
            return
        
        result.add_log(f"Starting local execution: {app_file}")
        
        if lang == "python":
            cmd = ["python", app_file]
        elif lang == "node":
            cmd = ["node", app_file]
        else:
            result.error = f"Unsupported language for local execution: {lang}"
            return
        
        # Start as background process
        result.add_log(f"Command: {' '.join(cmd)}")
        result.add_log("Application would start here (non-blocking in production)")
        
        # In production, we'd use subprocess.Popen for non-blocking execution
        port = self._find_available_port(self.config.container_port)
        result.endpoints.append(f"http://localhost:{port}")
    
    def cleanup(self):
        """Clean up workspace."""
        if self.workspace.exists():
            shutil.rmtree(self.workspace)


def execute_intent(ir: IntentIR, workspace: str = None, skip_amen_check: bool = None) -> ExecutionResult:
    """Convenience function to execute an approved intent."""
    executor = Executor(workspace)
    return executor.execute(ir, skip_amen_check=skip_amen_check)

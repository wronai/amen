"""Terminal output helpers for CLI execution results."""

from __future__ import annotations

from pathlib import Path

from cli.colors import Colors
from executor.docker_ops import get_container_logs
from executor.models import ExecutionResult


def log_status_color(log: str) -> str:
    if "✓" in log or "success" in log.lower():
        return Colors.GREEN
    if "✗" in log or "error" in log.lower() or "ERROR" in log:
        return Colors.RED
    if "⚠" in log or "warning" in log.lower():
        return Colors.YELLOW
    return Colors.RESET


def print_execution_logs(result: ExecutionResult) -> None:
    print(f"\n{Colors.BOLD}Execution Logs:{Colors.RESET}")
    for log in result.logs:
        status = log_status_color(log)
        print(f"  {status}{log}{Colors.RESET}")


def print_validation_success(result: ExecutionResult) -> None:
    print(f"\n{Colors.BOLD}Validation:{Colors.RESET}")
    if result.validation.success:
        print(f"  {Colors.GREEN}✓ All endpoints validated{Colors.RESET}")
        return
    print(f"  {Colors.YELLOW}⚠ Some issues detected{Colors.RESET}")
    for check in result.validation.checks:
        if check["ok"]:
            print(f"    {Colors.GREEN}✓{Colors.RESET} {check['endpoint']}")
        else:
            err = check.get("error", "Failed")
            print(f"    {Colors.RED}✗{Colors.RESET} {check['endpoint']} - {err}")


def print_execution_success(cli, result: ExecutionResult) -> None:
    cli.print_success(f"Execution completed in {result.execution_time:.2f}s")
    if result.container_id:
        print(f"\n{Colors.BOLD}Container ID:{Colors.RESET} {result.container_id}")
    if result.endpoints:
        print(f"\n{Colors.BOLD}Available Endpoints:{Colors.RESET}")
        for endpoint in result.endpoints:
            print(f"  → {endpoint}")
    if result.artifacts:
        print(f"\n{Colors.BOLD}Generated Artifacts:{Colors.RESET}")
        for name, path in result.artifacts.items():
            print(f"  {name}: {path}")
    if result.validation:
        print_validation_success(result)
    if result.auto_fix_applied:
        print(
            f"\n{Colors.CYAN}Auto-fix applied "
            f"({result.fix_iterations} iteration(s)){Colors.RESET}"
        )


def print_validation_errors(result: ExecutionResult) -> None:
    if not result.validation:
        return
    if result.validation.errors:
        print(f"\n{Colors.BOLD}Validation Errors:{Colors.RESET}")
        for error in result.validation.errors:
            print(f"  {Colors.RED}✗{Colors.RESET} {error}")
    if result.validation.suggestions:
        print(f"\n{Colors.BOLD}Suggestions:{Colors.RESET}")
        for suggestion in result.validation.suggestions:
            print(f"  • {suggestion}")


def print_container_logs(workspace: str | None, container_id: str) -> None:
    try:
        from config import get_config

        ws = Path(workspace) if workspace else Path(get_config().workspace_dir or ".")
        logs = get_container_logs(ws, container_id, tail=20)
        if not logs:
            return
        print(f"\n{Colors.BOLD}Container Logs:{Colors.RESET}")
        for line in logs.split("\n")[-10:]:
            if line.strip():
                print(f"  {line}")
    except Exception:
        pass


def print_execution_failure(cli, result: ExecutionResult, workspace: str | None) -> None:
    cli.print_error(f"Execution failed: {result.error}")
    print_validation_errors(result)
    if result.container_id:
        print_container_logs(workspace, result.container_id)

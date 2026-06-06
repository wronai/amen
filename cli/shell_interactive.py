"""Interactive shell command dispatch."""

from __future__ import annotations

from typing import Callable

from cli.colors import Colors


def _dispatch_basic(cli, cmd: str, args: str) -> bool:
    handlers: dict[str, Callable[[], None]] = {
        "plan": lambda: cli.cmd_plan(),
        "iterate": lambda: cli.cmd_iterate(),
        "iterun": lambda: cli.cmd_iterun(),
    }
    if cmd in handlers:
        handlers[cmd]()
        return True
    if cmd in ("exec", "execute", "run"):
        cli.cmd_execute()
        return True
    if cmd == "new":
        cli.cmd_new(args or "my-intent")
        return True
    if cmd == "load":
        if args:
            cli.cmd_load(args)
        else:
            cli.print_error("Usage: load <filepath>")
        return True
    if cmd == "show":
        cli.cmd_show(format=args or "summary")
        return True
    if cmd == "save":
        if args:
            cli.cmd_save(args)
        else:
            cli.print_error("Usage: save <filepath>")
        return True
    if cmd == "help":
        cli._show_help()
        return True
    return False


def _dispatch_ai(cli, cmd: str, args: str, ai_available: bool) -> bool:
    if not ai_available:
        return False
    if cmd == "suggest":
        cli.cmd_ai_suggest(focus=args if args else None)
        return True
    if cmd == "apply":
        cli.cmd_ai_apply()
        return True
    if cmd == "chat":
        cli.cmd_ai_chat(message=args if args else None)
        return True
    if cmd == "models":
        max_p = float(args) if args else 12.0
        cli.cmd_models(max_p)
        return True
    if cmd in ("ai-health", "aihealth", "health"):
        cli.cmd_ai_health()
        return True
    return False


def handle_interactive_line(cli, line: str, *, ai_available: bool) -> str | None:
    """Process one shell line. Returns 'exit' to stop the loop."""
    if not line:
        return None
    parts = line.split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    if cmd in ("exit", "quit", "q"):
        print("Goodbye!")
        return "exit"
    if _dispatch_basic(cli, cmd, args):
        return None
    if _dispatch_ai(cli, cmd, args, ai_available):
        return None
    cli.print_error(f"Unknown command: {cmd}")
    print("Type 'help' for available commands.")
    return None


def build_prompt(cli) -> str:
    prompt = f"{Colors.BOLD}intent{Colors.RESET}"
    if cli.current_ir:
        prompt += f":{Colors.CYAN}{cli.current_ir.intent.name}{Colors.RESET}"
    return prompt + "> "

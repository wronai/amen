#!/bin/bash
# Multi-service STACK examples (docker compose).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ ! -f "$REPO_ROOT/pyproject.toml" ] || ! grep -q 'name = "iterun"' "$REPO_ROOT/pyproject.toml" 2>/dev/null; then
    echo "ERROR: run-stacks.sh należy uruchomić z repo iterun (np. ~/github/wronai/iterun), nie z koru." >&2
    echo "  cd ~/github/wronai/iterun && ./examples/run-stacks.sh" >&2
    exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
    echo "Docker required for run-stacks.sh" >&2
    exit 1
fi

echo "=== ITERUN STACK examples (N Dockerfiles + compose) ==="
failed=0
for ex in 17-stack-shop-gateway 18-stack-blog 19-stack-api-cache; do
    echo "--- $ex ---"
    ITERUN_EXECUTE=1 bash "$SCRIPT_DIR/$ex/run.sh" || failed=1
done

if [ "$failed" -ne 0 ]; then
    echo "=== STACK FAILED ===" >&2
    exit 1
fi
echo "=== STACK OK (3 examples) ==="

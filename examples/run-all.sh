#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -z "${OPENROUTER_API_KEY:-}" ] && [ -z "${OLLAMA_API_BASE:-}" ]; then
    echo "WARN: Set OPENROUTER_API_KEY (or Ollama) in .env — examples use LLM generate" >&2
fi

echo "=== ITERUN examples (prompt → generate → plan) ==="
failed=0
for ex in 01-user-api 02-ping-smoke 03-flask-api 04-express-api 05-ir-show 06-iterate-workflow 07-execution-smoke 08-llm-generate; do
    if [ "$ex" = "07-execution-smoke" ]; then
        ITERUN_EXECUTE=0 bash "$SCRIPT_DIR/$ex/run.sh" || failed=1
    else
        bash "$SCRIPT_DIR/$ex/run.sh" || failed=1
    fi
done

if [ "$failed" -ne 0 ]; then
    echo "=== FAILED ===" >&2
    exit 1
fi
echo "=== OK (8 examples) ==="

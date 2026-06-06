#!/bin/bash
# Generuj intent.yaml z promptu NL (LiteLLM) → plan → opcjonalnie execute.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../_common.sh"
_example_setup "$SCRIPT_DIR"

if [ "${ITERUN_EXECUTE:-0}" = "1" ]; then
    _example_generate execute
else
    _example_generate plan
fi

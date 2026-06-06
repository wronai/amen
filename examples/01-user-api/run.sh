#!/bin/bash
# LLM prompt → iterun.yaml → plan (+ opcjonalne execute Docker).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=../_common.sh
source "$SCRIPT_DIR/../_common.sh"
_example_setup "$SCRIPT_DIR"

if [ "${ITERUN_EXECUTE:-0}" = "1" ]; then
    _example_generate execute
else
    _example_generate plan
fi

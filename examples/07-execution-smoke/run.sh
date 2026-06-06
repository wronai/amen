#!/bin/bash
# Smoke: generate+plan własnego intentu + 02/03/04; execute gdy ITERUN_EXECUTE=1.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../_common.sh"
_example_setup "$SCRIPT_DIR"

if [ "${ITERUN_EXECUTE:-0}" = "1" ] && command -v docker >/dev/null 2>&1; then
    _example_generate execute
else
    _example_generate plan
fi

for sub in 02-ping-smoke 03-flask-api 04-express-api; do
    _example_generate_dir "$EXAMPLES_ROOT/$sub" plan
done

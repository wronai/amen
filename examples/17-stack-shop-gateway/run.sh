#!/bin/bash
# STACK: gateway + users + catalog → docker-compose.yaml + 3 Dockerfiles
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../_common.sh"
_example_setup "$SCRIPT_DIR"
_example_use_source_pkg

$CLI plan "$ITERUN_PKG" --output-dir "$GENERATED" --quiet

if [ "${ITERUN_EXECUTE:-1}" = "1" ] && command -v docker >/dev/null 2>&1; then
    $CLI execute "$ITERUN_PKG" --workspace "$GENERATED" --quiet
    echo "OK stack running — gateway http://localhost:18080"
else
    echo "OK stack planned in $GENERATED (set ITERUN_EXECUTE=1 for docker compose)"
fi

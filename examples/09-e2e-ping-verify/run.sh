#!/bin/bash
# prompt → generate → execute → intract + testql + expectations
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../_common.sh"
source "$SCRIPT_DIR/../_verify.sh"
_example_setup "$SCRIPT_DIR"

_example_generate execute
_example_e2e_verify

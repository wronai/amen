#!/bin/bash
# E2E examples: LLM + Docker + testql + intract (wolniejsze, wymagają narzędzi).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON="${PYTHON:-python3}"

# shellcheck source=_bootstrap_deps.sh
source "$SCRIPT_DIR/_bootstrap_deps.sh"
_example_ensure_e2e_deps || exit 1

echo "=== ITERUN e2e examples (prompt → execute → testql + intract) ==="
failed=0
for ex in 09-e2e-ping-verify 10-e2e-user-crud-verify 11-e2e-express-verify 12-e2e-full-gate; do
    echo "--- $ex ---"
    bash "$SCRIPT_DIR/$ex/run.sh" || failed=1
done

if [ "$failed" -ne 0 ]; then
    echo "=== E2E FAILED ===" >&2
    exit 1
fi
echo "=== E2E OK (4 examples) ==="

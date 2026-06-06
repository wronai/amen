#!/bin/bash
# E2E examples: LLM + Docker + testql + intract (wolniejsze, wymagają narzędzi).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if ! command -v docker >/dev/null 2>&1; then
    echo "Docker required for run-e2e.sh" >&2
    exit 1
fi
if ! command -v testql >/dev/null 2>&1; then
    echo "testql required: pip install testql" >&2
    exit 1
fi
if ! python3 -c "import intract" 2>/dev/null; then
    echo "intract required: pip install -e ../semcod/intract" >&2
    exit 1
fi

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

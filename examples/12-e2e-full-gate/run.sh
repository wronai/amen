#!/bin/bash
# Zaawansowany gate: generate → execute → intract graph → testql → testql auto → expectations
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../_common.sh"
source "$SCRIPT_DIR/../_verify.sh"
_example_setup "$SCRIPT_DIR"

_example_generate execute
_example_require_tools

_example_wait_service
_example_emit_contracts
_example_discover_url
_example_annotate_intract

# Intract: validate + graph + artifact scan (manifest w generated/intract.yaml)
"$PYTHON" -m intract validate "$GENERATED" --manifest "$GENERATED/intract.yaml"
"$PYTHON" -m intract graph "$GENERATED" --manifest "$GENERATED/intract.yaml" --format mermaid > "$GENERATED/intract.graph.mmd"
"$PYTHON" -m intract scan "$GENERATED" --all-artifacts --json > "$GENERATED/intract.artifacts.json"

# TestQL: ręczny scenariusz + auto z katalogu generated
_example_run_testql
testql auto "$GENERATED" --url "$SERVICE_URL" --format console --keep-generated

# Zgodność prompt ↔ intent ↔ HTTP
_example_verify_expectations

# JSON raport execute (jeśli jest)
if [ -f "$GENERATED/execution.json" ]; then
    "$PYTHON" - <<'PY' "$GENERATED/execution.json"
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
print("execution endpoints:", ", ".join(data.get("endpoints", [])[:5]))
PY
fi

echo "OK full gate passed at $SERVICE_URL"
echo "  graph: $GENERATED/intract.graph.mmd"
echo "  artifacts: $GENERATED/intract.artifacts.json"

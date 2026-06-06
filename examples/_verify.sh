# Wspólna weryfikacja e2e: generated/intract.yaml + generated/service.testql.toon.yaml
# shellcheck shell=bash

# shellcheck source=_bootstrap_deps.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_bootstrap_deps.sh"

_example_require_tools() {
    _example_ensure_e2e_deps
}

_example_intent_name() {
    python3 - <<'PY' "$INTENT"
import sys, yaml
data = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
print((data.get("INTENT") or {}).get("name", ""))
PY
}

_example_discover_url() {
    if [ -f "$GENERATED/verify.result.json" ]; then
        SERVICE_URL="$("$PYTHON" - <<'PY' "$GENERATED/verify.result.json"
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
print(data.get("service_url") or "")
PY
)"
        if [ -n "$SERVICE_URL" ]; then
            export SERVICE_URL
            return 0
        fi
    fi
    local intent_name
    intent_name="$(_example_intent_name)"
    local pattern="intent-${intent_name}"
    local port
    port="$(docker ps --filter "name=${pattern}" --format '{{.Ports}}' 2>/dev/null \
        | grep -oE '0\.0\.0\.0:([0-9]+)' | head -1 | cut -d: -f2)"
    if [ -z "$port" ]; then
        port="$(docker ps --filter "name=${pattern}" --format '{{.Ports}}' 2>/dev/null \
            | grep -oE '127\.0\.0\.1:([0-9]+)' | head -1 | cut -d: -f2)"
    fi
    if [ -z "$port" ]; then
        echo "No running container for ${pattern}" >&2
        return 1
    fi
    SERVICE_URL="http://localhost:${port}"
    export SERVICE_URL
}

_example_emit_openapi() {
    "$PYTHON" "$EXAMPLES_ROOT/_scripts/intent_to_openapi.py" \
        "$INTENT" -o "$GENERATED/openapi.yaml"
}

_example_wait_service() {
    _example_discover_url || return 1
    if ! "$PYTHON" -c "
from pathlib import Path
import sys, yaml
from generator.contract_verify import wait_for_service
url, intent = sys.argv[1], Path(sys.argv[2])
data = yaml.safe_load(intent.read_text(encoding='utf-8')) or {}
sys.exit(0 if wait_for_service(url, intent_data=data) else 1)
" "$SERVICE_URL" "$INTENT"; then
        echo "Service not ready at $SERVICE_URL" >&2
        return 1
    fi
}

_example_emit_contracts() {
    if [ ! -f "$INTENT" ]; then
        echo "Missing $INTENT for contract emit" >&2
        return 1
    fi
    _example_emit_openapi
    "$PYTHON" - <<'PY' "$INTENT" "$GENERATED"
from pathlib import Path
import sys
from generator.intract_manifest import write_intract_manifest
from generator.testql_scenario import write_testql_scenario

intent = Path(sys.argv[1])
gen = Path(sys.argv[2])
write_intract_manifest(intent, gen / "intract.yaml")
write_testql_scenario(intent, gen / "service.testql.toon.yaml")
PY
}

_example_annotate_intract() {
    local app_file=""
    if [ -f "$GENERATED/app.py" ]; then
        app_file="$GENERATED/app.py"
    elif [ -f "$GENERATED/app.js" ]; then
        app_file="$GENERATED/app.js"
    fi
    if [ -n "$app_file" ]; then
        "$PYTHON" "$EXAMPLES_ROOT/_scripts/annotate_intract.py" "$INTENT" "$app_file"
    fi
}

_example_run_intract() {
    local manifest="${1:-$GENERATED/intract.yaml}"
    if [ ! -f "$manifest" ]; then
        echo "Missing generated contract: $manifest (run generate --verify first)" >&2
        return 1
    fi
    _example_emit_openapi
    _example_annotate_intract
    "$PYTHON" -m intract validate "$GENERATED" --manifest "$manifest"
    "$PYTHON" -m intract scan "$GENERATED" --all-artifacts || true
}

_example_run_testql() {
    local scenario="${1:-$GENERATED/service.testql.toon.yaml}"
    if [ ! -f "$scenario" ]; then
        echo "Missing generated testql: $scenario" >&2
        return 1
    fi
    if ! command -v testql >/dev/null 2>&1; then
        echo "testql not installed — skipped (pip install testql)" >&2
        return 0
    fi
    _example_discover_url
    testql run "$scenario" --url "$SERVICE_URL" --output console --timeout 30000
}

_example_verify_expectations() {
    local expectations="${1:-$EXAMPLE_DIR/expectations.yaml}"
    if [ ! -f "$expectations" ]; then
        return 0
    fi
    local url_arg=()
    if [ -n "${SERVICE_URL:-}" ]; then
        url_arg=(--url "$SERVICE_URL")
    fi
    "$PYTHON" "$EXAMPLES_ROOT/_scripts/verify_expectations.py" \
        "$expectations" "$INTENT" "${url_arg[@]}"
}

_example_e2e_verify() {
    if [ "${ITERUN_SKIP_INTRACT:-}" = "1" ]; then
        _example_discover_url || return 1
        _example_run_testql
        _example_verify_expectations
        echo "OK e2e verified (pipeline + testql, intract skipped) at ${SERVICE_URL:-?}"
        return 0
    fi
    _example_require_tools || return 1
    if [ -f "$GENERATED/verify.result.json" ]; then
        if ! "$PYTHON" - <<'PY' "$GENERATED/verify.result.json"
import json, sys
ok = json.load(open(sys.argv[1], encoding="utf-8")).get("success")
sys.exit(0 if ok else 1)
PY
        then
            echo "Pipeline contract verify failed — see generated/verify.result.json" >&2
            return 1
        fi
    fi
    _example_discover_url || return 1
    _example_run_intract
    _example_run_testql
    _example_verify_expectations
    echo "OK e2e verified at $SERVICE_URL"
}

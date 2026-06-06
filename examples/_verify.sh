# Wspólna weryfikacja e2e: generated/intract.yaml + generated/service.testql.toon.yaml
# shellcheck shell=bash

_example_require_tools() {
    local missing=0
    for tool in docker; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            echo "Missing required tool: $tool" >&2
            missing=1
        fi
    done
    if ! "$PYTHON" -c "import intract" 2>/dev/null; then
        echo "Missing Python package: intract (pip install -e ../intract or pip install intract)" >&2
        missing=1
    fi
    if [ "$missing" -ne 0 ]; then
        return 1
    fi
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

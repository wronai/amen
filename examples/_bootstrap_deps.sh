# Opcjonalne zależności E2E (source z run-e2e.sh / run-resilience.sh / _verify.sh).
# shellcheck shell=bash

_example_find_intract_dir() {
    local root="${REPO_ROOT:-}"
    if [ -z "$root" ]; then
        root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    fi
    local candidates=(
        "${INTRACT_PATH:-}"
        "$root/../../semcod/intract"
        "$root/../semcod/intract"
        "$HOME/github/semcod/intract"
    )
    local c
    for c in "${candidates[@]}"; do
        [ -n "$c" ] && [ -f "$c/pyproject.toml" ] && echo "$c" && return 0
    done
    return 1
}

_example_ensure_intract() {
    if [ "${ITERUN_SKIP_INTRACT:-}" = "1" ]; then
        echo "WARN: ITERUN_SKIP_INTRACT=1 — pomijam intract" >&2
        return 0
    fi
    if "$PYTHON" -c "import intract" 2>/dev/null; then
        return 0
    fi
    local dir
    if ! dir="$(_example_find_intract_dir)"; then
        echo "Missing intract. Install one of:" >&2
        echo "  pip install -e /path/to/semcod/intract" >&2
        echo "  export INTRACT_PATH=/path/to/semcod/intract && ./examples/run-e2e.sh" >&2
        echo "  ITERUN_SKIP_INTRACT=1 ./examples/run-resilience.sh  # tylko pipeline --verify" >&2
        return 1
    fi
    echo "Installing intract from $dir ..." >&2
    "$PYTHON" -m pip install -e "$dir" -q
    "$PYTHON" -c "import intract"
}

_example_ensure_testql() {
    if command -v testql >/dev/null 2>&1; then
        return 0
    fi
    echo "Installing testql ..." >&2
    "$PYTHON" -m pip install testql -q
    command -v testql >/dev/null 2>&1
}

_example_ensure_e2e_deps() {
    PYTHON="${PYTHON:-python3}"
    command -v docker >/dev/null 2>&1 || {
        echo "Docker required" >&2
        return 1
    }
    _example_ensure_testql || {
        echo "testql required: pip install testql" >&2
        return 1
    }
    _example_ensure_intract
}

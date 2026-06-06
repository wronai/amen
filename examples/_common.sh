# Wspólne zmienne dla examples/*/run.sh (source, nie uruchamiaj bezpośrednio).
_example_setup() {
    local script_dir="$1"
    EXAMPLE_DIR="$(cd "$script_dir" && pwd)"
    REPO_ROOT="$(cd "$EXAMPLE_DIR/../.." && pwd)"
    EXAMPLES_ROOT="$(cd "$EXAMPLE_DIR/.." && pwd)"
    PROMPT_FILE="$EXAMPLE_DIR/prompt.txt"
    GENERATED="$EXAMPLE_DIR/generated"
    ITERUN_PKG="$GENERATED/iterun.yaml"
    INTENT="$ITERUN_PKG"
    PYTHON="${PYTHON:-python3}"
    CLI="$PYTHON -m cli"

    cd "$REPO_ROOT"
    mkdir -p "$GENERATED"

    if [ "${ITERUN_SKIP_CLEAN:-}" != "1" ]; then
        rm -rf "$GENERATED"/*
    fi
}

_example_read_prompt() {
    if [ -n "${ITERUN_PROMPT:-}" ]; then
        PROMPT="$ITERUN_PROMPT"
    elif [ -f "$PROMPT_FILE" ]; then
        PROMPT="$(cat "$PROMPT_FILE")"
    else
        echo "Missing prompt: $PROMPT_FILE" >&2
        exit 1
    fi
}

# generate → iterun.yaml (+ plan; opcjonalnie execute + verify)
_example_generate() {
    local mode="${1:-plan}"
    _example_read_prompt
    local extra_flags="--run"
    if [ "$mode" = "execute" ]; then
        extra_flags="--execute"
        if [ "${ITERUN_VERIFY:-1}" = "1" ]; then
            extra_flags="$extra_flags --verify"
        fi
    fi
    local max_verify="${ITERUN_MAX_VERIFY_ITERATIONS:-3}"
    # shellcheck disable=SC2086
    $CLI generate "$PROMPT" --output-dir "$GENERATED" $extra_flags --quiet \
        --max-iterations 5 --max-verify-iterations "$max_verify"
    ITERUN_PKG="$GENERATED/iterun.yaml"
    INTENT="$ITERUN_PKG"
}

_example_generate_dir() {
    local dir="$1"
    local mode="${2:-plan}"
    local prev_example_dir="$EXAMPLE_DIR"
    local prev_generated="$GENERATED"
    local prev_prompt_file="$PROMPT_FILE"
    local prev_intent="$INTENT"

    EXAMPLE_DIR="$(cd "$dir" && pwd)"
    PROMPT_FILE="$EXAMPLE_DIR/prompt.txt"
    GENERATED="$EXAMPLE_DIR/generated"
    mkdir -p "$GENERATED"
    if [ "${ITERUN_SKIP_CLEAN:-}" != "1" ]; then
        rm -rf "$GENERATED"/*
    fi
    _example_generate "$mode"

    EXAMPLE_DIR="$prev_example_dir"
    GENERATED="$prev_generated"
    PROMPT_FILE="$prev_prompt_file"
    INTENT="$prev_intent"
}

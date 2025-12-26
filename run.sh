#!/bin/bash
# INTENT-ITERATIVE startup script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load .env if exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Defaults
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8080}
DEFAULT_MODEL=${DEFAULT_MODEL:-llama3.2}

case "${1:-help}" in
    shell|cli)
        echo "Starting INTENT-ITERATIVE Shell..."
        python -m cli.main "${@:2}"
        ;;
    web|server|run)
        echo "Starting INTENT-ITERATIVE Web Server..."
        echo "→ http://${HOST}:${PORT}"
        python -m web.app
        ;;
    test|tests)
        echo "Running tests..."
        pytest tests/ -v "${@:2}"
        ;;
    test-shell)
        echo "Running shell tests..."
        pytest tests/e2e/test_shell.py -v "${@:2}"
        ;;
    test-web)
        echo "Running web tests..."
        pytest tests/e2e/test_web.py -v "${@:2}"
        ;;
    test-ai)
        echo "Running AI Gateway tests..."
        pytest tests/e2e/test_ai_gateway.py -v "${@:2}"
        ;;
    install)
        echo "Installing dependencies..."
        pip install -r requirements.txt
        ;;
    install-ai)
        echo "Installing AI Gateway dependencies (LiteLLM)..."
        pip install litellm
        ;;
    setup)
        echo "Full setup..."
        pip install -r requirements.txt
        pip install litellm
        [ ! -f .env ] && cp .env.example .env && echo "Created .env from .env.example"
        echo "Setup complete!"
        ;;
    plan)
        echo "Running dry-run..."
        python -m cli.main plan "${2:-examples/user-api.intent.yaml}"
        ;;
    execute|exec)
        echo "Executing intent..."
        python -m cli.main execute "${2:-examples/user-api.intent.yaml}"
        ;;
    ollama-start)
        echo "Starting Ollama server..."
        ollama serve &
        sleep 2
        echo "Pulling default model (${DEFAULT_MODEL})..."
        ollama pull ${DEFAULT_MODEL}
        ;;
    ollama-status)
        echo "Checking Ollama status..."
        curl -s http://localhost:11434/api/tags > /dev/null 2>&1 && \
            echo "✓ Ollama is running" || \
            echo "✗ Ollama is not running"
        ;;
    ollama-models)
        echo ""
        echo "Recommended Ollama models (≤12B):"
        echo "  llama3.2      - 3B  - Default, fast"
        echo "  llama3.2:1b   - 1B  - Ultra lightweight"
        echo "  llama3.1:8b   - 8B  - Balanced"
        echo "  mistral       - 7B  - Fast inference"
        echo "  mistral-nemo  - 12B - Best quality"
        echo "  gemma2        - 9B  - Google Gemma 2"
        echo "  phi3          - 3.8B - Microsoft Phi-3"
        echo "  qwen2.5       - 7B  - Alibaba Qwen"
        echo "  codellama     - 7B  - Code generation"
        echo ""
        echo "Install: ollama pull <model>"
        ;;
    clean)
        echo "Cleaning..."
        rm -rf __pycache__ */__pycache__ */*/__pycache__
        rm -rf .pytest_cache */.pytest_cache
        rm -rf *.egg-info .eggs
        rm -rf /tmp/intent-*
        echo "Done"
        ;;
    docker-clean)
        echo "Cleaning Docker resources..."
        docker ps -a --filter "name=intent-" -q | xargs -r docker rm -f
        docker images --filter "reference=intent-*" -q | xargs -r docker rmi -f
        echo "Done"
        ;;
    config)
        echo ""
        echo "Current Configuration:"
        echo "  HOST=${HOST}"
        echo "  PORT=${PORT}"
        echo "  DEFAULT_MODEL=${DEFAULT_MODEL}"
        echo "  CONTAINER_PORT=${CONTAINER_PORT:-8000}"
        echo "  OLLAMA_BASE_URL=${OLLAMA_BASE_URL:-http://localhost:11434}"
        echo "  SKIP_AMEN_CONFIRMATION=${SKIP_AMEN_CONFIRMATION:-true}"
        echo ""
        ;;
    help|*)
        echo "INTENT-ITERATIVE v0.1.0"
        echo ""
        echo "Usage: ./run.sh <command> [options]"
        echo ""
        echo "Setup:"
        echo "  install         Install dependencies"
        echo "  install-ai      Install LiteLLM for AI features"
        echo "  setup           Full setup (install + AI + .env)"
        echo ""
        echo "Run:"
        echo "  shell, cli      Start interactive shell"
        echo "  web, server     Start web server (http://localhost:${PORT})"
        echo "  plan [file]     Run dry-run on intent file"
        echo "  execute [file]  Execute intent file (no AMEN prompt)"
        echo ""
        echo "Test:"
        echo "  test            Run all tests"
        echo "  test-shell      Run shell tests only"
        echo "  test-web        Run web tests only"
        echo "  test-ai         Run AI Gateway tests"
        echo ""
        echo "AI/Ollama:"
        echo "  ollama-start    Start Ollama and pull default model"
        echo "  ollama-status   Check Ollama status"
        echo "  ollama-models   List recommended models"
        echo ""
        echo "Maintenance:"
        echo "  clean           Clean cache files"
        echo "  docker-clean    Remove intent-* containers/images"
        echo "  config          Show current configuration"
        echo "  help            Show this help"
        echo ""
        echo "Environment variables (or .env file):"
        echo "  HOST, PORT, DEFAULT_MODEL, OLLAMA_BASE_URL,"
        echo "  SKIP_AMEN_CONFIRMATION, CONTAINER_PORT"
        ;;
esac

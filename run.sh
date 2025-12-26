#!/bin/bash
# amen startup script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

case "${1:-help}" in
    shell|cli)
        echo "Starting amen Shell..."
        python -m cli.main "${@:2}"
        ;;
    web|server)
        echo "Starting amen Web Server..."
        echo "→ http://localhost:8080"
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
        pip install -r requirements.txt --break-system-packages
        ;;
    install-ai)
        echo "Installing AI Gateway dependencies (LiteLLM)..."
        pip install litellm --break-system-packages
        ;;
    ollama-start)
        echo "Starting Ollama server..."
        ollama serve &
        sleep 2
        echo "Pulling default model (llama3.2)..."
        ollama pull llama3.2
        ;;
    ollama-models)
        echo "Available Ollama models for amen (≤12B):"
        echo "  llama3.2      - Llama 3.2 3B (default)"
        echo "  llama3.2:1b   - Llama 3.2 1B"
        echo "  llama3.1:8b   - Llama 3.1 8B"
        echo "  mistral       - Mistral 7B"
        echo "  mistral-nemo  - Mistral Nemo 12B"
        echo "  gemma2        - Gemma 2 9B"
        echo "  gemma2:2b     - Gemma 2 2B"
        echo "  phi3          - Phi-3 Mini 3.8B"
        echo "  qwen2.5       - Qwen 2.5 7B"
        echo "  codellama     - Code Llama 7B"
        echo ""
        echo "To install: ollama pull <model>"
        ;;
    help|*)
        echo "amen v0.1.0"
        echo ""
        echo "Usage: ./run.sh <command> [options]"
        echo ""
        echo "Commands:"
        echo "  shell, cli      Start interactive shell"
        echo "  web, server     Start web server (http://localhost:8080)"
        echo "  test            Run all tests"
        echo "  test-shell      Run shell tests only"
        echo "  test-web        Run web tests only"
        echo "  test-ai         Run AI Gateway tests"
        echo "  install         Install dependencies"
        echo "  install-ai      Install LiteLLM for AI features"
        echo "  ollama-start    Start Ollama and pull default model"
        echo "  ollama-models   List recommended Ollama models"
        echo "  help            Show this help"
        echo ""
        echo "AI Gateway (Ollama) Setup:"
        echo "  1. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh"
        echo "  2. Start Ollama:   ollama serve"
        echo "  3. Pull model:     ollama pull llama3.2"
        echo ""
        echo "Examples:"
        echo "  ./run.sh shell"
        echo "  ./run.sh web"
        echo "  ./run.sh cli new my-api"
        echo "  ./run.sh cli plan examples/user-api.intent.yaml"
        ;;
esac

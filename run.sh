#!/bin/bash
# INTENT-ITERATIVE startup script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

case "${1:-help}" in
    shell|cli)
        echo "Starting INTENT-ITERATIVE Shell..."
        python -m cli.main "${@:2}"
        ;;
    web|server)
        echo "Starting INTENT-ITERATIVE Web Server..."
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
    install)
        echo "Installing dependencies..."
        pip install -r requirements.txt --break-system-packages
        ;;
    help|*)
        echo "INTENT-ITERATIVE v0.1.0"
        echo ""
        echo "Usage: ./run.sh <command> [options]"
        echo ""
        echo "Commands:"
        echo "  shell, cli      Start interactive shell"
        echo "  web, server     Start web server (http://localhost:8080)"
        echo "  test            Run all tests"
        echo "  test-shell      Run shell tests only"
        echo "  test-web        Run web tests only"
        echo "  install         Install dependencies"
        echo "  help            Show this help"
        echo ""
        echo "Examples:"
        echo "  ./run.sh shell"
        echo "  ./run.sh web"
        echo "  ./run.sh cli new my-api"
        echo "  ./run.sh cli plan examples/user-api.intent.yaml"
        ;;
esac

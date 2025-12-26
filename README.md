# INTENT-ITERATIVE

> DSL-based intent execution system with iterative refinement, AMEN boundary, and AI-powered assistance

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

amen is a system that allows you to:

1. **Define intents** using a simple YAML-based DSL
2. **Simulate execution** with dry-run planning
3. **Get AI suggestions** using local LLMs via Ollama
4. **Iteratively refine** your intent through feedback loops
5. **Execute safely** with the AMEN boundary (explicit approval required)

## Architecture

```
┌─────────────────────┐
│  CLI / Web UI       │  ← User interface
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Parser / Validator  │  ← DSL → IR
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Intermediate Rep.   │  ← Canonical state
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Planner / Simulator │  ← Dry-run
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ AI Gateway (Ollama) │  ← LLM suggestions
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Feedback Loop       │  ← Iterate
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ AMEN Boundary       │  ← Explicit approval
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Executor            │  ← Real execution
└─────────────────────┘
```

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/softreck/amen.git
cd amen

# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

### AI Gateway Setup (Ollama)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama server
ollama serve

# Pull default model (Llama 3.2 3B)
ollama pull llama3.2

# Or use other models (≤12B)
ollama pull mistral
ollama pull mistral-nemo
ollama pull gemma2
ollama pull codellama
```

### Shell Interface

```bash
# Start interactive shell
python -m cli.main

# Or use commands directly
python -m cli.main new my-api --goal "Create REST API"
python -m cli.main plan examples/user-api.intent.yaml
```

**Interactive Shell Commands:**

```
intent> new my-api          # Create new intent
intent> load file.yaml      # Load from file
intent> plan                # Run dry-run
intent> suggest             # Get AI suggestions
intent> apply               # Auto-apply AI suggestions
intent> chat                # Chat with AI
intent> iterate             # Apply manual changes
intent> amen                # Approve execution
intent> execute             # Execute approved intent
intent> show [json]         # Show current state
intent> models              # List AI models
intent> ai-health           # Check AI Gateway status
intent> help                # Show help
intent> exit                # Exit shell
```

### Web Interface

```bash
# Start web server
python -m web.app

# Open browser at http://localhost:8080
```

## AI Gateway

The AI Gateway uses **LiteLLM** to provide unified access to local LLMs via Ollama.

### Supported Models (≤12B parameters)

| Model | Size | Description |
|-------|------|-------------|
| `llama3.2` | 3B | Default - Fast and efficient |
| `llama3.2:1b` | 1B | Ultra lightweight |
| `llama3.1:8b` | 8B | Balanced performance |
| `mistral` | 7B | Fast inference |
| `mistral-nemo` | 12B | Best quality under 12B |
| `gemma2` | 9B | Google Gemma 2 |
| `gemma2:2b` | 2B | Lightweight |
| `phi3` | 3.8B | Microsoft Phi-3 |
| `qwen2.5` | 7B | Alibaba Qwen 2.5 |
| `codellama` | 7B | Code generation |
| `codegemma` | 7B | Google CodeGemma |
| `deepseek-coder` | 6.7B | DeepSeek Coder |

### Configuration

Environment variables:

```bash
export OLLAMA_BASE_URL="http://localhost:11434"
export DEFAULT_MODEL="llama3.2"
export MAX_MODEL_PARAMS="12.0"
```

### DSL Format

```yaml
INTENT:
  name: user-api
  goal: Create a REST API for user management

ENVIRONMENT:
  runtime: docker
  base_image: python:3.12-slim
  ports:
    - 8000

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /ping
    - api.expose GET /users
    - api.expose POST /users
    - api.expose DELETE /users/{id}

EXECUTION:
  mode: dry-run
```

### Supported Actions

| Action | Format | Description |
|--------|--------|-------------|
| `api.expose` | `api.expose METHOD /path` | Expose HTTP endpoint |
| `db.create` | `db.create table_name` | Create database table |
| `db.add_column` | `db.add_column table column type` | Add column to table |
| `shell.exec` | `shell.exec command` | Execute shell command |
| `rest.call` | `rest.call METHOD url` | Call external REST API |
| `file.create` | `file.create path` | Create file |

## API Reference

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/intents` | List all intents |
| `POST` | `/api/intents/parse` | Parse DSL and create intent |
| `GET` | `/api/intents/{id}` | Get intent by ID |
| `DELETE` | `/api/intents/{id}` | Delete intent |
| `POST` | `/api/intents/{id}/plan` | Run dry-run |
| `POST` | `/api/intents/{id}/iterate` | Apply changes |
| `POST` | `/api/intents/{id}/amen` | Approve for execution |
| `POST` | `/api/intents/{id}/execute` | Execute approved intent |
| `GET` | `/api/intents/{id}/code` | Get generated code |

### AI Gateway Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/ai/status` | Check AI Gateway status |
| `GET` | `/api/ai/models` | List available models |
| `POST` | `/api/ai/complete` | Generate AI completion |
| `POST` | `/api/ai/chat` | Chat with AI |
| `POST` | `/api/intents/{id}/ai/suggest` | Get AI suggestions |
| `POST` | `/api/intents/{id}/ai/apply` | Auto-apply suggestions |

### Python API

```python
from ir.models import IntentIR
from parser import parse_dsl
from planner import plan_intent
from ai_gateway import get_gateway, create_feedback_loop

# Parse DSL
ir = parse_dsl(dsl_content)

# Run dry-run
result = plan_intent(ir)
print(result.generated_code)

# Get AI suggestions
loop = create_feedback_loop()
suggestions = loop.analyze(ir, focus="security")
print(suggestions.suggestions)

# Apply AI suggestions
loop.iterate(ir, auto_apply=True)

# Or chat directly
gateway = get_gateway()
response = gateway.complete("Explain FastAPI middleware")
print(response["content"])
```

## Testing

```bash
# Run all tests (58 tests)
pytest

# Run specific test suites
pytest tests/e2e/test_shell.py -v      # 17 tests
pytest tests/e2e/test_web.py -v        # 18 tests  
pytest tests/e2e/test_ai_gateway.py -v # 23 tests

# Run with coverage
pytest --cov=. --cov-report=html
```

## Project Structure

```
amen/
├── ir/                 # Intermediate Representation models
├── parser/             # DSL parser
├── planner/            # Dry-run simulator
├── executor/           # Execution engine
├── ai_gateway/         # LiteLLM AI Gateway
│   ├── gateway.py      # Main gateway with Ollama models
│   └── feedback_loop.py # LLM-powered feedback loop
├── cli/                # Shell interface
├── web/                # Web interface (FastAPI)
├── tests/e2e/          # E2E test suite
│   ├── test_shell.py
│   ├── test_web.py
│   └── test_ai_gateway.py
├── examples/           # Example DSL files
├── config.py           # Configuration
├── requirements.txt
└── README.md
```

## Workflow

1. **Define Intent** → Write DSL or use web editor
2. **Parse** → Convert DSL to IR (Intermediate Representation)
3. **Plan** → Run dry-run simulation, review generated code
4. **Get AI Suggestions** → Analyze with local LLM
5. **Iterate** → Make changes, re-plan until satisfied
6. **AMEN** → Explicitly approve for execution
7. **Execute** → Run with real side effects (Docker build, etc.)

## License

Apache 2 License - see [LICENSE](LICENSE) file.

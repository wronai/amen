# INTENT-ITERATIVE

> DSL-based intent execution system with iterative refinement and AMEN boundary

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

INTENT-ITERATIVE is a system that allows you to:

1. **Define intents** using a simple YAML-based DSL
2. **Simulate execution** with dry-run planning
3. **Iteratively refine** your intent through feedback loops
4. **Execute safely** with the AMEN boundary (explicit approval required)

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
git clone https://github.com/wronai/amen.git
cd amen

# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

### Shell Interface

```bash
# Start interactive shell
python -m cli.main

# Or use commands directly
python -m cli.main new my-api --goal "Create REST API"
python -m cli.main plan examples/user-api.intent.yaml
python -m cli.main execute examples/user-api.intent.yaml
```

**Interactive Shell Commands:**

```
intent> new my-api          # Create new intent
intent> load file.yaml      # Load from file
intent> plan                # Run dry-run
intent> iterate             # Apply changes
intent> amen                # Approve execution
intent> execute             # Execute approved intent
intent> show [json]         # Show current state
intent> save file.json      # Save to file
intent> help                # Show help
intent> exit                # Exit shell
```

### Web Interface

```bash
# Start web server
python -m web.app

# Open browser at http://localhost:8080
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

### Python API

```python
from ir.models import IntentIR
from parser import parse_dsl
from planner import plan_intent
from executor import execute_intent

# Parse DSL
ir = parse_dsl(dsl_content)

# Run dry-run
result = plan_intent(ir)
print(result.generated_code)
print(result.dockerfile)

# Iterate
ir.add_iteration({"action": "api.expose POST /data"})

# Approve and execute
ir.approve_amen()
exec_result = execute_intent(ir)
```

## Testing

```bash
# Run all tests
pytest

# Run shell tests only
pytest tests/e2e/test_shell.py -v

# Run web tests only
pytest tests/e2e/test_web.py -v

# Run with coverage
pytest --cov=. --cov-report=html
```

## Project Structure

```
intent-iterative/
├── ir/                 # Intermediate Representation models
│   ├── __init__.py
│   └── models.py
├── parser/             # DSL parser
│   ├── __init__.py
│   └── dsl_parser.py
├── planner/            # Dry-run simulator
│   ├── __init__.py
│   └── simulator.py
├── executor/           # Execution engine
│   ├── __init__.py
│   └── runner.py
├── cli/                # Shell interface
│   ├── __init__.py
│   └── main.py
├── web/                # Web interface
│   ├── __init__.py
│   ├── app.py
│   └── templates/
│       └── index.html
├── tests/              # Test suite
│   ├── conftest.py
│   └── e2e/
│       ├── test_shell.py
│       └── test_web.py
├── examples/           # Example DSL files
│   └── user-api.intent.yaml
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Workflow

1. **Define Intent** → Write DSL or use web editor
2. **Parse** → Convert DSL to IR (Intermediate Representation)
3. **Plan** → Run dry-run simulation, review generated code
4. **Iterate** → Make changes, re-plan until satisfied
5. **AMEN** → Explicitly approve for execution
6. **Execute** → Run with real side effects (Docker build, etc.)

## License

MIT License - see [LICENSE](LICENSE) file.

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -am 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

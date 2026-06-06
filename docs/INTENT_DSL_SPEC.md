# ITERUN Intent DSL — Specification

## Overview

ITERUN opisuje **co** wdrożyć (API, akcje, runtime) w pliku paczki DSL. Domyślna nazwa pliku: **`iterun.yaml`** (`config.PACKAGE_FILENAME`). Wewnętrzna sekcja root nadal to `INTENT:`.

Dwa tryby wejścia:

| Tryb | Wejście | Wyjście |
|------|---------|---------|
| **Prompt-first** (zalecany) | NL prompt | `generated/iterun.yaml` + artefakty |
| **Ręczny DSL** | `iterun.yaml` | `plan` / `execute` |

## Interfejsy generowania

| Interface | Entry |
|-----------|-------|
| CLI | `iterun generate "prompt" -o generated/ [--run] [--execute] [--verify]` |
| REST | `POST /api/intents/generate`, `POST /api/intents/generate-and-run` |
| SDK | `IterunClient().generate_and_run(prompt, output_dir=...)` |
| MCP | `iterun_generate_intent` tool |

## Document structure (`iterun.yaml`)

```yaml
INTENT:          # required
  name: kebab-case-id
  goal: string
  description: optional

ENVIRONMENT:     # optional (defaults shown)
  runtime: docker | kubernetes | local
  base_image: python:3.12-slim
  ports: [8000]
  env_vars: {}

IMPLEMENTATION:  # required
  language: python | node
  framework: fastapi | flask | express
  actions:         # list of DSL strings
    - api.expose GET /ping

EXECUTION:       # optional
  mode: dry-run | transactional
```

## Action grammar

```
api.expose METHOD /path
db.create table
db.add_column table column type
shell.exec command
rest.call METHOD url
file.create path
```

## JSON Schema

```bash
iterun schema
# GET /api/schema
iterun validate generated/iterun.yaml
# POST /api/intents/validate-yaml
```

## Pipeline: prompt → usługa

```text
prompt (NL)
  → LLM + validate-retry (max 5)     → iterun.yaml
  → intract.yaml                     (kontrakt Intract)
  → service.testql.toon.yaml         (kontrakt TestQL)
  → plan                             → app.py, Dockerfile, plan.result.json
  → execute (Docker)
  → verify (--verify)                → testql + HTTP + expectations.yaml
  → przy FAIL: ponowne generate z kontekstem błędów (max 3–5 rund)
  → session.json, execution.json, container.log, verify.rounds.json
```

### CLI

```bash
# tylko YAML + kontrakty
iterun generate "Create a REST API for user management" -o generated/ --quiet

# YAML + plan
iterun generate "..." -o generated/ --run

# YAML + plan + Docker
iterun generate "..." -o generated/ --execute

# pełny gate: deploy + testql + retry naprawczy
iterun generate "..." -o generated/ --execute --verify
iterun generate "..." -o generated/ --execute --verify --max-verify-iterations 5
```

### Artefakty w `--output-dir`

| Plik | Źródło |
|------|--------|
| `iterun.yaml` | LLM (`generator/intent_generator.py`) |
| `prompt.txt` | kopia promptu sesji |
| `intract.yaml` | `generator/intract_manifest.py` |
| `service.testql.toon.yaml` | `generator/testql_scenario.py` |
| `plan.result.json` | plan + logi dry-run |
| `execution.json` | execute + logi |
| `container.log` | `docker logs` (tail 200) |
| `verify.result.json` | TestQL + sondy HTTP |
| `verify.rounds.json` | historia rund `--verify` |
| `session.json` | **zbiorczy log całej sesji** |
| `expectations.yaml` | opcjonalny kontrakt (np. examples resilience) |
| `openapi.yaml` | OpenAPI + `x-intract` (E2E) |

## LLM generation loop (YAML)

1. System prompt: JSON Schema + example + action rules
2. User prompt: natural language goal
3. LiteLLM completion → extract YAML
4. Validate: Pydantic + `parse_dsl()`
5. On failure: re-prompt with errors (max `--max-iterations`, default 5)

## Contract verify loop (`--verify`)

Po `execute`:

1. Czekaj na gotowość kontenera
2. `testql run generated/service.testql.toon.yaml --url <base>`
3. HTTP probe każdego `api.expose` z `iterun.yaml`
4. Jeśli `generated/expectations.yaml` — sprawdź brakujące endpointy / framework
5. Zapis `verify.result.json`; przy błędzie — nowa runda `generate` z listą failures w prompcie
6. Historia: `verify.rounds.json`

Integracje zewnętrzne (opcjonalnie w examples E2E):

- **[Intract](https://github.com/semcod/intract)** — `intract validate generated/ --manifest generated/intract.yaml`
- **[TestQL](https://github.com/oqlos/testql)** — scenariusz w `service.testql.toon.yaml`

## Environment (.env)

Priorytet modelu: `--model` CLI > `LLM_MODEL` > `DEFAULT_MODEL`

| Variable | Przykład | Opis |
|----------|----------|------|
| `OPENROUTER_API_KEY` | `sk-or-...` | OpenRouter (LiteLLM) |
| `LLM_MODEL` | `openrouter/deepseek/deepseek-v4-pro` | Model dla `generate` |
| `DEFAULT_MODEL` | `llama3.2` | Fallback Ollama (`suggest`, `chat`) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Lokalny Ollama |
| `SKIP_ITERUN_CONFIRMATION` | `true` | Bez interaktywnego `iterun` w CLI |
| `CONTAINER_PORT` | `8000` | Port w kontenerze |

```bash
pip install -e ".[ai]"
cp .env.example .env
iterun generate "Create a REST API for user management" -o generated/ --execute --verify
```

## Przykłady

| Zakres | Skrypt |
|--------|--------|
| Podstawowe (01–08) | `./examples/run-all.sh` |
| E2E testql + intract (09–12) | `./examples/run-e2e.sh` |
| Resilience / repair loop (13–16) | `./examples/run-resilience.sh` |

Szczegóły: [examples/README.md](../examples/README.md).

## SDK

```python
from sdk import IterunClient

client = IterunClient()
result = client.generate_and_run(
    "Create a REST API for user management",
    output_dir="generated",
    execute=True,
)
print(result.yaml_path)  # generated/iterun.yaml
```

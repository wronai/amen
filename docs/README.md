# Dokumentacja ITERUN

## Indeks

| Dokument | Opis |
|----------|------|
| [INTENT_DSL_SPEC.md](INTENT_DSL_SPEC.md) | Składnia DSL, `iterun.yaml`, pipeline LLM, kontrakty, verify loop |
| [../README.md](../README.md) | Instalacja, architektura, REST API, workflow |
| [../examples/README.md](../examples/README.md) | Przykłady 01–16, artefakty `generated/`, E2E, resilience |

## Architektura (skrót)

```text
prompt (NL)
  → Generator (LiteLLM)     → iterun.yaml
  → intract + testql        → kontrakty w generated/
  → Planner                 → app.py, Dockerfile
  → Executor (Docker)
  → Contract verify         → TestQL + HTTP (+ expectations.yaml)
  → session.json            → pełny log sesji
```

Szczegóły pipeline: [INTENT_DSL_SPEC.md § Pipeline](INTENT_DSL_SPEC.md#pipeline-prompt--usługa).

## CLI — najczęstsze komendy

```bash
# Prompt → paczka → usługa → weryfikacja
iterun generate "Create a REST API for users" -o generated/ --execute --verify

# Tylko YAML (+ auto intract + testql)
iterun generate "Create a ping API" -o generated/ --quiet

# YAML + plan (bez Docker)
iterun generate "..." -o generated/ --run

# Schema / walidacja ręcznego DSL
iterun schema
iterun validate generated/iterun.yaml

# Plan / execute istniejącej paczki
iterun plan generated/iterun.yaml -o generated/
iterun execute generated/iterun.yaml --workspace generated/

# Shell interaktywny
iterun
```

### Flagi `iterun generate`

| Flaga | Domyślnie | Opis |
|-------|-----------|------|
| `-o`, `--output-dir` | `generated` | Katalog artefaktów sesji |
| `--run` | off | Plan po wygenerowaniu YAML |
| `--execute` | off | Deploy w Docker po planie |
| `--verify` | off | TestQL + HTTP po execute; retry przy fail |
| `--max-iterations` | 5 | Limit walidacji YAML przez LLM |
| `--max-verify-iterations` | 3 | Limit rund naprawczych przy `--verify` |
| `-m`, `--model` | z `.env` | Model LiteLLM (np. OpenRouter) |
| `--json` | off | Wynik sesji na stdout (JSON) |
| `--quiet` | off | Minimalny output (skrypty) |

## Pliki w `generated/`

| Plik | Zawartość |
|------|-----------|
| `iterun.yaml` | Paczka DSL (główny artefakt) |
| `session.json` | **Pełny log** — prompt, generate, plan, execute, verify |
| `intract.yaml` | Kontrakt Intract (`require: implement.*`) |
| `service.testql.toon.yaml` | Scenariusz TestQL |
| `plan.result.json` | IR + logi planera |
| `execution.json` | Execute, endpointy, `container_id` |
| `container.log` | Tail `docker logs` |
| `verify.result.json` | Wynik ostatniego verify |
| `verify.rounds.json` | Historia rund naprawczych |
| `app.py` / `Dockerfile` | Wygenerowana usługa |

Pełna tabela: [examples/README.md § Gdzie są dane i logi](../examples/README.md#gdzie-są-dane-i-logi-generated).

## Przykłady

| Skrypt | Zakres |
|--------|--------|
| `./examples/run-all.sh` | 01–08: prompt → `iterun.yaml` → plan |
| `./examples/run-e2e.sh` | 09–12: execute + TestQL + Intract |
| `./examples/run-resilience.sh` | 13–16: skrajne prompty, pętla naprawcza |

| Katalog | Temat |
|---------|-------|
| `01-user-api` | FastAPI CRUD |
| `02-ping-smoke` | Minimalny `/ping` |
| `08-llm-generate` | SDK + MCP |
| `09-e2e-ping-verify` | TestQL + Intract |
| `12-e2e-full-gate` | Pełny gate (intract graph/scan) |
| `13-resilience-vague` | Mglisty prompt vs expectations |

## Integracje zewnętrzne

| Narzędzie | Rola w ITERUN |
|-----------|----------------|
| [LiteLLM](https://github.com/BerriAI/litellm) | OpenRouter / Ollama w `iterun generate` |
| [TestQL](https://github.com/oqlos/testql) | `--verify`, `service.testql.toon.yaml` |
| [Intract](https://github.com/semcod/intract) | `intract.yaml`, walidacja kontraktu kodu |

## Konfiguracja LLM (`.env`)

```bash
OPENROUTER_API_KEY=sk-or-...
LLM_MODEL=openrouter/deepseek/deepseek-v4-pro   # generate
DEFAULT_MODEL=llama3.2                          # shell suggest/chat (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
```

Priorytet modelu: `--model` CLI > `LLM_MODEL` > `DEFAULT_MODEL`.

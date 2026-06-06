# ITERUN

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Workflows](#workflows)
- [Quality Pipeline (`pyqual.yaml`)](#quality-pipeline-pyqualyaml)
- [Dependencies](#dependencies)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `iterun`
- **version**: `0.1.6`
- **python_requires**: `>=3.11`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, requirements.txt, Makefile, testql(3), app.doql.less, pyqual.yaml, goal.yaml, .env.example, project/(6 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: iterun;
  version: 0.1.6;
}

dependencies {
  runtime: "pyyaml>=6.0, pydantic>=2.0, fastapi>=0.109.0, uvicorn>=0.27.0, jinja2>=3.1.0";
  dev: "pytest>=8.0.0, pytest-asyncio>=0.23.0, httpx>=0.26.0, anyio>=4.0.0, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60";
}

interface[type="api"] {
  type: rest;
  framework: fastapi;
}

interface[type="cli"] {
  framework: argparse;
}
interface[type="cli"] page[name="iterun"] {

}

workflow[name="install"] {
  trigger: manual;
  step-1: run cmd=$(PIP) install -r requirements.txt;
}

workflow[name="install-dev"] {
  trigger: manual;
  step-1: run cmd=$(PIP) install pytest pytest-asyncio httpx anyio;
}

workflow[name="install-ai"] {
  trigger: manual;
  step-1: run cmd=$(PIP) install litellm;
}

workflow[name="setup"] {
  trigger: manual;
  step-1: run cmd=echo "$(GREEN)✓ Setup complete$(RESET)";
}

workflow[name="env"] {
  trigger: manual;
  step-1: run cmd=if [ ! -f .env ]; then \;
  step-2: run cmd=cp .env.example .env; \;
  step-3: run cmd=echo "$(GREEN)✓ Created .env from .env.example$(RESET)"; \;
  step-4: run cmd=else \;
  step-5: run cmd=echo "$(YELLOW)⚠ .env already exists$(RESET)"; \;
  step-6: run cmd=fi;
}

workflow[name="run"] {
  trigger: manual;
  step-1: depend target=web;
}

workflow[name="web"] {
  trigger: manual;
  step-1: run cmd=echo "$(CYAN)Starting web server on http://$(HOST):$(PORT)$(RESET)";
  step-2: run cmd=$(PYTHON) -m web.app;
}

workflow[name="shell"] {
  trigger: manual;
  step-1: run cmd=echo "$(CYAN)Starting interactive shell$(RESET)";
  step-2: run cmd=$(PYTHON) -m cli.main;
}

workflow[name="plan"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m cli.main plan examples/01-user-api/intent.yaml;
}

workflow[name="execute"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m cli.main execute examples/01-user-api/intent.yaml;
}

workflow[name="examples"] {
  trigger: manual;
  step-1: run cmd=./examples/run-all.sh;
}

workflow[name="run-intent"] {
  trigger: manual;
  step-1: run cmd=if [ -z "$(FILE)" ]; then \;
  step-2: run cmd=echo "$(RED)ERROR: FILE not specified$(RESET)"; \;
  step-3: run cmd=echo "Usage: make run-intent FILE=path/to/intent.yaml"; \;
  step-4: run cmd=exit 1; \;
  step-5: run cmd=fi;
  step-6: run cmd=$(PYTHON) -m cli.main execute $(FILE);
}

workflow[name="test"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m pytest tests/ -v;
}

workflow[name="test-shell"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m pytest tests/e2e/test_shell.py -v;
}

workflow[name="test-web"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m pytest tests/e2e/test_web.py -v;
}

workflow[name="test-ai"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m pytest tests/e2e/test_ai_gateway.py -v;
}

workflow[name="test-cov"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term;
}

workflow[name="ollama-start"] {
  trigger: manual;
  step-1: run cmd=echo "$(CYAN)Starting Ollama server...$(RESET)";
  step-2: run cmd=ollama serve &;
  step-3: run cmd=sleep 2;
  step-4: run cmd=echo "$(GREEN)✓ Ollama server started$(RESET)";
}

workflow[name="ollama-pull"] {
  trigger: manual;
  step-1: run cmd=echo "$(CYAN)Pulling model: $(DEFAULT_MODEL)$(RESET)";
  step-2: run cmd=ollama pull $(DEFAULT_MODEL);
  step-3: run cmd=echo "$(GREEN)✓ Model $(DEFAULT_MODEL) ready$(RESET)";
}

workflow[name="ollama-models"] {
  trigger: manual;
  step-1: run cmd=echo "";
  step-2: run cmd=echo "$(CYAN)Recommended Ollama models (≤12B):$(RESET)";
  step-3: run cmd=echo "  $(GREEN)llama3.2$(RESET)       - 3B  - Default, fast";
  step-4: run cmd=echo "  llama3.2:1b    - 1B  - Ultra lightweight";
  step-5: run cmd=echo "  llama3.1:8b    - 8B  - Balanced";
  step-6: run cmd=echo "  mistral        - 7B  - Fast inference";
  step-7: run cmd=echo "  mistral-nemo   - 12B - Best quality";
  step-8: run cmd=echo "  gemma2         - 9B  - Google Gemma 2";
  step-9: run cmd=echo "  phi3           - 3.8B - Microsoft Phi-3";
  step-10: run cmd=echo "  qwen2.5        - 7B  - Alibaba Qwen";
  step-11: run cmd=echo "  codellama      - 7B  - Code generation";
  step-12: run cmd=echo "";
  step-13: run cmd=echo "$(YELLOW)Install:$(RESET) ollama pull <model>";
  step-14: run cmd=echo "";
}

workflow[name="ollama-status"] {
  trigger: manual;
  step-1: run cmd=echo "$(CYAN)Checking Ollama status...$(RESET)";
  step-2: run cmd=curl -s http://localhost:11434/api/tags > /dev/null 2>&1 && \;
  step-3: run cmd=echo "$(GREEN)✓ Ollama is running$(RESET)" || \;
  step-4: run cmd=echo "$(RED)✗ Ollama is not running$(RESET)";
}

workflow[name="lint"] {
  trigger: manual;
  step-1: run cmd=which ruff > /dev/null 2>&1 && ruff check . || echo "$(YELLOW)ruff not installed$(RESET)";
}

workflow[name="format"] {
  trigger: manual;
  step-1: run cmd=which ruff > /dev/null 2>&1 && ruff format . || echo "$(YELLOW)ruff not installed$(RESET)";
}

workflow[name="clean"] {
  trigger: manual;
  step-1: run cmd=echo "$(CYAN)Cleaning...$(RESET)";
  step-2: run cmd=rm -rf __pycache__ */__pycache__ */*/__pycache__;
  step-3: run cmd=rm -rf .pytest_cache */.pytest_cache;
  step-4: run cmd=rm -rf *.egg-info .eggs;
  step-5: run cmd=rm -rf htmlcov .coverage;
  step-6: run cmd=rm -rf /tmp/intent-*;
  step-7: run cmd=echo "$(GREEN)✓ Cleaned$(RESET)";
}

workflow[name="docker-clean"] {
  trigger: manual;
  step-1: run cmd=echo "$(CYAN)Cleaning Docker resources...$(RESET)";
  step-2: run cmd=-docker ps -a --filter "name=$(CONTAINER_PREFIX)-" -q | xargs -r docker rm -f;
  step-3: run cmd=-docker images --filter "reference=$(CONTAINER_PREFIX)-*" -q | xargs -r docker rmi -f;
  step-4: run cmd=echo "$(GREEN)✓ Docker cleaned$(RESET)";
}

workflow[name="docker-ps"] {
  trigger: manual;
  step-1: run cmd=docker ps --filter "name=$(CONTAINER_PREFIX)-";
}

workflow[name="docker-stop"] {
  trigger: manual;
  step-1: run cmd=docker ps --filter "name=$(CONTAINER_PREFIX)-" -q | xargs -r docker stop;
  step-2: run cmd=echo "$(GREEN)✓ Containers stopped$(RESET)";
}

workflow[name="dev"] {
  trigger: manual;
  step-1: run cmd=uvicorn web.app:app --reload --host $(HOST) --port $(PORT);
}

workflow[name="new-intent"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m cli.main new;
}

workflow[name="show-config"] {
  trigger: manual;
  step-1: run cmd=echo "";
  step-2: run cmd=echo "$(CYAN)Current Configuration:$(RESET)";
  step-3: run cmd=echo "  HOST=$(HOST)";
  step-4: run cmd=echo "  PORT=$(PORT)";
  step-5: run cmd=echo "  DEFAULT_MODEL=$(DEFAULT_MODEL)";
  step-6: run cmd=echo "  CONTAINER_PORT=$(CONTAINER_PORT)";
  step-7: run cmd=echo "  CONTAINER_PREFIX=$(CONTAINER_PREFIX)";
  step-8: run cmd=echo "  OLLAMA_BASE_URL=$(OLLAMA_BASE_URL)";
  step-9: run cmd=echo "  SKIP_ITERUN_CONFIRMATION=$(SKIP_ITERUN_CONFIRMATION)";
  step-10: run cmd=echo "";
}

deploy {
  target: docker;
}

environment[name="local"] {
  runtime: docker-compose;
  env_file: .env;
  python_version: >=3.11;
}
```

## Workflows

## Quality Pipeline (`pyqual.yaml`)

```yaml markpact:pyqual path=pyqual.yaml
pipeline:
  name: iterun-quality

  metrics:
    cc_max: 15
    critical_max: 0

  custom_tools:
    - name: code2llm_iterun
      binary: code2llm
      command: >-
        code2llm {workdir} -f toon -o ./project --no-chunk
        --exclude .git .venv .venv_test build dist __pycache__ .pytest_cache .code2llm_cache .benchmarks .mypy_cache .ruff_cache node_modules
      output: ""
      allow_failure: false

    - name: vallm_iterun
      binary: vallm
      command: >-
        vallm batch {workdir} --recursive --format toon --output ./project
        --exclude .git,.venv,.venv_test,build,dist,__pycache__,.pytest_cache,.code2llm_cache,.benchmarks,.mypy_cache,.ruff_cache,node_modules
      output: ""
      allow_failure: false

  stages:
    - name: analyze
      tool: code2llm_iterun
      optional: true
      timeout: 0

    - name: validate
      tool: vallm_iterun
      optional: true
      timeout: 0

    - name: lint
      tool: ruff
      optional: true

    - name: fix
      tool: prefact
      optional: true
      when: metrics_fail
      timeout: 900

    - name: test
      run: python3 -m pytest -q
      when: always

  loop:
    max_iterations: 3
    on_fail: report

  env:
    LLM_MODEL: openrouter/qwen/qwen3-coder-next
```

## Dependencies

### Runtime

```text markpact:deps python
pyyaml>=6.0
pydantic>=2.0
fastapi>=0.109.0
uvicorn>=0.27.0
jinja2>=3.1.0
```

### Development

```text markpact:deps python scope=dev
pytest>=8.0.0
pytest-asyncio>=0.23.0
httpx>=0.26.0
anyio>=4.0.0
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
```

## Call Graph

*85 nodes · 77 edges · 22 modules · CC̄=4.2*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `run_pipeline` *(in generator.pipeline)* | 30 ⚠ | 3 | 35 | **38** |
| `cmd_execute` *(in cli.main.CLI)* | 37 ⚠ | 0 | 37 | **37** |
| `verify_contract` *(in generator.contract_verify)* | 16 ⚠ | 1 | 32 | **33** |
| `verify` *(in examples._scripts.verify_expectations)* | 23 ⚠ | 1 | 27 | **28** |
| `check_expectations` *(in generator.expectations)* | 20 ⚠ | 1 | 23 | **24** |
| `cmd_plan` *(in cli.main.CLI)* | 11 ⚠ | 0 | 24 | **24** |
| `cmd_ai_suggest` *(in cli.main.CLI)* | 11 ⚠ | 0 | 21 | **21** |
| `generate` *(in generator.intent_generator.IntentGenerator)* | 11 ⚠ | 0 | 21 | **21** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/wronai/iterun
# generated in 0.04s
# nodes: 85 | edges: 77 | modules: 22
# CC̄=4.2

HUBS[20]:
  generator.pipeline.run_pipeline
    CC=30  in:3  out:35  total:38
  cli.main.CLI.cmd_execute
    CC=37  in:0  out:37  total:37
  generator.contract_verify.verify_contract
    CC=16  in:1  out:32  total:33
  examples._scripts.verify_expectations.verify
    CC=23  in:1  out:27  total:28
  generator.expectations.check_expectations
    CC=20  in:1  out:23  total:24
  cli.main.CLI.cmd_plan
    CC=11  in:0  out:24  total:24
  cli.main.CLI.cmd_ai_suggest
    CC=11  in:0  out:21  total:21
  generator.intent_generator.IntentGenerator.generate
    CC=11  in:0  out:21  total:21
  examples._scripts.intent_to_openapi.intent_to_openapi
    CC=8  in:1  out:17  total:18
  cli.main.CLI.cmd_ai_chat
    CC=12  in:0  out:18  total:18
  generator.session.write_session_artifacts
    CC=5  in:1  out:16  total:17
  config.load_dotenv
    CC=15  in:1  out:15  total:16
  examples._scripts.annotate_intract.annotate_express
    CC=6  in:1  out:13  total:14
  ai_gateway.gateway.get_gateway
    CC=3  in:13  out:1  total:14
  examples._scripts.annotate_intract._actions
    CC=7  in:2  out:11  total:13
  generator.intract_manifest.parse_api_actions
    CC=6  in:4  out:9  total:13
  examples._scripts.annotate_intract.annotate_python
    CC=5  in:1  out:11  total:12
  planner.simulator._endpoint_to_func_name
    CC=5  in:2  out:10  total:12
  generator.intent_generator.extract_yaml_from_llm
    CC=6  in:1  out:11  total:12
  cli.main.CLI.cmd_ai_health
    CC=4  in:0  out:12  total:12

MODULES:
  ai_gateway.feedback_loop  [2 funcs]
    __init__  CC=3  out:1
    create_feedback_loop  CC=1  out:1
  ai_gateway.gateway  [4 funcs]
    __post_init__  CC=15  out:8
    complete  CC=1  out:2
    get_gateway  CC=3  out:1
    suggest_improvements  CC=1  out:2
  cli.main  [10 funcs]
    cmd_ai_apply  CC=8  out:10
    cmd_ai_chat  CC=12  out:18
    cmd_ai_health  CC=4  out:12
    cmd_ai_suggest  CC=11  out:21
    cmd_execute  CC=37  out:37
    cmd_load  CC=3  out:8
    cmd_models  CC=3  out:9
    cmd_new  CC=4  out:7
    cmd_parse  CC=2  out:4
    cmd_plan  CC=11  out:24
  config  [3 funcs]
    get_config  CC=2  out:1
    load_dotenv  CC=15  out:15
    reload_config  CC=1  out:2
  dsl.schema  [3 funcs]
    get_json_schema  CC=1  out:1
    get_system_prompt  CC=1  out:2
    validate_yaml_document  CC=7  out:7
  examples._scripts.annotate_intract  [6 funcs]
    _actions  CC=7  out:11
    _comment  CC=1  out:1
    _slug  CC=2  out:4
    annotate_express  CC=6  out:13
    annotate_python  CC=5  out:11
    main  CC=3  out:8
  examples._scripts.intent_to_intract  [1 funcs]
    main  CC=3  out:9
  examples._scripts.intent_to_openapi  [3 funcs]
    _slug  CC=2  out:4
    intent_to_openapi  CC=8  out:17
    main  CC=1  out:9
  examples._scripts.intent_to_testql  [1 funcs]
    main  CC=1  out:6
  examples._scripts.verify_expectations  [4 funcs]
    _load_yaml  CC=2  out:2
    _parse_actions  CC=6  out:9
    main  CC=3  out:9
    verify  CC=23  out:27
  executor.runner  [2 funcs]
    __init__  CC=3  out:5
    execute_intent  CC=1  out:2
  generator.contract_verify  [2 funcs]
    verify_contract  CC=16  out:32
    write_contract_artifacts  CC=1  out:2
  generator.expectations  [2 funcs]
    check_expectations  CC=20  out:23
    load_and_check_expectations  CC=4  out:8
  generator.intent_generator  [4 funcs]
    __init__  CC=2  out:2
    generate  CC=11  out:21
    _build_user_prompt  CC=4  out:1
    extract_yaml_from_llm  CC=6  out:11
  generator.intract_manifest  [6 funcs]
    _safe_id  CC=1  out:3
    _slug  CC=2  out:4
    build_intract_manifest  CC=6  out:11
    intent_to_intract_dict  CC=2  out:4
    parse_api_actions  CC=6  out:9
    write_intract_manifest  CC=1  out:5
  generator.pipeline  [4 funcs]
    _container_logs  CC=4  out:3
    _finalize  CC=2  out:3
    _write_plan_artifacts  CC=4  out:8
    run_pipeline  CC=30  out:35
  generator.session  [1 funcs]
    write_session_artifacts  CC=5  out:16
  generator.testql_scenario  [3 funcs]
    _probe_path  CC=1  out:1
    build_testql_scenario  CC=7  out:9
    write_testql_scenario  CC=2  out:7
  parser.dsl_parser  [2 funcs]
    parse_dsl  CC=1  out:2
    parse_dsl_file  CC=1  out:2
  planner.simulator  [4 funcs]
    _generate_fastapi_code  CC=5  out:7
    _generate_flask_code  CC=5  out:5
    _endpoint_to_func_name  CC=5  out:10
    plan_intent  CC=1  out:2
  sdk.client  [4 funcs]
    generate_and_run  CC=3  out:2
    parse  CC=1  out:1
    schema  CC=1  out:1
    validate  CC=2  out:2
  web.app  [14 funcs]
    ai_apply_suggestions  CC=4  out:7
    ai_chat  CC=4  out:7
    ai_complete  CC=3  out:6
    ai_status  CC=2  out:5
    ai_suggest  CC=6  out:8
    execute  CC=5  out:5
    generate_and_run_api  CC=3  out:3
    generate_code  CC=3  out:6
    get_schema  CC=1  out:2
    list_models  CC=2  out:4

EDGES:
  examples._scripts.verify_expectations.verify → examples._scripts.verify_expectations._load_yaml
  examples._scripts.verify_expectations.verify → examples._scripts.verify_expectations._parse_actions
  examples._scripts.verify_expectations.main → examples._scripts.verify_expectations.verify
  generator.intract_manifest.build_intract_manifest → generator.intract_manifest._safe_id
  generator.intract_manifest.build_intract_manifest → generator.intract_manifest.parse_api_actions
  generator.intract_manifest.build_intract_manifest → generator.intract_manifest._slug
  generator.intract_manifest.intent_to_intract_dict → generator.intract_manifest.build_intract_manifest
  generator.intract_manifest.write_intract_manifest → generator.intract_manifest.intent_to_intract_dict
  examples._scripts.intent_to_openapi.intent_to_openapi → examples._scripts.intent_to_openapi._slug
  examples._scripts.intent_to_openapi.main → examples._scripts.intent_to_openapi.intent_to_openapi
  generator.testql_scenario.build_testql_scenario → generator.intract_manifest.parse_api_actions
  generator.testql_scenario.build_testql_scenario → generator.testql_scenario._probe_path
  generator.testql_scenario.write_testql_scenario → generator.testql_scenario.build_testql_scenario
  examples._scripts.intent_to_testql.main → generator.testql_scenario.write_testql_scenario
  generator.contract_verify.write_contract_artifacts → generator.intract_manifest.write_intract_manifest
  generator.contract_verify.write_contract_artifacts → generator.testql_scenario.write_testql_scenario
  generator.contract_verify.verify_contract → generator.contract_verify.write_contract_artifacts
  generator.contract_verify.verify_contract → generator.intract_manifest.parse_api_actions
  generator.contract_verify.verify_contract → generator.expectations.load_and_check_expectations
  generator.expectations.check_expectations → generator.intract_manifest.parse_api_actions
  generator.expectations.load_and_check_expectations → generator.expectations.check_expectations
  executor.runner.Executor.__init__ → config.get_config
  sdk.client.IterunClient.schema → dsl.schema.get_json_schema
  sdk.client.IterunClient.validate → dsl.schema.validate_yaml_document
  sdk.client.IterunClient.generate_and_run → generator.pipeline.run_pipeline
  sdk.client.IterunClient.parse → parser.dsl_parser.parse_dsl
  examples._scripts.annotate_intract._comment → examples._scripts.annotate_intract._slug
  examples._scripts.annotate_intract.annotate_python → examples._scripts.annotate_intract._actions
  examples._scripts.annotate_intract.annotate_express → examples._scripts.annotate_intract._actions
  examples._scripts.annotate_intract.main → examples._scripts.annotate_intract.annotate_python
  examples._scripts.annotate_intract.main → examples._scripts.annotate_intract.annotate_express
  planner.simulator.Planner._generate_fastapi_code → planner.simulator._endpoint_to_func_name
  planner.simulator.Planner._generate_flask_code → planner.simulator._endpoint_to_func_name
  examples._scripts.intent_to_intract.main → generator.intract_manifest.write_intract_manifest
  ai_gateway.feedback_loop.FeedbackLoop.__init__ → ai_gateway.gateway.get_gateway
  config.reload_config → config.load_dotenv
  generator.pipeline._write_plan_artifacts → generator.intract_manifest.write_intract_manifest
  generator.pipeline._write_plan_artifacts → generator.testql_scenario.write_testql_scenario
  generator.pipeline._finalize → generator.pipeline._container_logs
  generator.pipeline._finalize → generator.session.write_session_artifacts
  generator.pipeline.run_pipeline → generator.pipeline._finalize
  generator.pipeline.run_pipeline → planner.simulator.plan_intent
  generator.intent_generator.IntentGenerator.__init__ → dsl.schema.get_system_prompt
  generator.intent_generator.IntentGenerator.__init__ → ai_gateway.gateway.get_gateway
  generator.intent_generator.IntentGenerator.generate → generator.intent_generator._build_user_prompt
  generator.intent_generator.IntentGenerator.generate → generator.intent_generator.extract_yaml_from_llm
  generator.intent_generator.IntentGenerator.generate → dsl.schema.validate_yaml_document
  cli.main.CLI.cmd_new → parser.dsl_parser.parse_dsl
  cli.main.CLI.cmd_load → parser.dsl_parser.parse_dsl_file
  cli.main.CLI.cmd_parse → parser.dsl_parser.parse_dsl
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Api (2)

**`API Integration Tests`**
- `GET /health` → `200`
- `GET /api/v1/status` → `200`
- `POST /api/v1/test` → `201`
- assert `status == ok`
- assert `response_time < 1000`

**`Auto-generated API Smoke Tests`**
- assert `_status < 500`
- assert `_status >= 200`
- detectors: FastAPIDetector, TestEndpointDetector, ConfigEndpointDetector

### Integration (1)

**`Auto-generated from Python Tests`**

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/wronai/iterun
# generated in 0.04s
# nodes: 85 | edges: 77 | modules: 22
# CC̄=4.2

HUBS[20]:
  generator.pipeline.run_pipeline
    CC=30  in:3  out:35  total:38
  cli.main.CLI.cmd_execute
    CC=37  in:0  out:37  total:37
  generator.contract_verify.verify_contract
    CC=16  in:1  out:32  total:33
  examples._scripts.verify_expectations.verify
    CC=23  in:1  out:27  total:28
  generator.expectations.check_expectations
    CC=20  in:1  out:23  total:24
  cli.main.CLI.cmd_plan
    CC=11  in:0  out:24  total:24
  cli.main.CLI.cmd_ai_suggest
    CC=11  in:0  out:21  total:21
  generator.intent_generator.IntentGenerator.generate
    CC=11  in:0  out:21  total:21
  examples._scripts.intent_to_openapi.intent_to_openapi
    CC=8  in:1  out:17  total:18
  cli.main.CLI.cmd_ai_chat
    CC=12  in:0  out:18  total:18
  generator.session.write_session_artifacts
    CC=5  in:1  out:16  total:17
  config.load_dotenv
    CC=15  in:1  out:15  total:16
  examples._scripts.annotate_intract.annotate_express
    CC=6  in:1  out:13  total:14
  ai_gateway.gateway.get_gateway
    CC=3  in:13  out:1  total:14
  examples._scripts.annotate_intract._actions
    CC=7  in:2  out:11  total:13
  generator.intract_manifest.parse_api_actions
    CC=6  in:4  out:9  total:13
  examples._scripts.annotate_intract.annotate_python
    CC=5  in:1  out:11  total:12
  planner.simulator._endpoint_to_func_name
    CC=5  in:2  out:10  total:12
  generator.intent_generator.extract_yaml_from_llm
    CC=6  in:1  out:11  total:12
  cli.main.CLI.cmd_ai_health
    CC=4  in:0  out:12  total:12

MODULES:
  ai_gateway.feedback_loop  [2 funcs]
    __init__  CC=3  out:1
    create_feedback_loop  CC=1  out:1
  ai_gateway.gateway  [4 funcs]
    __post_init__  CC=15  out:8
    complete  CC=1  out:2
    get_gateway  CC=3  out:1
    suggest_improvements  CC=1  out:2
  cli.main  [10 funcs]
    cmd_ai_apply  CC=8  out:10
    cmd_ai_chat  CC=12  out:18
    cmd_ai_health  CC=4  out:12
    cmd_ai_suggest  CC=11  out:21
    cmd_execute  CC=37  out:37
    cmd_load  CC=3  out:8
    cmd_models  CC=3  out:9
    cmd_new  CC=4  out:7
    cmd_parse  CC=2  out:4
    cmd_plan  CC=11  out:24
  config  [3 funcs]
    get_config  CC=2  out:1
    load_dotenv  CC=15  out:15
    reload_config  CC=1  out:2
  dsl.schema  [3 funcs]
    get_json_schema  CC=1  out:1
    get_system_prompt  CC=1  out:2
    validate_yaml_document  CC=7  out:7
  examples._scripts.annotate_intract  [6 funcs]
    _actions  CC=7  out:11
    _comment  CC=1  out:1
    _slug  CC=2  out:4
    annotate_express  CC=6  out:13
    annotate_python  CC=5  out:11
    main  CC=3  out:8
  examples._scripts.intent_to_intract  [1 funcs]
    main  CC=3  out:9
  examples._scripts.intent_to_openapi  [3 funcs]
    _slug  CC=2  out:4
    intent_to_openapi  CC=8  out:17
    main  CC=1  out:9
  examples._scripts.intent_to_testql  [1 funcs]
    main  CC=1  out:6
  examples._scripts.verify_expectations  [4 funcs]
    _load_yaml  CC=2  out:2
    _parse_actions  CC=6  out:9
    main  CC=3  out:9
    verify  CC=23  out:27
  executor.runner  [2 funcs]
    __init__  CC=3  out:5
    execute_intent  CC=1  out:2
  generator.contract_verify  [2 funcs]
    verify_contract  CC=16  out:32
    write_contract_artifacts  CC=1  out:2
  generator.expectations  [2 funcs]
    check_expectations  CC=20  out:23
    load_and_check_expectations  CC=4  out:8
  generator.intent_generator  [4 funcs]
    __init__  CC=2  out:2
    generate  CC=11  out:21
    _build_user_prompt  CC=4  out:1
    extract_yaml_from_llm  CC=6  out:11
  generator.intract_manifest  [6 funcs]
    _safe_id  CC=1  out:3
    _slug  CC=2  out:4
    build_intract_manifest  CC=6  out:11
    intent_to_intract_dict  CC=2  out:4
    parse_api_actions  CC=6  out:9
    write_intract_manifest  CC=1  out:5
  generator.pipeline  [4 funcs]
    _container_logs  CC=4  out:3
    _finalize  CC=2  out:3
    _write_plan_artifacts  CC=4  out:8
    run_pipeline  CC=30  out:35
  generator.session  [1 funcs]
    write_session_artifacts  CC=5  out:16
  generator.testql_scenario  [3 funcs]
    _probe_path  CC=1  out:1
    build_testql_scenario  CC=7  out:9
    write_testql_scenario  CC=2  out:7
  parser.dsl_parser  [2 funcs]
    parse_dsl  CC=1  out:2
    parse_dsl_file  CC=1  out:2
  planner.simulator  [4 funcs]
    _generate_fastapi_code  CC=5  out:7
    _generate_flask_code  CC=5  out:5
    _endpoint_to_func_name  CC=5  out:10
    plan_intent  CC=1  out:2
  sdk.client  [4 funcs]
    generate_and_run  CC=3  out:2
    parse  CC=1  out:1
    schema  CC=1  out:1
    validate  CC=2  out:2
  web.app  [14 funcs]
    ai_apply_suggestions  CC=4  out:7
    ai_chat  CC=4  out:7
    ai_complete  CC=3  out:6
    ai_status  CC=2  out:5
    ai_suggest  CC=6  out:8
    execute  CC=5  out:5
    generate_and_run_api  CC=3  out:3
    generate_code  CC=3  out:6
    get_schema  CC=1  out:2
    list_models  CC=2  out:4

EDGES:
  examples._scripts.verify_expectations.verify → examples._scripts.verify_expectations._load_yaml
  examples._scripts.verify_expectations.verify → examples._scripts.verify_expectations._parse_actions
  examples._scripts.verify_expectations.main → examples._scripts.verify_expectations.verify
  generator.intract_manifest.build_intract_manifest → generator.intract_manifest._safe_id
  generator.intract_manifest.build_intract_manifest → generator.intract_manifest.parse_api_actions
  generator.intract_manifest.build_intract_manifest → generator.intract_manifest._slug
  generator.intract_manifest.intent_to_intract_dict → generator.intract_manifest.build_intract_manifest
  generator.intract_manifest.write_intract_manifest → generator.intract_manifest.intent_to_intract_dict
  examples._scripts.intent_to_openapi.intent_to_openapi → examples._scripts.intent_to_openapi._slug
  examples._scripts.intent_to_openapi.main → examples._scripts.intent_to_openapi.intent_to_openapi
  generator.testql_scenario.build_testql_scenario → generator.intract_manifest.parse_api_actions
  generator.testql_scenario.build_testql_scenario → generator.testql_scenario._probe_path
  generator.testql_scenario.write_testql_scenario → generator.testql_scenario.build_testql_scenario
  examples._scripts.intent_to_testql.main → generator.testql_scenario.write_testql_scenario
  generator.contract_verify.write_contract_artifacts → generator.intract_manifest.write_intract_manifest
  generator.contract_verify.write_contract_artifacts → generator.testql_scenario.write_testql_scenario
  generator.contract_verify.verify_contract → generator.contract_verify.write_contract_artifacts
  generator.contract_verify.verify_contract → generator.intract_manifest.parse_api_actions
  generator.contract_verify.verify_contract → generator.expectations.load_and_check_expectations
  generator.expectations.check_expectations → generator.intract_manifest.parse_api_actions
  generator.expectations.load_and_check_expectations → generator.expectations.check_expectations
  executor.runner.Executor.__init__ → config.get_config
  sdk.client.IterunClient.schema → dsl.schema.get_json_schema
  sdk.client.IterunClient.validate → dsl.schema.validate_yaml_document
  sdk.client.IterunClient.generate_and_run → generator.pipeline.run_pipeline
  sdk.client.IterunClient.parse → parser.dsl_parser.parse_dsl
  examples._scripts.annotate_intract._comment → examples._scripts.annotate_intract._slug
  examples._scripts.annotate_intract.annotate_python → examples._scripts.annotate_intract._actions
  examples._scripts.annotate_intract.annotate_express → examples._scripts.annotate_intract._actions
  examples._scripts.annotate_intract.main → examples._scripts.annotate_intract.annotate_python
  examples._scripts.annotate_intract.main → examples._scripts.annotate_intract.annotate_express
  planner.simulator.Planner._generate_fastapi_code → planner.simulator._endpoint_to_func_name
  planner.simulator.Planner._generate_flask_code → planner.simulator._endpoint_to_func_name
  examples._scripts.intent_to_intract.main → generator.intract_manifest.write_intract_manifest
  ai_gateway.feedback_loop.FeedbackLoop.__init__ → ai_gateway.gateway.get_gateway
  config.reload_config → config.load_dotenv
  generator.pipeline._write_plan_artifacts → generator.intract_manifest.write_intract_manifest
  generator.pipeline._write_plan_artifacts → generator.testql_scenario.write_testql_scenario
  generator.pipeline._finalize → generator.pipeline._container_logs
  generator.pipeline._finalize → generator.session.write_session_artifacts
  generator.pipeline.run_pipeline → generator.pipeline._finalize
  generator.pipeline.run_pipeline → planner.simulator.plan_intent
  generator.intent_generator.IntentGenerator.__init__ → dsl.schema.get_system_prompt
  generator.intent_generator.IntentGenerator.__init__ → ai_gateway.gateway.get_gateway
  generator.intent_generator.IntentGenerator.generate → generator.intent_generator._build_user_prompt
  generator.intent_generator.IntentGenerator.generate → generator.intent_generator.extract_yaml_from_llm
  generator.intent_generator.IntentGenerator.generate → dsl.schema.validate_yaml_document
  cli.main.CLI.cmd_new → parser.dsl_parser.parse_dsl
  cli.main.CLI.cmd_load → parser.dsl_parser.parse_dsl_file
  cli.main.CLI.cmd_parse → parser.dsl_parser.parse_dsl
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 94f 8624L | python:36,shell:24,txt:17,yaml:15,toml:1 | 2026-06-06
# generated in 0.02s
# CC̅=4.2 | critical:10/235 | dups:0 | cycles:0

HEALTH[13]:
  🔴 GOD   executor/runner.py = 614L, 4 classes, 20m, max CC=13
  🔴 GOD   web/app.py = 523L, 9 classes, 25m, max CC=6
  🔴 GOD   ai_gateway/gateway.py = 644L, 4 classes, 20m, max CC=15
  🟡 CC    verify CC=23 (limit:15)
  🟡 CC    verify_contract CC=16 (limit:15)
  🟡 CC    check_expectations CC=20 (limit:15)
  🟡 CC    suggest_next_steps CC=17 (limit:15)
  🟡 CC    load_dotenv CC=15 (limit:15)
  🟡 CC    run_pipeline CC=30 (limit:15)
  🟡 CC    cmd_execute CC=37 (limit:15)
  🟡 CC    interactive_mode CC=30 (limit:15)
  🟡 CC    main CC=72 (limit:15)
  🟡 CC    __post_init__ CC=15 (limit:15)

REFACTOR[4]:
  1. split executor/runner.py  (god module)
  2. split web/app.py  (god module)
  3. split ai_gateway/gateway.py  (god module)
  4. split 10 high-CC methods  (CC>15)

PIPELINES[145]:
  [1] Src [main]: main → verify → _load_yaml
      PURITY: 100% pure
  [2] Src [main]: main → intent_to_openapi → _slug
      PURITY: 100% pure
  [3] Src [__getattr__]: __getattr__
      PURITY: 100% pure
  [4] Src [main]: main → write_testql_scenario → build_testql_scenario → parse_api_actions
      PURITY: 100% pure
  [5] Src [add_check]: add_check
      PURITY: 100% pure
  [6] Src [add_log]: add_log
      PURITY: 100% pure
  [7] Src [to_dict]: to_dict
      PURITY: 100% pure
  [8] Src [__init__]: __init__ → get_config
      PURITY: 100% pure
  [9] Src [execute]: execute
      PURITY: 100% pure
  [10] Src [_validate_and_fix]: _validate_and_fix
      PURITY: 100% pure
  [11] Src [_validate_endpoints]: _validate_endpoints
      PURITY: 100% pure
  [12] Src [_attempt_fix]: _attempt_fix
      PURITY: 100% pure
  [13] Src [_restart_container]: _restart_container
      PURITY: 100% pure
  [14] Src [_write_artifacts]: _write_artifacts
      PURITY: 100% pure
  [15] Src [_find_available_port]: _find_available_port
      PURITY: 100% pure
  [16] Src [_execute_docker]: _execute_docker
      PURITY: 100% pure
  [17] Src [_execute_local]: _execute_local
      PURITY: 100% pure
  [18] Src [get_container_logs]: get_container_logs
      PURITY: 100% pure
  [19] Src [cleanup]: cleanup
      PURITY: 100% pure
  [20] Src [__init__]: __init__
      PURITY: 100% pure
  [21] Src [schema]: schema → get_json_schema
      PURITY: 100% pure
  [22] Src [validate]: validate → validate_yaml_document → parse_dsl
      PURITY: 100% pure
  [23] Src [generate]: generate
      PURITY: 100% pure
  [24] Src [generate_and_run]: generate_and_run → run_pipeline → _finalize → _container_logs
      PURITY: 100% pure
  [25] Src [parse]: parse → parse_dsl
      PURITY: 100% pure
  [26] Src [_remote_generate]: _remote_generate
      PURITY: 100% pure
  [27] Src [_remote_pipeline]: _remote_pipeline
      PURITY: 100% pure
  [28] Src [main]: main → annotate_python → _actions
      PURITY: 100% pure
  [29] Src [add_log]: add_log
      PURITY: 100% pure
  [30] Src [dry_run]: dry_run
      PURITY: 100% pure
  [31] Src [_generate_python_code]: _generate_python_code
      PURITY: 100% pure
  [32] Src [_generate_fastapi_code]: _generate_fastapi_code → _endpoint_to_func_name
      PURITY: 100% pure
  [33] Src [_generate_flask_code]: _generate_flask_code → _endpoint_to_func_name
      PURITY: 100% pure
  [34] Src [_generate_node_code]: _generate_node_code
      PURITY: 100% pure
  [35] Src [_generate_express_code]: _generate_express_code
      PURITY: 100% pure
  [36] Src [_generate_dockerfile]: _generate_dockerfile
      PURITY: 100% pure
  [37] Src [_simulate_action]: _simulate_action
      PURITY: 100% pure
  [38] Src [_estimate_resources]: _estimate_resources
      PURITY: 100% pure
  [39] Src [main]: main → write_intract_manifest → intent_to_intract_dict → build_intract_manifest → ...(1 more)
      PURITY: 100% pure
  [40] Src [to_dict]: to_dict
      PURITY: 100% pure
  [41] Src [__init__]: __init__ → get_gateway
      PURITY: 100% pure
  [42] Src [analyze]: analyze
      PURITY: 100% pure
  [43] Src [apply_suggestions]: apply_suggestions
      PURITY: 100% pure
  [44] Src [iterate]: iterate
      PURITY: 100% pure
  [45] Src [suggest_next_steps]: suggest_next_steps
      PURITY: 100% pure
  [46] Src [_build_analysis_prompt]: _build_analysis_prompt
      PURITY: 100% pure
  [47] Src [_parse_suggestions]: _parse_suggestions
      PURITY: 100% pure
  [48] Src [_extract_action]: _extract_action
      PURITY: 100% pure
  [49] Src [_parse_action]: _parse_action
      PURITY: 100% pure
  [50] Src [_process_user_feedback]: _process_user_feedback
      PURITY: 100% pure

LAYERS:
  cli/                            CC̄=9.6    ←in:0  →out:18  !! split
  │ !! main                       928L  2C   25m  CC=72     ←0
  │ __init__                    20L  0C    1m  CC=3      ←0
  │ __main__                     4L  0C    0m  CC=0.0    ←0
  │
  generator/                      CC̄=5.4    ←in:7  →out:6
  │ intent_generator           232L  3C    7m  CC=11     ←0
  │ !! pipeline                   220L  1C    5m  CC=30     ←3
  │ !! contract_verify            201L  1C    8m  CC=16     ←1
  │ intract_manifest           106L  0C    6m  CC=6      ←6
  │ !! expectations                89L  0C    4m  CC=20     ←1
  │ testql_scenario             67L  0C    3m  CC=7      ←4
  │ session                     52L  0C    1m  CC=5      ←1
  │ __init__                    23L  0C    0m  CC=0.0    ←0
  │
  executor/                       CC̄=4.8    ←in:3  →out:1
  │ !! runner                     614L  4C   20m  CC=13     ←3
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │
  ai_gateway/                     CC̄=4.6    ←in:14  →out:1
  │ !! gateway                    644L  4C   20m  CC=15     ←4
  │ !! feedback_loop              384L  3C   14m  CC=17     ←2
  │ __init__                    34L  0C    0m  CC=0.0    ←0
  │
  parser/                         CC̄=3.5    ←in:7  →out:0
  │ dsl_parser                 263L  3C   13m  CC=8      ←5
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │
  planner/                        CC̄=3.2    ←in:3  →out:0
  │ simulator                  374L  2C   17m  CC=9      ←3
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=3.1    ←in:0  →out:0
  │ !! planfile.yaml              643L  0C    0m  CC=0.0    ←0
  │ !! goal.yaml                  512L  0C    0m  CC=0.0    ←0
  │ Makefile                   222L  0C    0m  CC=0.0    ←0
  │ !! config                     168L  1C    8m  CC=15     ←4
  │ run.sh                     160L  0C    0m  CC=0.0    ←0
  │ pyproject.toml             105L  0C    0m  CC=0.0    ←0
  │ prefact.yaml                82L  0C    0m  CC=0.0    ←0
  │ project.sh                  59L  0C    0m  CC=0.0    ←0
  │ pyqual.yaml                 55L  0C    0m  CC=0.0    ←0
  │ requirements.txt            20L  0C    0m  CC=0.0    ←0
  │ tree.sh                      1L  0C    0m  CC=0.0    ←0
  │
  web/                            CC̄=2.7    ←in:0  →out:14  !! split
  │ !! app                        523L  9C   25m  CC=6      ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │
  examples/                       CC̄=2.4    ←in:0  →out:0
  │ _verify.sh                 134L  0C    9m  CC=0.0    ←0
  │ !! verify_expectations        127L  0C    5m  CC=23     ←0
  │ annotate_intract            97L  0C    6m  CC=7      ←0
  │ _common.sh                  95L  0C    6m  CC=0.0    ←0
  │ intent_to_openapi           76L  0C    3m  CC=8      ←0
  │ run.sh                      40L  0C    0m  CC=0.0    ←0
  │ run-e2e.sh                  31L  0C    0m  CC=0.0    ←0
  │ expectations.yaml           31L  0C    0m  CC=0.0    ←0
  │ intent_to_intract           29L  0C    1m  CC=3      ←0
  │ expectations.yaml           27L  0C    0m  CC=0.0    ←0
  │ intent_to_testql            26L  0C    1m  CC=1      ←0
  │ expectations.yaml           26L  0C    0m  CC=0.0    ←0
  │ run-resilience.sh           25L  0C    0m  CC=0.0    ←0
  │ run-all.sh                  24L  0C    0m  CC=0.0    ←0
  │ expectations.yaml           24L  0C    0m  CC=0.0    ←0
  │ run.sh                      22L  0C    0m  CC=0.0    ←0
  │ expectations.yaml           20L  0C    0m  CC=0.0    ←0
  │ expectations.yaml           20L  0C    0m  CC=0.0    ←0
  │ expectations.yaml           19L  0C    0m  CC=0.0    ←0
  │ run.sh                      17L  0C    0m  CC=0.0    ←0
  │ run.sh                      16L  0C    0m  CC=0.0    ←0
  │ run.sh                      16L  0C    0m  CC=0.0    ←0
  │ run.sh                      16L  0C    0m  CC=0.0    ←0
  │ run.sh                      14L  0C    0m  CC=0.0    ←0
  │ expectations.yaml           13L  0C    0m  CC=0.0    ←0
  │ run.sh                      13L  0C    0m  CC=0.0    ←0
  │ run.sh                      11L  0C    0m  CC=0.0    ←0
  │ run.sh                      10L  0C    0m  CC=0.0    ←0
  │ run.sh                      10L  0C    0m  CC=0.0    ←0
  │ run.sh                       9L  0C    0m  CC=0.0    ←0
  │ run.sh                       9L  0C    0m  CC=0.0    ←0
  │ run.sh                       8L  0C    0m  CC=0.0    ←0
  │ run.sh                       8L  0C    0m  CC=0.0    ←0
  │ run.sh                       8L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │ prompt.txt                   1L  0C    0m  CC=0.0    ←0
  │
  dsl/                            CC̄=2.4    ←in:8  →out:1
  │ schema                     164L  5C    5m  CC=7      ←4
  │ __init__                    17L  0C    0m  CC=0.0    ←0
  │
  sdk/                            CC̄=2.1    ←in:0  →out:4
  │ client                     119L  1C    8m  CC=3      ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │
  ir/                             CC̄=1.1    ←in:0  →out:0
  │ models                     223L  8C   14m  CC=2      ←0
  │ __init__                     9L  0C    0m  CC=0.0    ←0
  │
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-from-pytests.testql.toon.yaml    42L  0C    0m  CC=0.0    ←0
  │ generated-api-smoke.testql.toon.yaml    40L  0C    0m  CC=0.0    ←0
  │ generated-api-integration.testql.toon.yaml    18L  0C    0m  CC=0.0    ←0
  │
  mcp/                            CC̄=0.0    ←in:0  →out:0
  │ server                      82L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │

COUPLING:
                                   cli         ai_gateway                web          generator                dsl             parser             config           executor                sdk            planner  examples._scripts
                cli                 ──                  6                                     3                  2                  3                  2                  1                                     1                     !! fan-out
         ai_gateway                 ←6                 ──                 ←7                 ←1                                                        1                                                                              hub
                web                                     7                 ──                  1                  2                  1                  1                  1                                     1                     !! fan-out
          generator                 ←3                  1                 ←1                 ──                  2                  1                                     1                 ←1                  1                 ←2  hub
                dsl                 ←2                                    ←2                 ←2                 ──                  1                                                       ←2                                        hub
             parser                 ←3                                    ←1                 ←1                 ←1                 ──                                                       ←1                                        hub
             config                 ←2                 ←1                 ←1                                                                          ──                 ←1                                                           hub
           executor                 ←1                                    ←1                 ←1                                                        1                 ──                                                         
                sdk                                                                           1                  2                  1                                                       ──                                      
            planner                 ←1                                    ←1                 ←1                                                                                                                ──                   
  examples._scripts                                                                           2                                                                                                                                   ──
  CYCLES: none
  HUB: config/ (fan-in=5)
  HUB: ai_gateway/ (fan-in=14)
  HUB: dsl/ (fan-in=8)
  HUB: parser/ (fan-in=7)
  HUB: generator/ (fan-in=7)
  SMELL: web/ fan-out=14 → split needed
  SMELL: cli/ fan-out=18 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 5 groups | 41f 6022L | 2026-06-06

SUMMARY:
  files_scanned: 41
  total_lines:   6022
  dup_groups:    5
  dup_fragments: 32
  saved_lines:   94
  scan_ms:       2271

HOTSPOTS[7] (files with most duplication):
  examples/01-user-api/generated/app.py  dup=21L  groups=1  frags=7  (0.3%)
  generated/app.py  dup=21L  groups=1  frags=7  (0.3%)
  generator/intract_manifest.py  dup=17L  groups=2  frags=2  (0.3%)
  examples/_scripts/verify_expectations.py  dup=14L  groups=1  frags=1  (0.2%)
  parser/dsl_parser.py  dup=8L  groups=1  frags=2  (0.1%)
  planner/simulator.py  dup=7L  groups=2  frags=2  (0.1%)
  examples/02-ping-smoke/generated/app.py  dup=6L  groups=1  frags=2  (0.1%)

DUPLICATES[5] (ranked by impact):
  [032a6ddde45774c9] ! STRU  ping  L=3 N=22 saved=63 sim=1.00
      examples/01-user-api/generated/app.py:9-11  (ping)
      examples/01-user-api/generated/app.py:14-16  (health)
      examples/01-user-api/generated/app.py:19-21  (users)
      examples/01-user-api/generated/app.py:24-26  (users_post)
      examples/01-user-api/generated/app.py:29-31  (users_by_id)
      examples/01-user-api/generated/app.py:34-36  (users_by_id_put)
      examples/01-user-api/generated/app.py:39-41  (users_by_id_delete)
      examples/02-ping-smoke/generated/app.py:9-11  (ping)
      examples/02-ping-smoke/generated/app.py:14-16  (health)
      examples/05-ir-show/generated/app.py:9-11  (ping)
      examples/06-iterate-workflow/generated/app.py:9-11  (ping)
      examples/07-execution-smoke/generated/app.py:9-11  (ping)
      examples/07-execution-smoke/generated/app.py:14-16  (health)
      examples/09-e2e-ping-verify/generated/app.py:10-12  (ping)
      examples/09-e2e-ping-verify/generated/app.py:16-18  (health)
      generated/app.py:9-11  (ping)
      generated/app.py:14-16  (health)
      generated/app.py:19-21  (users)
      generated/app.py:24-26  (users_post)
      generated/app.py:29-31  (users_by_id)
      generated/app.py:34-36  (users_by_id_put)
      generated/app.py:39-41  (users_by_id_delete)
  [ef2fcfb176592b6f]   STRU  _parse_actions  L=14 N=2 saved=14 sim=1.00
      examples/_scripts/verify_expectations.py:22-35  (_parse_actions)
      generator/intract_manifest.py:21-34  (parse_api_actions)
  [d1ab1a804f1b435b]   STRU  parse_dsl  L=4 N=3 saved=8 sim=1.00
      parser/dsl_parser.py:254-257  (parse_dsl)
      parser/dsl_parser.py:260-263  (parse_dsl_file)
      planner/simulator.py:371-374  (plan_intent)
  [ad19acd787fb5e4b]   EXAC  _slug  L=3 N=3 saved=6 sim=1.00
      examples/_scripts/annotate_intract.py:13-15  (_slug)
      examples/_scripts/intent_to_openapi.py:13-15  (_slug)
      generator/intract_manifest.py:12-14  (_slug)
  [f041dec9367328ca]   EXAC  add_log  L=3 N=2 saved=3 sim=1.00
      executor/runner.py:93-95  (add_log)
      planner/simulator.py:51-53  (add_log)

REFACTOR[5] (ranked by priority):
  [1] ○ extract_function   → utils/ping.py
      WHY: 22 occurrences of 3-line block across 7 files — saves 63 lines
      FILES: examples/01-user-api/generated/app.py, examples/02-ping-smoke/generated/app.py, examples/05-ir-show/generated/app.py, examples/06-iterate-workflow/generated/app.py, examples/07-execution-smoke/generated/app.py +2 more
  [2] ○ extract_function   → utils/_parse_actions.py
      WHY: 2 occurrences of 14-line block across 2 files — saves 14 lines
      FILES: examples/_scripts/verify_expectations.py, generator/intract_manifest.py
  [3] ○ extract_function   → utils/parse_dsl.py
      WHY: 3 occurrences of 4-line block across 2 files — saves 8 lines
      FILES: parser/dsl_parser.py, planner/simulator.py
  [4] ○ extract_function   → utils/_slug.py
      WHY: 3 occurrences of 3-line block across 3 files — saves 6 lines
      FILES: examples/_scripts/annotate_intract.py, examples/_scripts/intent_to_openapi.py, generator/intract_manifest.py
  [5] ○ extract_function   → utils/add_log.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: executor/runner.py, planner/simulator.py

QUICK_WINS[4] (low risk, high savings — do first):
  [1] extract_function   saved=63L  → utils/ping.py
      FILES: app.py, app.py, app.py +4
  [2] extract_function   saved=14L  → utils/_parse_actions.py
      FILES: verify_expectations.py, intract_manifest.py
  [3] extract_function   saved=8L  → utils/parse_dsl.py
      FILES: dsl_parser.py, simulator.py
  [4] extract_function   saved=6L  → utils/_slug.py
      FILES: annotate_intract.py, intent_to_openapi.py, intract_manifest.py

DEPENDENCY_RISK[5] (duplicates spanning multiple packages):
  ping  packages=2  files=7
      examples/01-user-api/generated/app.py
      examples/02-ping-smoke/generated/app.py
      examples/05-ir-show/generated/app.py
      examples/06-iterate-workflow/generated/app.py
      +3 more
  _parse_actions  packages=2  files=2
      examples/_scripts/verify_expectations.py
      generator/intract_manifest.py
  parse_dsl  packages=2  files=2
      parser/dsl_parser.py
      planner/simulator.py
  _slug  packages=2  files=3
      examples/_scripts/annotate_intract.py
      examples/_scripts/intent_to_openapi.py
      generator/intract_manifest.py
  add_log  packages=2  files=2
      executor/runner.py
      planner/simulator.py

EFFORT_ESTIMATE (total ≈ 6.3h):
  hard   ping                                saved=63L  ~252min
  medium _parse_actions                      saved=14L  ~56min
  medium parse_dsl                           saved=8L  ~32min
  easy   _slug                               saved=6L  ~24min
  easy   add_log                             saved=3L  ~12min

METRICS-TARGET:
  dup_groups:  5 → 0
  saved_lines: 94 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 204 func | 19f | 2026-06-06
# generated in 0.00s

NEXT[10] (ranked by impact):
  [1] !! SPLIT           cli/main.py
      WHY: 928L, 2 classes, max CC=72
      EFFORT: ~4h  IMPACT: 66816

  [2] !! SPLIT           ai_gateway/gateway.py
      WHY: 644L, 4 classes, max CC=15
      EFFORT: ~4h  IMPACT: 9660

  [3] !! SPLIT-FUNC      main  CC=72  fan=39
      WHY: CC=72 exceeds 15
      EFFORT: ~1h  IMPACT: 2808

  [4] !! SPLIT-FUNC      run_pipeline  CC=30  fan=23
      WHY: CC=30 exceeds 15
      EFFORT: ~1h  IMPACT: 690

  [5] !! SPLIT-FUNC      CLI.interactive_mode  CC=30  fan=23
      WHY: CC=30 exceeds 15
      EFFORT: ~1h  IMPACT: 690

  [6] !! SPLIT-FUNC      CLI.cmd_execute  CC=37  fan=15
      WHY: CC=37 exceeds 15
      EFFORT: ~1h  IMPACT: 555

  [7] !  SPLIT-FUNC      verify_contract  CC=16  fan=26
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 416

  [8] !  SPLIT-FUNC      check_expectations  CC=20  fan=11
      WHY: CC=20 exceeds 15
      EFFORT: ~1h  IMPACT: 220

  [9] !  SPLIT-FUNC      load_dotenv  CC=15  fan=14
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 210

  [10] !! SPLIT           planfile.yaml
      WHY: 643L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0


RISKS[3]:
  ⚠ Splitting cli/main.py may break 25 import paths
  ⚠ Splitting ai_gateway/gateway.py may break 20 import paths
  ⚠ Splitting planfile.yaml may break 0 import paths

METRICS-TARGET:
  CC̄:          4.5 → ≤3.1
  max-CC:      72 → ≤20
  god-modules: 6 → 0
  high-CC(≥15): 9 → ≤4
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  prev CC̄=4.2 → now CC̄=4.5
```

### Validation (`project/validation.toon.yaml`)

```toon markpact:analysis path=project/validation.toon.yaml
# vallm batch | 38f | 9✓ 0⚠ 19✗ | 2026-03-31

SUMMARY:
  scanned: 38  passed: 9 (23.7%)  warnings: 0  errors: 19  unsupported: 10

ERRORS[19]{path,score}:
  ai_gateway/__init__.py,0.57
    issues[2]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'gateway' not found,1
      python.import.resolvable,error,Module 'feedback_loop' not found,12
  cli/__init__.py,0.57
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'main' not found,1
  executor/__init__.py,0.57
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'runner' not found,1
  ir/__init__.py,0.57
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'models' not found,1
  parser/__init__.py,0.57
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'dsl_parser' not found,1
  planner/__init__.py,0.57
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'simulator' not found,1
  web/__init__.py,0.57
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'app' not found,1
  tests/e2e/test_ai_gateway.py,0.64
    issues[26]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'ir.models' not found,14
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,22
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,30
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,41
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,55
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,67
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,70
      python.import.resolvable,error,Module 'config' not found,81
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,104
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,121
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,129
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,142
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,153
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,166
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,194
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,202
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,213
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,227
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,239
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,266
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,282
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,293
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,318
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,331
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,352
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,361
  web/app.py,0.71
    issues[15]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'fastapi' not found,6
      python.import.resolvable,error,Module 'fastapi.responses' not found,7
      python.import.resolvable,error,Module 'fastapi.staticfiles' not found,8
      python.import.resolvable,error,Module 'fastapi.templating' not found,9
      python.import.resolvable,error,Module 'ir.models' not found,19
      python.import.resolvable,error,Module 'parser.dsl_parser' not found,20
      python.import.resolvable,error,Module 'planner.simulator' not found,21
      python.import.resolvable,error,Module 'executor.runner' not found,22
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,26
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,27
      python.import.resolvable,error,Module 'executor.runner' not found,224
      python.import.resolvable,error,Module 'config' not found,228
      python.import.resolvable,error,Module 'executor.runner' not found,257
      python.import.resolvable,error,Module 'config' not found,455
      python.import.resolvable,error,Module 'parser.dsl_parser' not found,152
  cli/main.py,0.72
    issues[9]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'ir.models' not found,16
      python.import.resolvable,error,Module 'parser.dsl_parser' not found,17
      python.import.resolvable,error,Module 'planner.simulator' not found,18
      python.import.resolvable,error,Module 'executor.runner' not found,19
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,23
      python.import.resolvable,error,Module 'ai_gateway.feedback_loop' not found,24
      python.import.resolvable,error,Module 'config' not found,229
      python.import.resolvable,error,Module 'config' not found,270
      python.import.resolvable,error,Module 'executor.runner' not found,350
  config.py,0.82
    issues[3]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'getv' not found,13
      python.import.resolvable,error,Module 'getv' not found,28
      python.import.resolvable,error,Module 'getv.integrations.pydantic_env' not found,29
  tests/e2e/test_shell.py,0.83
    issues[4]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'ir.models' not found,15
      python.import.resolvable,error,Module 'parser.dsl_parser' not found,16
      python.import.resolvable,error,Module 'planner.simulator' not found,17
      python.import.resolvable,error,Module 'cli.main' not found,18
  ai_gateway/feedback_loop.py,0.86
    issues[3]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'ir.models' not found,15
      python.import.resolvable,error,Module 'ai_gateway.gateway' not found,16
      python.import.resolvable,error,Module 'parser.dsl_parser' not found,333
  tests/conftest.py,0.89
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'ir.models' not found,47
  planner/simulator.py,0.91
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'ir.models' not found,13
  tests/e2e/test_web.py,0.91
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'web.app' not found,14
  ai_gateway/gateway.py,0.92
    issues[2]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'ir.models' not found,24
      python.import.resolvable,error,Module 'config' not found,220
  executor/runner.py,0.93
    issues[2]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'ir.models' not found,19
      python.import.resolvable,error,Module 'config' not found,20
  parser/dsl_parser.py,0.93
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'ir.models' not found,14

UNSUPPORTED[4]{bucket,count}:
  *.md,5
  *.txt,1
  *.example,1
  other,3
```

## Intent

DSL-based intent execution system with iterative refinement, featuring AI-powered suggestions via Ollama, safe simulation, and automatic health validation.

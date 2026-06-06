# 08 — LLM Generate (SDK / MCP)

Ten sam flow co pozostałe przykłady (`prompt.txt` → `generate`). Dodatkowo: SDK i MCP.

## Uruchomienie

```bash
./run.sh
```

## Komendy

```bash
iterun generate "$(cat prompt.txt)" -o generated/ --run --quiet
iterun generate "$(cat prompt.txt)" -o generated/ --execute --quiet
iterun schema
iterun validate generated/intent.yaml
```

## SDK

```python
from sdk import IterunClient

client = IterunClient()
result = client.generate_and_run(
    open("prompt.txt").read(),
    output_dir="generated",
    execute=False,
)
print(result.yaml_path)
```

## MCP

```bash
pip install mcp litellm
python -m mcp.server
```

## Wymagania

`pip install -e ".[ai]"` + `.env` z `OPENROUTER_API_KEY` lub lokalny Ollama.

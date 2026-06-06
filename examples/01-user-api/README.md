# 01 — User API (FastAPI CRUD)

Pełne REST API użytkowników — prompt → LLM → **iterun.yaml** → plan (+ opcjonalnie execute).

## Uruchomienie

```bash
./run.sh
```

## Komendy

```bash
# generate + plan
iterun generate "$(cat prompt.txt)" -o generated/ --run --quiet

# prompt → plan → Docker
ITERUN_EXECUTE=1 ./run.sh
# lub:
iterun generate "$(cat prompt.txt)" -o generated/ --execute --quiet
```

## `prompt.txt` — źródło

Prompt NL w repo. `generated/iterun.yaml` powstaje przy `generate`. Logi sesji: `generated/session.json`.

## `generated/`

| Plik | Skąd |
|------|------|
| `iterun.yaml` | LLM + validate-retry |
| `session.json` | pełny log sesji (prompt → verify) |
| `plan.result.json` | plan w pipeline |
| `app.py`, `Dockerfile` | plan w pipeline |

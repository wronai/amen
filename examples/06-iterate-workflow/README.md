# 06 — Iterate Workflow

Generate + plan początkowy. Pełny cykl iterate → ITERUN → execute w interaktywnej powłoce.

## Uruchomienie (generate + plan)

```bash
./run.sh
```

## Interaktywna iteracja

```bash
python -m cli
```

```
intent> load examples/06-iterate-workflow/generated/intent.yaml
intent> plan
intent> iterate
> action=api.expose GET /health
> action=api.expose POST /data
> done
intent> plan
intent> iterun
intent> execute
```

## Jedna komenda (generate → execute)

```bash
iterun generate "$(cat prompt.txt)" -o generated/ --execute --quiet
```

## `generated/`

`intent.yaml`, `plan.result.json`, `app.py`, `Dockerfile`

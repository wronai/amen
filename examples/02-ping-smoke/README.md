# 02 — Ping Smoke

Minimalny intent: `/ping` + `/health`. Szybki smoke test generatora i planera.

## Uruchomienie

```bash
./run.sh
```

## Komendy

```bash
iterun generate "$(cat prompt.txt)" -o generated/ --run --quiet
```

## `generated/`

`intent.yaml`, `plan.result.json`, `app.py`, `Dockerfile`

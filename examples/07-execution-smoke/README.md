# 07 — Execution Smoke

Generate+plan własnego intentu + 02/03/04. Opcjonalne wykonanie Docker.

## Uruchomienie

```bash
# tylko plan (domyślnie)
./run.sh

# z execute
ITERUN_EXECUTE=1 ./run.sh
```

## Komendy

```bash
iterun generate "$(cat prompt.txt)" -o generated/ --execute --quiet
```

## `generated/`

`intent.yaml`, `plan.result.json`, `app.py`, `Dockerfile`

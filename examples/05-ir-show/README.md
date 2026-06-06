# 05 — IR Show

Prompt → IntentIR (różne typy akcji) + dry-run.

## Uruchomienie

```bash
./run.sh
```

## Komendy

```bash
iterun generate "$(cat prompt.txt)" -o generated/ --run --quiet
iterun parse generated/iterun.yaml --output-dir generated/ --quiet
```

## `generated/`

| Plik | Opis |
|------|------|
| `iterun.yaml` | LLM |
| `ir.json` | IntentIR (parse) |
| `plan.result.json` | Wynik dry-run |
| `app.py`, `Dockerfile` | Wygenerowany kod |

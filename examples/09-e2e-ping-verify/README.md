# 09 — E2E Ping Verify (testql + intract)

Flow: **prompt → iterun.yaml → intract.yaml (kontrakt) → service → walidacja**.

## Uruchomienie

```bash
./run.sh
```

## Co ląduje w `generated/`

| Plik | Skąd |
|------|------|
| `iterun.yaml` | LLM z `prompt.txt` |
| `intract.yaml` | **auto** — `generator/intract_manifest.py` |
| `service.testql.toon.yaml` | auto — `generator/testql_scenario.py` |
| `verify.result.json` | auto — `iterun generate --verify` |
| `openapi.yaml` | auto — `intent_to_openapi.py` (przed intract) |
| `app.py`, `Dockerfile` | plan + execute |

## Komendy ręczne

```bash
iterun generate "$(cat prompt.txt)" -o generated/ --execute --verify --quiet
testql run generated/service.testql.toon.yaml --url "$(jq -r .service_url generated/verify.result.json)"
python ../_scripts/intent_to_intract.py generated/iterun.yaml -o generated/intract.yaml -p prompt.txt
python -m intract validate generated/ --manifest generated/intract.yaml
testql run tests/service.testql.toon.yaml --url http://localhost:<port>
```

## Wymagania

`pip install -e ".[ai]"`, `testql`, `intract` (semcod/intract), Docker.

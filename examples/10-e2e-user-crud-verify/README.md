# 10 — E2E User CRUD Verify

Pełny CRUD z promptu — weryfikacja 7 endpointów przez testql + intract + `expectations.yaml`.

## Uruchomienie

```bash
./run.sh
```

## Oneliner (bez run.sh)

```bash
iterun generate "$(cat prompt.txt)" -o generated/ --execute --json | jq '.execution.endpoints[0]'
testql run tests/service.testql.toon.yaml --url "$(docker ps --filter name=intent-user-api --format '{{.Ports}}' | grep -oE '[0-9]+' | head -1 | xargs -I{} echo http://localhost:{})"
```

## Co sprawdzamy

1. **iterun.yaml** — czy LLM dodał wszystkie akcje z promptu
2. **testql** — czy kontener odpowiada HTTP 200
3. **intract** — `generated/intract.yaml` (auto z intent) vs kod + openapi
4. **expectations** — pola JSON (`status`, `endpoint`, `method`)

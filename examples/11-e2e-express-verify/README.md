# 11 — E2E Express Verify

Node/Express z promptu — testql + intract na `app.js` w kontenerze.

## Uruchomienie

```bash
./run.sh
```

## Uwagi

- Express startuje wolniej niż FastAPI — `WAIT 3000` w scenariuszu testql
- `expectations.yaml` wymaga `framework: express`
- `generated/intract.yaml` powstaje z intent (nie ręczny fixture)
- Intract skanuje `generated/Dockerfile` + `generated/openapi.yaml`

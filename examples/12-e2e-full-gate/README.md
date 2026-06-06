# 12 — E2E Full Gate (iterun + intract + testql)

```text
prompt.txt
  → iterun generate --execute
  → generated/iterun.yaml
  → generated/intract.yaml      # kontrakt (nie ręczny fixture!)
  → generated/openapi.yaml
  → Docker service
  → intract validate / graph / scan
  → testql run + testql auto
  → verify_expectations.py
```

## Uruchomienie

```bash
./run.sh
```

## `generated/intract.yaml`

Powstaje automatycznie z `iterun.yaml` — lista `require: implement.*` odzwierciedla `api.expose` z promptu. Nie trzymaj ręcznego `intract.yaml` w katalogu przykładu.

```bash
python ../_scripts/intent_to_intract.py generated/iterun.yaml \
  -o generated/intract.yaml -p prompt.txt
```

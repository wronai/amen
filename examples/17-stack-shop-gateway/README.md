# 17 — STACK: Shop Gateway

**Jedna aplikacja, trzy Dockerfile + `docker-compose.yaml`:**

| Serwis | Technologia | Port hosta |
|--------|-------------|------------|
| `api-gateway` | FastAPI (proxy) | 18080 |
| `users-service` | FastAPI (wewnętrzny) | — |
| `catalog-service` | Express (wewnętrzny) | — |

## Uruchomienie

```bash
./run.sh
curl http://localhost:18080/ping
curl http://localhost:18080/users
```

## Z promptu (LLM)

```bash
iterun generate "$(cat prompt.txt)" -o generated/ --run --execute
```

## Dwa miejsca — ale jeden `iterun.yaml`

| Plik | Rola |
|------|------|
| **`iterun.yaml`** (w katalogu przykładu) | Źródło STACK w repo — **jedyna** paczka DSL |
| **`generated/`** | Wynik plan/execute: compose, `services/*/`, `plan.result.json` |

Przykłady 01–16 trzymają `iterun.yaml` tylko w `generated/` (z LLM). STACK ma ręczną specyfikację w repo — **nie jest już kopiowana** do `generated/`.

```
generated/
├── docker-compose.yaml
└── services/
    ├── api-gateway/Dockerfile + app.py
    ├── users-service/Dockerfile + app.py
    └── catalog-service/Dockerfile + app.js
```

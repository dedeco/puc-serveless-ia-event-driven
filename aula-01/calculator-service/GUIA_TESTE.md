# Guia de Teste - Calculadora Serverless

### Endpoint
**URL:** `https://calculator-service-uucgfw647q-uc.a.run.app`

### Comando para Testar (Curl)
Copie e cole no seu terminal para testar a função deployada:

```bash
TOKEN=$(gcloud auth print-identity-token)
URL="https://calculator-service-uucgfw647q-uc.a.run.app"

curl -X POST $URL \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"operation": "add", "a": 10, "b": 5}'
```

### Exemplos de Requisição (JSON)

**Soma:**
`{"operation": "add", "a": 10, "b": 5}`

**Subtração:**
`{"operation": "subtract", "a": 20, "b": 8}`

**Multiplicação:**
`{"operation": "multiply", "a": 7, "b": 6}`

**Divisão:**
`{"operation": "divide", "a": 100, "b": 4}`

# Guia de Testes Diretos: Aula 3

Este roteiro contem os comandos prontos para execucao. Basta copiar e colar no terminal.

---

## Step 01: Orquestracao Basica
Objetivo: Demonstrar o fluxo sequencial e a atualizacao de estado no Firestore.

```bash
gcloud workflows run order-basic \
  --location=us-central1 \
  --data='{"url": "https://simulator-step1-575401317367.us-central1.run.app", "order_id": "PEDIDO-BASICO-01"}'
```

---

## Step 02: Resiliencia (Retries)
Objetivo: Demonstrar a recuperacao automatica de falhas temporarias (HTTP 503).

```bash
gcloud workflows run order-retries \
  --location=us-central1 \
  --data='{"url": "https://simulator-step2-575401317367.us-central1.run.app", "order_id": "PEDIDO-RETRY-01"}'
```

---

## Step 03: Idempotencia
Objetivo: Garantir que execucoes duplicadas nao gerem efeitos colaterais repetidos. Rode o comando abaixo 2 vezes seguidas.

```bash
gcloud workflows run order-idempotency \
  --location=us-central1 \
  --data='{"url": "https://simulator-step3-575401317367.us-central1.run.app", "order_id": "PEDIDO-IDEM-01"}'
```

---

## Step 04: Dead-Letter Queue (DLQ)
Objetivo: Tratar erros fatais (HTTP 402) enviando a falha para o Pub/Sub.

```bash
gcloud workflows run order-full \
  --location=us-central1 \
  --data='{"url": "https://simulator-step4-575401317367.us-central1.run.app", "order_id": "PEDIDO-FALHA-FATAL"}'
```

### Comando para ler a mensagem na DLQ:
```bash
gcloud pubsub subscriptions pull orders-dlq-sub --auto-ack --limit=1
```

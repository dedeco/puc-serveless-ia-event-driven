# Laboratório Aula 3: Orquestração Serverless

Este laboratório está dividido em 4 etapas evolutivas para ensinar Cloud Workflows.

## Estrutura das Etapas

### [Step 01: Orquestração Básica](./lab/step-01-basic)
- **Foco**: Sintaxe básica (steps, call, args).
- **Cenário**: Um fluxo sequencial que reserva, cobra e envia um pedido.

### [Step 02: Resiliência e Retries](./lab/step-02-retries)
- **Foco**: Tratamento de falhas transitórias.
- **Cenário**: O serviço de pagamento simula instabilidade e o Workflow recupera a transação automaticamente.

### [Step 03: Idempotência](./lab/step-03-idempotency)
- **Foco**: Segurança em repetições.
- **Cenário**: Uso de `Idempotency-Key` para garantir que retries não gerem cobranças duplicadas.

### [Step 04: Dead-Letter Queue (DLQ)](./lab/step-04-full)
- **Foco**: Tratamento de erros fatais.
- **Cenário**: Quando os retries esgotam, o erro é capturado e enviado para um tópico Pub/Sub para auditoria.

## Como Executar
1. Navegue até a pasta do step desejado.
2. Execute o deploy do simulador (Cloud Run) e da infraestrutura (Terraform).
3. Teste o workflow via console ou CLI.

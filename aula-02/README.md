# Prática Aula 2 - Arquitetura Orientada a Eventos

Este projeto demonstra a implementação de uma arquitetura orientada a eventos (EDA) utilizando Google Cloud Pub/Sub e Cloud Functions (2ª Geração).

## Estrutura do Projeto

- `main.tf`: Configuração do Terraform para criar o tópico Pub/Sub, o bucket de código e as Cloud Functions.
- `src/main.py`: Código Python que contém dois handlers: `hello_pubsub` (processador) e `read_model_simulator` (dashboard).
- `src/requirements.txt`: Dependências das funções.

## Como Executar

1. **Inicializar o Terraform:**
   ```bash
   terraform init
   ```

2. **Planejar a Infraestrutura:**
   ```bash
   terraform plan
   ```

3. **Aplicar as Mudanças:**
   ```bash
   terraform apply
   ```

4. **Testar a Arquitetura (Fan-out):**
   Envie uma mensagem para o tópico `orders`. Duas funções serão disparadas simultaneamente!
   ```bash
   ./test_event.sh
   ```

5. **Verificar os Logs:**
   Verifique o log da primeira função:
   ```bash
   gcloud functions logs read process-order --gen2 --region=us-central1 --limit=10
   ```
   Verifique o log da segunda função (Read Model):
   ```bash
   gcloud functions logs read read-model-simulator --gen2 --region=us-central1 --limit=10
   ```

## Conceitos Aplicados

- **Pub/Sub (Publish/Subscribe):** Desacoplamento entre produtores e consumidores.
- **Fan-out:** Uma única mensagem no tópico é entregue a múltiplos assinantes independentes.
- **CQRS (Read Model):** A segunda função demonstra como atualizar uma visão de leitura a partir de eventos de domínio.
- **CloudEvents:** Padrão de payload para eventos GCP.

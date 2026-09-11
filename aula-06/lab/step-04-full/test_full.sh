#!/bin/bash
echo ">>> TESTE STEP 4: Validando o Agente Orientado a Eventos Completo"

# 1. Obter o ID do Projeto ativo do GCP
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "Erro: Projeto GCP não configurado no gcloud CLI."
    exit 1
fi

echo "Projeto GCP ativo: $PROJECT_ID"

# 2. Publicar a primeira falha no Pub/Sub: build-101 (Erro de Conexão -> Reexecução)
echo -e "\n--------------------------------------------------------------"
echo "Publicando evento de falha para o build-101 no Pub/Sub..."
gcloud pubsub topics publish build-failures --message='{"build_id": "build-101"}'

# 3. Publicar a segunda falha no Pub/Sub: build-202 (Erro de Sintaxe -> Alerta Humano)
echo -e "\n--------------------------------------------------------------"
echo "Publicando evento de falha para o build-202 no Pub/Sub..."
gcloud pubsub topics publish build-failures --message='{"build_id": "build-202"}'

echo -e "\n--------------------------------------------------------------"
echo "Sucesso! Eventos publicados."
echo "Como a arquitetura é Event-Driven, o processamento ocorre em segundo plano."
echo "Aguarde de 15 a 30 segundos e acesse o painel do Firestore no Console do GCP."
echo "Você deverá ver a coleção 'build_triages' com os diagnósticos detalhados salvos."
echo "Se preferir, verifique os logs da função executando:"
echo "  gcloud functions logs read triage-agent-event-driven --gen2 --region=us-central1 --limit=30"

#!/bin/bash

PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"

function deploy_step() {
    STEP=$1
    DIR="lab/$STEP"
    echo "Deploying $STEP..."
    
    cd $DIR/src
    gcloud run deploy simulator-$STEP --source . --platform managed --region $REGION --allow-unauthenticated --quiet
    URL=$(gcloud run services describe simulator-$STEP --format 'value(status.url)' --region $REGION)
    cd ../../..
    
    cd $DIR
    terraform init
    terraform apply -var="project_id=$PROJECT_ID" -auto-approve
    cd ../..
    
    echo "URL do Simulador: $URL"
    echo "Workflow pronto para testes no Console do GCP."
}

echo "Escolha a etapa da Aula 3 para Deploy:"
echo "1) Step 01 - Orquestração Básica"
echo "2) Step 02 - Retries"
echo "3) Step 03 - Idempotência"
echo "4) Step 04 - Dead-Letter Queue (Completo)"
read opt

case $opt in
    1) deploy_step "step-01-basic" ;;
    2) deploy_step "step-02-retries" ;;
    3) deploy_step "step-03-idempotency" ;;
    4) deploy_step "step-04-full" ;;
    *) echo "Inválido" ;;
esac

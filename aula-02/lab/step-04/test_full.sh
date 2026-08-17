#!/bin/bash

# STEP 4: TESTANDO TUDO

echo "--------------------------------------------------------"
echo "INICIANDO TESTE FINAL DA COREOGRAFIA"
echo "--------------------------------------------------------"

# 1. Limpar e Inicializar estoque
echo "[1/4] Inicializando produtos no Firestore..."
python3 init_firestore.py

# 2. Publicar Ordem
echo "[2/4] Publicando evento 'OrderCreated'..."
ORDER_ID=$RANDOM
gcloud pubsub topics publish orders --message="{\"order_id\": \"$ORDER_ID\", \"product_id\": \"prod-123\", \"quantity\": 1}"

echo "[3/4] Aguardando processamento (Fan-out + Chaining)..."
sleep 10

# 3. Verificar Resultados
echo "--------------------------------------------------------"
echo "VERIFICAÇÃO DE RESULTADOS"
echo "--------------------------------------------------------"

echo ">> LOGS DO INVENTORY (Baixando estoque):"
gcloud functions logs read inventory-service --gen2 --region=us-central1 --limit=3

echo ""
echo ">> LOGS DO PAYMENT (Gateway delay + Novo evento):"
gcloud functions logs read payment-service --gen2 --region=us-central1 --limit=3

echo ""
echo ">> LOGS DO SHIPPING (Reação ao pagamento):"
gcloud functions logs read shipping-service --gen2 --region=us-central1 --limit=3

echo "--------------------------------------------------------"
echo "FIM DO TESTE. Verifique os dados no Firestore (coleções 'products' e 'order_summaries')."

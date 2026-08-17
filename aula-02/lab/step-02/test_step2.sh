#!/bin/bash
echo "TESTE STEP 2: Fan-out (Inventário + Read Model)"

# 1. Init banco
python3 init_firestore.py

# 2. Enviar ordem
echo "Disparando 'OrderCreated' para testar Fan-out..."
gcloud pubsub topics publish orders --message='{"order_id": "STEP2-TEST", "product_id": "prod-123", "quantity": 1}'

echo "Aguarde 5 segundos..."
sleep 35

echo "Verifique no Firestore:"
echo "1. Coleção 'products' -> prod-123 deve ter estoque 9."
echo "2. Coleção 'order_summaries' -> deve existir o documento STEP2-TEST."

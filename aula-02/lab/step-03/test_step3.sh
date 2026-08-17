#!/bin/bash
echo "TESTE STEP 3: Coreografia Completa"

echo "Disparando fluxo: Order -> Payment -> Shipping..."
gcloud pubsub topics publish orders --message='{"order_id": "CHOREO-TEST", "product_id": "prod-456", "quantity": 1}'

echo "Aguardando o encadeamento (10s)..."
sleep 10

echo "Verifique no Firestore (order_summaries -> CHOREO-TEST):"
echo "O status deve ser SHIPPING_INITIATED, confirmando que o Pagamento disparou a Logistica!"

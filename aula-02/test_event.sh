#!/bin/bash

# Enviar uma mensagem de teste para o tópico 'orders'
echo "Enviando mensagem de teste para o tópico 'orders'..."

ORDER_ID=$RANDOM
TOTAL=$(( ( RANDOM % 1000 )  + 1 )).90

gcloud pubsub topics publish orders --message="{\"order_id\": \"$ORDER_ID\", \"customer_id\": \"77\", \"total\": $TOTAL}"

echo "Aguarde alguns segundos e verifique os logs da função."

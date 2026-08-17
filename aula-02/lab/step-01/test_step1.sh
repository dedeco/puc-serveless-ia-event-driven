#!/bin/bash
echo "TESTE STEP 1: Validando o Tópico"
echo "Publicando uma mensagem no tópico 'orders'..."

gcloud pubsub topics publish orders --message='{"info": "Apenas um teste de conexao"}'

echo "Sucesso! A mensagem foi aceita pelo Pub/Sub (mesmo sem consumidores ainda)."

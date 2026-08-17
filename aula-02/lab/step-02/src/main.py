import functions_framework
import base64
import json
import os
import time
from google.cloud import firestore
from google.cloud import pubsub_v1

# Clients
db = firestore.Client()
publisher = pubsub_v1.PublisherClient()
PROJECT_ID = os.environ.get("GCP_PROJECT")

@functions_framework.cloud_event
def inventory_service(cloud_event):
    """
    INVENTORY SERVICE: Reage a 'OrderCreated'.
    Bloqueia o estoque do produto.
    """
    if "message" in cloud_event.data and "data" in cloud_event.data["message"]:
        message_data = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
        data = json.loads(message_data)
        product_id = data.get("product_id")
        quantity = data.get("quantity")

        print(f"INVENTORY: Processando estoque para {product_id}...")
        
        doc_ref = db.collection("products").document(product_id)
        
        # Operação Atômica no Firestore
        doc_ref.update({
            "stock": firestore.Increment(-quantity),
            "last_order_id": data.get("order_id")
        })
        
        print(f"INVENTORY: Estoque de {product_id} reduzido em {quantity}.")

@functions_framework.cloud_event
def payment_service(cloud_event):
    """
    PAYMENT SERVICE: Reage a 'OrderCreated'.
    Simula gateway e publica 'PaymentConfirmed'.
    """
    if "message" in cloud_event.data and "data" in cloud_event.data["message"]:
        message_data = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
        data = json.loads(message_data)
        order_id = data.get("order_id")

        print(f"PAYMENT: Aguardando resposta do Gateway para Pedido {order_id}...")
        time.sleep(30) # Simula latência do gateway
        
        # Publica evento de sucesso
        topic_path = publisher.topic_path(PROJECT_ID, "payments")
        payment_event = {
            "order_id": order_id,
            "status": "confirmed",
            "timestamp": time.time()
        }
        publisher.publish(topic_path, json.dumps(payment_event).encode("utf-8"))
        
        print(f"PAYMENT: Pagamento do Pedido {order_id} CONFIRMADO. Evento publicado.")

@functions_framework.cloud_event
def shipping_service(cloud_event):
    """
    SHIPPING SERVICE: Reage a 'PaymentConfirmed' (tópico payments).
    Inicia a logística.
    """
    if "message" in cloud_event.data and "data" in cloud_event.data["message"]:
        message_data = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
        data = json.loads(message_data)
        order_id = data.get("order_id")

        print(f"SHIPPING: Pagamento recebido! Iniciando logística para o Pedido {order_id}...")
        
        # Atualiza status no banco para visualização
        db.collection("order_summaries").document(str(order_id)).update({
            "status": "SHIPPING_INITIATED",
            "shipping_time": firestore.SERVER_TIMESTAMP
        })
        
        print(f"SHIPPING: Pedido {order_id} enviado para transportadora.")

@functions_framework.cloud_event
def read_model_simulator(cloud_event):
    """
    DASHBOARD/READ MODEL: Mantém a visão consolidada para o aluno ver no Firestore.
    """
    if "message" in cloud_event.data and "data" in cloud_event.data["message"]:
        message_data = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
        data = json.loads(message_data)
        order_id = data.get("order_id")
        
        doc_ref = db.collection("order_summaries").document(str(order_id))
        
        # Se for evento de ordem, cria. Se for de pagamento, atualiza.
        # Aqui simplificamos usando merge=True
        doc_ref.set({
            "order_id": order_id,
            "updated_at": firestore.SERVER_TIMESTAMP,
            "raw_payload": data
        }, merge=True)

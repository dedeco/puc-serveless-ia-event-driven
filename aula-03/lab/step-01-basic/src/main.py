import os
from flask import Flask, request, jsonify
from google.cloud import firestore

app = Flask(__name__)
db = firestore.Client()

@app.route('/reserve', methods=['POST'])
def reserve():
    data = request.get_json() or {}
    order_id = data.get('order_id', 'unknown')
    product_id = "prod-123" # Padrão da aula
    
    # Atualiza Firestore para efeito visual na aula
    db.collection("order_summaries").document(str(order_id)).set({
        "order_id": order_id,
        "status": "RESERVING_STOCK",
        "updated_at": firestore.SERVER_TIMESTAMP
    }, merge=True)
    
    print(f"STEP-01: Reservando {order_id}")
    return jsonify({"status": "reserved"}), 200

@app.route('/charge', methods=['POST'])
def charge():
    data = request.get_json() or {}
    order_id = data.get('order_id', 'unknown')
    
    db.collection("order_summaries").document(str(order_id)).update({
        "status": "PAYMENT_PROCESSED",
        "updated_at": firestore.SERVER_TIMESTAMP
    })
    
    print(f"STEP-01: Cobrando {order_id}")
    return jsonify({"status": "charged"}), 200

@app.route('/ship', methods=['POST'])
def ship():
    data = request.get_json() or {}
    order_id = data.get('order_id', 'unknown')
    
    db.collection("order_summaries").document(str(order_id)).update({
        "status": "SHIPPING_INITIATED",
        "updated_at": firestore.SERVER_TIMESTAMP
    })
    
    print(f"STEP-01: Enviando {order_id}")
    return jsonify({"status": "shipped"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

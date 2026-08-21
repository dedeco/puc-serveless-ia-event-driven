import os
import random
from flask import Flask, request, jsonify
from google.cloud import firestore

app = Flask(__name__)
db = firestore.Client()

@app.route('/reserve', methods=['POST'])
def reserve():
    data = request.get_json() or {}
    order_id = data.get('order_id', 'unknown')
    db.collection("order_summaries").document(str(order_id)).set({
        "order_id": order_id,
        "status": "STOCK_RESERVED",
        "updated_at": firestore.SERVER_TIMESTAMP
    }, merge=True)
    return jsonify({"status": "reserved"}), 200

@app.route('/charge', methods=['POST'])
def charge():
    data = request.get_json() or {}
    order_id = data.get('order_id', 'unknown')
    
    # Simula instabilidade: falha 50% das vezes
    if random.random() < 0.5:
        print("STEP-02: Falha temporária no pagamento!")
        db.collection("order_summaries").document(str(order_id)).update({
            "status": "PAYMENT_RETRYING",
            "last_error": "Service Unavailable",
            "updated_at": firestore.SERVER_TIMESTAMP
        })
        return jsonify({"error": "Service Unavailable"}), 503
    
    print("STEP-02: Cobrança efetuada!")
    db.collection("order_summaries").document(str(order_id)).update({
        "status": "PAYMENT_PROCESSED",
        "updated_at": firestore.SERVER_TIMESTAMP
    })
    return jsonify({"status": "charged"}), 200

@app.route('/ship', methods=['POST'])
def ship():
    data = request.get_json() or {}
    order_id = data.get('order_id', 'unknown')
    db.collection("order_summaries").document(str(order_id)).update({
        "status": "SHIPPING_INITIATED",
        "updated_at": firestore.SERVER_TIMESTAMP
    })
    return jsonify({"status": "shipped"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

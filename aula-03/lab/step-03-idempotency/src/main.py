import os
from flask import Flask, request, jsonify
from google.cloud import firestore

app = Flask(__name__)
db = firestore.Client()
keys = set()

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
    key = request.headers.get('Idempotency-Key')
    data = request.get_json() or {}
    order_id = data.get('order_id', 'unknown')
    
    if key in keys:
        print(f"STEP-03: Chave {key} já processada!")
        db.collection("order_summaries").document(str(order_id)).update({
            "status": "PAYMENT_ALREADY_DONE",
            "idempotent_key": key,
            "updated_at": firestore.SERVER_TIMESTAMP
        })
        return jsonify({"status": "already_charged"}), 200
    
    keys.add(key)
    print(f"STEP-03: Primeira cobrança para {key}!")
    db.collection("order_summaries").document(str(order_id)).update({
        "status": "PAYMENT_PROCESSED",
        "idempotent_key": key,
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

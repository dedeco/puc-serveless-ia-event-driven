import os
from google.cloud import firestore

# Initialize Firestore Client with explicit project ID
db = firestore.Client(project="andresousa-puc")

def init_products():
    print("Inicializando Firestore com produtos de teste no projeto andresousa-puc...")
    
    products = [
        {"id": "prod-123", "name": "Notebook Gamer", "stock": 10},
        {"id": "prod-456", "name": "Monitor 4K", "stock": 5},
        {"id": "prod-789", "name": "Teclado Mecânico", "stock": 20}
    ]
    
    for p in products:
        doc_ref = db.collection("products").document(p["id"])
        doc_ref.set(p)
        print(f"Produto {p['name']} inicializado com estoque {p['stock']}.")

if __name__ == "__main__":
    init_products()

import functions_framework
from flask import Flask, request, jsonify

app = Flask(__name__)

def calculate_logic(data):
    if not data:
        return {"error": "Nenhum dado fornecido"}, 400
    
    operation = data.get('operation')
    a = data.get('a')
    b = data.get('b')
    
    if operation not in ['add', 'subtract', 'multiply', 'divide']:
        return {"error": "Operação inválida"}, 400
    
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return {"error": "Os valores 'a' e 'b' devem ser números"}, 400
    
    result = None
    if operation == 'add':
        result = a + b
    elif operation == 'subtract':
        result = a - b
    elif operation == 'multiply':
        result = a * b
    elif operation == 'divide':
        if b == 0:
            return {"error": "Divisão por zero"}, 400
        result = a / b
        
    return {
        "operation": operation,
        "a": a,
        "b": b,
        "result": result
    }, 200

@app.route('/calculate', methods=['POST'])
def flask_calculate():
    res, status = calculate_logic(request.get_json())
    return jsonify(res), status

@functions_framework.http
def calculate(request):
    """EntryPoint para o Google Cloud Functions"""
    if request.method == 'OPTIONS':
        # Permite requisições CORS
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    # Define headers para CORS em requisições reais
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    if request.method != 'POST':
        return (jsonify({"error": "Apenas POST é suportado"}), 405, headers)

    res, status = calculate_logic(request.get_json())
    return (jsonify(res), status, headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

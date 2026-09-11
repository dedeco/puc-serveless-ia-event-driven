import functions_framework
import json
import os
import vertexai
from vertexai.generative_models import (
    FunctionDeclaration,
    Tool,
    GenerativeModel
)

# Inicialização do Vertex AI
PROJECT_ID = os.environ.get("GCP_PROJECT")
REGION = os.environ.get("GCP_REGION", "us-central1")

if PROJECT_ID:
    vertexai.init(project=PROJECT_ID, location=REGION)

# Declaração da ferramenta usando o schema padrão do Vertex AI
get_build_logs_declaration = FunctionDeclaration(
    name="get_build_logs",
    description="Retorna os logs de um build que falhou no Cloud Build, a partir do build ID. Use para diagnosticar falhas de pipeline.",
    parameters={
        "type": "object",
        "properties": {
            "build_id": {
                "type": "string",
                "description": "O identificador exclusivo do build que falhou (ex: build-123)."
            }
        },
        "required": ["build_id"]
    }
)

# Agrupando a declaração no objeto Tool
devops_tools = Tool(
    function_declarations=[get_build_logs_declaration]
)

@functions_framework.http
def triage_agent(request):
    """
    HTTP Cloud Function que demonstra a capacidade de Function Calling do Gemini.
    O modelo decide se deve chamar a ferramenta 'get_build_logs' com base no prompt.
    """
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "3600"
        }
        return ("", 204, headers)

    headers = {"Access-Control-Allow-Origin": "*"}

    try:
        request_json = request.get_json(silent=True)
        if not request_json or "prompt" not in request_json:
            return (json.dumps({"error": "O campo 'prompt' e obrigatorio no JSON."}), 400, headers)

        prompt = request_json["prompt"]
        print(f"Recebido prompt para triagem: {prompt}")

        # Inicializa o modelo com as ferramentas declaradas
        model = GenerativeModel(
            model_name="gemini-2.5-flash",
            tools=[devops_tools]
        )

        response = model.generate_content(prompt)

        # Verifica se o modelo decidiu chamar uma função (Function Call)
        function_calls = response.candidates[0].function_calls

        if function_calls:
            call = function_calls[0]
            print(f"O modelo decidiu chamar a função: {call.name} com argumentos: {dict(call.args)}")
            
            return (json.dumps({
                "prompt": prompt,
                "function_calling_detected": True,
                "function_call": {
                    "name": call.name,
                    "args": dict(call.args)
                },
                "message": "Sucesso! O modelo detectou a ferramenta correta e extraiu os parametros necessarios."
            }, ensure_ascii=False), 200, headers)
        else:
            print("O modelo não solicitou nenhuma chamada de função.")
            return (json.dumps({
                "prompt": prompt,
                "function_calling_detected": False,
                "response_text": response.text,
                "message": "O modelo respondeu com texto normal porque o prompt não ativou a necessidade da ferramenta."
            }, ensure_ascii=False), 200, headers)

    except Exception as e:
        print(f"Erro ao processar a requisição: {str(e)}")
        return (json.dumps({"error": str(e)}), 500, headers)

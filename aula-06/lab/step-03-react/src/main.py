import functions_framework
import json
import os
import vertexai
from vertexai.generative_models import (
    FunctionDeclaration,
    Tool,
    GenerativeModel,
    Part
)

# Inicialização do Vertex AI
PROJECT_ID = os.environ.get("GCP_PROJECT")
REGION = os.environ.get("GCP_REGION", "us-central1")

if PROJECT_ID:
    vertexai.init(project=PROJECT_ID, location=REGION)

# 1. Declaração das Ferramentas
get_build_logs_declaration = FunctionDeclaration(
    name="get_build_logs",
    description="Retorna os logs de erro de um build específico do Cloud Build. Use esta ferramenta para investigar as causas de falha.",
    parameters={
        "type": "object",
        "properties": {
            "build_id": {
                "type": "string",
                "description": "ID exclusivo do build que falhou."
            }
        },
        "required": ["build_id"]
    }
)

trigger_pipeline_retry_declaration = FunctionDeclaration(
    name="trigger_pipeline_retry",
    description="Dispara uma reexecução (retry) automática do pipeline para o build fornecido. Use APENAS se o erro for transitório (ex: timeout, falha de conexão).",
    parameters={
        "type": "object",
        "properties": {
            "build_id": {
                "type": "string",
                "description": "ID exclusivo do build que deve ser reexecutado."
            }
        },
        "required": ["build_id"]
    }
)

# Agrupando as ferramentas
devops_tools = Tool(
    function_declarations=[
        get_build_logs_declaration,
        trigger_pipeline_retry_declaration
    ]
)

# 2. Funções Locais (Ações executadas pelo nosso código)
def local_get_build_logs(build_id: str) -> str:
    print(f"[AÇÃO LOCAL] Buscando logs para o build {build_id}...")
    if build_id == "build-101":
        return "ERROR: Connection timeout to database at 10.0.1.5. Retrying failed after 3 attempts."
    elif build_id == "build-202":
        return "ERROR: SyntaxError: invalid syntax in main.py, line 42. x = 10 y = 20"
    else:
        return f"ERROR: Unknown error in build {build_id}. Logs show general compilation crash."

def local_trigger_pipeline_retry(build_id: str) -> str:
    print(f"[AÇÃO LOCAL] Disparando reexecução do pipeline para o build {build_id}...")
    return f"SUCCESS: Nova execução de pipeline criada para o build {build_id} (ID da nova execução: run-{build_id}-retry)."

@functions_framework.http
def triage_agent(request):
    """
    HTTP Cloud Function que executa o Loop ReAct completo.
    O modelo decide as ações, nossa função executa-as e devolve os resultados,
    e o modelo conclui se o pipeline deve ser reexecutado ou escalado.
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
        print(f"Iniciando triagem ReAct para o prompt: {prompt}")

        # Instruções de sistema para direcionar o comportamento do agente
        system_instruction = (
            "Você é um engenheiro de DevOps inteligente especialista em triagem de builds que falharam. "
            "Seu fluxo de trabalho para investigar uma falha é: "
            "1. Sempre busque os logs do build usando 'get_build_logs'. "
            "2. Analise os logs recebidos: "
            "   - Se for um erro transitório de infraestrutura (ex: timeout de banco, falha de rede), chame 'trigger_pipeline_retry' e informe ao usuário. "
            "   - Se for um erro de código de programação ou sintaxe (ex: SyntaxError, NameError), NÃO tente reexecutar. Explique amigavelmente o erro de código e alerte que requer correção humana. "
            "3. Conclua com uma explicação clara de seu diagnóstico e da ação tomada."
        )

        model = GenerativeModel(
            model_name="gemini-2.5-flash",
            tools=[devops_tools],
            system_instruction=system_instruction
        )

        # Usamos uma sessão de chat para manter o histórico do diálogo e os retornos de funções
        chat = model.start_chat()
        
        # Envia o prompt inicial do usuário
        response = chat.send_message(prompt)
        
        execution_steps = []
        max_loops = 5  # Proteção contra loops infinitos
        loop_count = 0

        # Loop de orquestração do Agente (Reasoning + Acting + Observing)
        while response.candidates[0].function_calls and loop_count < max_loops:
            loop_count += 1
            function_calls = response.candidates[0].function_calls
            call = function_calls[0]
            
            name = call.name
            args = dict(call.args)
            print(f"[REPOSITÓRIO DE DECISÕES] O Gemini solicitou chamar a função '{name}' com argumentos '{args}'")

            # Executa a ação local apropriada
            if name == "get_build_logs":
                result = local_get_build_logs(args.get("build_id"))
            elif name == "trigger_pipeline_retry":
                result = local_trigger_pipeline_retry(args.get("build_id"))
            else:
                result = f"Erro: Ferramenta {name} desconhecida."

            step_info = {
                "step": loop_count,
                "tool_called": name,
                "arguments": args,
                "observation": result
            }
            execution_steps.append(step_info)

            # Envia a resposta da execução da ferramenta (Observation) de volta para o Gemini
            response = chat.send_message(
                Part.from_function_response(
                    name=name,
                    response={"result": result}
                )
            )

        print("Loop ReAct finalizado. Modelo gerou a conclusão final.")
        
        return (json.dumps({
            "prompt": prompt,
            "conclusion": response.text,
            "execution_steps": execution_steps,
            "total_steps": len(execution_steps)
        }, ensure_ascii=False), 200, headers)

    except Exception as e:
        print(f"Erro ao processar a requisição ReAct: {str(e)}")
        return (json.dumps({"error": str(e)}), 500, headers)

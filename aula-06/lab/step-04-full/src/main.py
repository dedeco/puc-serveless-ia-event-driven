import functions_framework
import base64
import json
import os
import vertexai
from google.cloud import firestore
from vertexai.generative_models import (
    FunctionDeclaration,
    Tool,
    GenerativeModel,
    Part
)

# Inicialização do Firestore e Vertex AI
db = firestore.Client()
PROJECT_ID = os.environ.get("GCP_PROJECT")
REGION = os.environ.get("GCP_REGION", "us-central1")

if PROJECT_ID:
    vertexai.init(project=PROJECT_ID, location=REGION)

# Declaração das Ferramentas
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

devops_tools = Tool(
    function_declarations=[
        get_build_logs_declaration,
        trigger_pipeline_retry_declaration
    ]
)

# Funções Locais Mockadas
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

@functions_framework.cloud_event
def triage_agent_event_driven(cloud_event):
    """
    Agente de Triagem completo acionado por eventos do Pub/Sub.
    Decodifica o evento de falha, roda o loop ReAct e persiste
    o diagnóstico resultante de forma estruturada no Firestore.
    """
    # 1. Recupera os dados do Pub/Sub
    pubsub_message = cloud_event.data.get("message", {})
    if not pubsub_message or "data" not in pubsub_message:
        print("Erro: Payload do Pub/Sub inválido ou vazio.")
        return

    # Decodifica a string base64 do Pub/Sub
    try:
        data_str = base64.b64decode(pubsub_message["data"]).decode("utf-8")
        event_data = json.loads(data_str)
    except Exception as e:
        print(f"Erro ao decodificar a mensagem do Pub/Sub: {str(e)}")
        return

    build_id = event_data.get("build_id")
    if not build_id:
        print("Erro: O campo 'build_id' não foi encontrado na mensagem do Pub/Sub.")
        return

    print(f"\n>>> INICIANDO TRIAGEM DO BUILD: {build_id} <<<")

    # Prompt dinâmico construído a partir do evento
    prompt = f"Por favor, trie o build com ID {build_id}. Busque os logs de erro e tome a acao correspondente."

    # Instruções de Sistema
    system_instruction = (
        "Você é um engenheiro de DevOps inteligente especialista em triagem de builds que falharam. "
        "Seu fluxo de trabalho para investigar uma falha é: "
        "1. Sempre busque os logs do build usando 'get_build_logs'. "
        "2. Analise os logs recebidos: "
        "   - Se for um erro transitório de infraestrutura (ex: timeout de banco, falha de rede), chame 'trigger_pipeline_retry' e informe ao usuário. "
        "   - Se for um erro de código de programação ou sintaxe (ex: SyntaxError, NameError), NÃO tente reexecutar. Explique amigavelmente o erro de código e alerte que requer correção humana. "
        "3. Conclua com uma explicação clara de seu diagnóstico e da ação tomada."
    )

    try:
        model = GenerativeModel(
            model_name="gemini-2.5-flash",
            tools=[devops_tools],
            system_instruction=system_instruction
        )

        chat = model.start_chat()
        response = chat.send_message(prompt)
        
        execution_steps = []
        max_loops = 5
        loop_count = 0

        # Loop ReAct
        while response.candidates[0].function_calls and loop_count < max_loops:
            loop_count += 1
            call = response.candidates[0].function_calls[0]
            name = call.name
            args = dict(call.args)

            print(f"[REPOSITÓRIO DE DECISÕES] Gemini solicitou: '{name}' com '{args}'")

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

            # Devolve observação para o modelo
            response = chat.send_message(
                Part.from_function_response(
                    name=name,
                    response={"result": result}
                )
            )

        conclusion = response.text
        print(f"\nConclusão do Agente:\n{conclusion}\n")

        # 2. Persistência dos resultados no Firestore (CQRS / Read Model)
        print(f"Gravando diagnóstico no Firestore na coleção 'build_triages' para o documento '{build_id}'...")
        doc_ref = db.collection("build_triages").document(build_id)
        doc_ref.set({
            "build_id": build_id,
            "conclusion": conclusion,
            "execution_steps": execution_steps,
            "total_steps": len(execution_steps),
            "status": "TRIAGED",
            "updated_at": firestore.SERVER_TIMESTAMP
        })
        print(f"Sucesso! Diagnóstico do build {build_id} persistido.")

    except Exception as e:
        print(f"Erro grave durante a execução do agente de triagem: {str(e)}")

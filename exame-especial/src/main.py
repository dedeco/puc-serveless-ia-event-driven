import base64
import json
import os
import functions_framework
import vertexai
from google.cloud import firestore
from vertexai.generative_models import (
    FunctionDeclaration,
    GenerativeModel,
    Part,
    Tool,
)

# Inicialização global (fora do handler para reaproveitamento em Warm Starts)
PROJECT_ID = os.environ.get("GCP_PROJECT")
REGION = os.environ.get("GCP_REGION", "us-central1")

_db_client = None


def get_db():
    """Retorna cliente Firestore reutilizando a conexão entre invocações (Warm Start)."""
    global _db_client
    if _db_client is None:
        _db_client = firestore.Client()
    return _db_client


if PROJECT_ID:
    vertexai.init(project=PROJECT_ID, location=REGION)


# ============================================================================
# TODO (Etapa 4 - Observabilidade):
# Implemente logs estruturados em JSON para o Cloud Logging.
# Garanta que a função `log_structured` imprima um JSON válido em linha única
# contendo `severity`, `message`, `build_id` e quaisquer campos extras.
# ============================================================================
def log_structured(severity: str, message: str, build_id: str = None, **kwargs):
    payload = {
        "severity": severity,
        "message": message,
        "build_id": build_id,
        **kwargs,
    }
    print(json.dumps(payload, ensure_ascii=False))


# Declaração das Ferramentas
get_build_logs_declaration = FunctionDeclaration(
    name="get_build_logs",
    description="Retorna os logs de erro de um build específico do Cloud Build. Use esta ferramenta para investigar as causas de falha.",
    parameters={
        "type": "object",
        "properties": {
            "build_id": {
                "type": "string",
                "description": "ID exclusivo do build que falhou.",
            }
        },
        "required": ["build_id"],
    },
)

trigger_pipeline_retry_declaration = FunctionDeclaration(
    name="trigger_pipeline_retry",
    description="Dispara uma reexecução (retry) automática do pipeline para o build fornecido. Use APENAS se o erro for transitório (ex: timeout, falha de conexão).",
    parameters={
        "type": "object",
        "properties": {
            "build_id": {
                "type": "string",
                "description": "ID exclusivo do build que deve ser reexecutado.",
            }
        },
        "required": ["build_id"],
    },
)

# ============================================================================
# TODO (Etapa 2 - 15 pts): Declaração da Nova Ferramenta (`notify_oncall_team`)
# 1. Crie `notify_oncall_team_declaration = FunctionDeclaration(...)` com:
#    - name="notify_oncall_team"
#    - parâmetros: `build_id` (string), `severity` (string), `error_summary` (string)
#    - required: ["build_id", "severity", "error_summary"]
# 2. Adicione `notify_oncall_team_declaration` na lista de `devops_tools` abaixo.
# ============================================================================

devops_tools = Tool(
    function_declarations=[
        get_build_logs_declaration,
        trigger_pipeline_retry_declaration,
        # TODO (Etapa 2): Adicione notify_oncall_team_declaration aqui
    ]
)


# Funções Locais (Simuladores das Ferramentas)
def local_get_build_logs(build_id: str) -> str:
    log_structured("INFO", f"Buscando logs para o build {build_id}", build_id=build_id)
    if build_id == "build-101":
        return "ERROR: Connection timeout to database at 10.0.1.5. Retrying failed after 3 attempts."
    elif build_id == "build-202":
        return "ERROR: SyntaxError: invalid syntax in main.py, line 42. x = 10 y = 20"
    # TODO (Etapa 2): Adicione o cenário para `build-303` retornando um erro crítico
    # (ex: "CRITICAL: Database corruption or unauthorized secret access detected in production.")
    else:
        return f"ERROR: Unknown error in build {build_id}. Logs show general compilation crash."


def local_trigger_pipeline_retry(build_id: str) -> str:
    log_structured("INFO", f"Disparando reexecução do pipeline para o build {build_id}", build_id=build_id)
    return f"SUCCESS: Nova execução de pipeline criada para o build {build_id} (ID da nova execução: run-{build_id}-retry)."


# ============================================================================
# TODO (Etapa 2 - 10 pts): Implemente a função `local_notify_oncall_team`
# Assinatura sugerida:
# def local_notify_oncall_team(build_id: str, severity: str, error_summary: str) -> str:
#     ...
# (Dica: Você também pode ler a variável de ambiente ONCALL_WEBHOOK_SECRET injetada
# pelo Secret Manager na Etapa 3 para validar se o segredo está configurado!)
# ============================================================================


@functions_framework.cloud_event
def triage_agent_event_driven(cloud_event):
    """
    Agente de Triagem completo acionado por eventos do Pub/Sub.
    Verifica idempotência no Firestore, decodifica o evento de falha,
    roda o loop ReAct e persiste o diagnóstico resultante no Firestore.
    """
    pubsub_message = cloud_event.data.get("message", {})
    if not pubsub_message or "data" not in pubsub_message:
        log_structured("ERROR", "Payload do Pub/Sub inválido ou vazio.")
        return

    try:
        data_str = base64.b64decode(pubsub_message["data"]).decode("utf-8")
        event_data = json.loads(data_str)
    except Exception as e:
        log_structured("ERROR", f"Erro ao decodificar a mensagem do Pub/Sub: {str(e)}")
        return

    build_id = event_data.get("build_id")
    if not build_id:
        log_structured("ERROR", "O campo 'build_id' não foi encontrado na mensagem do Pub/Sub.")
        return

    db = get_db()
    doc_ref = db.collection("build_triages").document(build_id)

    # ========================================================================
    # TODO (Etapa 1 - 15 pts): Controle de Idempotência no Firestore
    # Consulte `doc_snapshot = doc_ref.get()`.
    # Se `doc_snapshot.exists` e `doc_snapshot.to_dict().get("status") == "TRIAGED"`,
    # emita um log estruturado de aviso/info ("Evento duplicado ignorado por idempotência")
    # e retorne `{"status": "IGNORED_IDEMPOTENT", "build_id": build_id}` sem chamar o Gemini!
    # ========================================================================

    log_structured("INFO", "Iniciando triagem do build", build_id=build_id)

    prompt = f"Por favor, trie o build com ID {build_id}. Busque os logs de erro e tome a acao correspondente."

    # TODO (Etapa 2): Atualize o system_instruction para orientar o modelo a chamar
    # `notify_oncall_team` quando encontrar um erro CRITICAL em produção (como no build-303).
    system_instruction = (
        "Você é um engenheiro de DevOps inteligente especialista em triagem de builds que falharam. "
        "Seu fluxo de trabalho para investigar uma falha é: "
        "1. Sempre busque os logs do build usando 'get_build_logs'. "
        "2. Analise os logs recebidos: "
        "   - Se for um erro transitório de infraestrutura (ex: timeout de banco, falha de rede), chame 'trigger_pipeline_retry' e informe ao usuário. "
        "   - Se for um erro crítico de produção/segurança/corrupção de dados (CRITICAL), chame 'notify_oncall_team' informando a severidade e o resumo. "
        "   - Se for um erro de código de programação ou sintaxe (ex: SyntaxError, NameError), NÃO tente reexecutar. Explique amigavelmente o erro de código e alerte que requer correção humana. "
        "3. Conclua com uma explicação clara de seu diagnóstico e da ação tomada."
    )

    try:
        model = GenerativeModel(
            model_name="gemini-2.5-flash",
            tools=[devops_tools],
            system_instruction=system_instruction,
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

            log_structured(
                "INFO",
                f"Gemini solicitou ferramenta '{name}'",
                build_id=build_id,
                step=loop_count,
                tool_called=name,
                arguments=args,
            )

            if name == "get_build_logs":
                result = local_get_build_logs(args.get("build_id"))
            elif name == "trigger_pipeline_retry":
                result = local_trigger_pipeline_retry(args.get("build_id"))
            # TODO (Etapa 2): Adicione o `elif name == "notify_oncall_team":`
            # chamando `local_notify_oncall_team(...)`
            else:
                result = f"Erro: Ferramenta {name} desconhecida."

            step_info = {
                "step": loop_count,
                "tool_called": name,
                "arguments": args,
                "observation": result,
            }
            execution_steps.append(step_info)

            response = chat.send_message(
                Part.from_function_response(name=name, response={"result": result})
            )

        conclusion = response.text
        log_structured("INFO", "Triagem concluída pelo agente", build_id=build_id, total_steps=len(execution_steps))

        doc_ref.set(
            {
                "build_id": build_id,
                "conclusion": conclusion,
                "execution_steps": execution_steps,
                "total_steps": len(execution_steps),
                "status": "TRIAGED",
                "updated_at": firestore.SERVER_TIMESTAMP,
            }
        )
        return {"status": "TRIAGED", "build_id": build_id}

    except Exception as e:
        log_structured("ERROR", f"Erro grave durante a execução do agente de triagem: {str(e)}", build_id=build_id)
        raise

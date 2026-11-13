# Exame Especial (Nova Oportunidade) — 100 Pontos

**Disciplina:** Serverless Computing e Arquiteturas Event-Driven  
**Curso:** Pós-Graduação em DevOps e Cloud Platform Engineering com IA (PUC Minas)  
**Professor:** André de Sousa Araújo  
**Prazo de Entrega:** Até 7 dias corridos a partir da publicação no Canvas  
**Valor Total:** 100 pontos  

---

## Objetivo da Atividade

Evoluir a **Plataforma Serverless de Triagem Inteligente de Incidentes DevOps** (vista na `aula-06/lab/step-04-full`), integrando os conceitos essenciais trabalhados nos 6 módulos da disciplina:
1. **Arquiteturas Event-Driven, Idempotência e Resiliência (DLQ)** (Aulas 01, 02 e 03)
2. **Agentes Autônomos com Vertex AI, Function Calling e Loop ReAct** (Aula 06)
3. **Segurança (IAM de Menor Privilégio + Secret Manager) e CI/CD com Cloud Build** (Aula 05)
4. **Observabilidade (Logs Estruturados) e Mitigação de Cold Start** (Aula 04)

---

## O Que Você Deve Implementar (4 Etapas)

Os arquivos desta pasta (`exame-especial/`) já contêm o código-base do `step-04-full` com marcações `# TODO` indicando exatamente onde atuar.

### Etapa 1 — Arquitetura Event-Driven, Idempotência e DLQ (30 pontos)
1. **Infraestrutura como Código (`main.tf`):**
   - Adicione um tópico Pub/Sub de **Dead-Letter Queue (DLQ)** chamado `build-failures-dlq`.
   - Crie uma assinatura (`google_pubsub_subscription`) com bloco `dead_letter_policy` (e `max_delivery_attempts = 5`) associada ao tópico `build-failures` apontando para a DLQ.
2. **Controle de Idempotência no Consumidor (`src/main.py`):**
   - Antes de iniciar o loop ReAct e invocar o modelo Gemini, consulte o **Firestore** (coleção `build_triages`, documento `build_id`).
   - Se o documento já existir e estiver com `status == "TRIAGED"`, emita um log estruturado informando que o evento duplicado foi ignorado por idempotência e retorne imediatamente sem chamar a Vertex AI.

### Etapa 2 — Evolução do Agente de IA com Function Calling (25 pontos)
1. **Nova Ferramenta (`src/main.py`):**
   - Além de `get_build_logs` e `trigger_pipeline_retry`, declare uma **3ª ferramenta** usando `FunctionDeclaration`: `notify_oncall_team`, recebendo `build_id` (`string`), `severity` (`string`) e `error_summary` (`string`).
   - Registre a nova declaração dentro de `devops_tools = Tool(function_declarations=[...])`.
   - Implemente a função local `local_notify_oncall_team(build_id: str, severity: str, error_summary: str) -> str` e conecte-a no despacho (`if/elif`) dentro do loop ReAct e no `system_instruction`.
2. **Novo Cenário de Teste (`src/main.py`):**
   - Em `local_get_build_logs`, adicione o cenário `build-303` simulando uma falha crítica de segurança ou banco corrompido (ex.: `"CRITICAL: Database corruption detected in production cluster"`), orientando o agente a acionar `notify_oncall_team` com severidade `"HIGH"` ou `"CRITICAL"`.

### Etapa 3 — Segurança (IAM + Secret Manager) e Pipeline CI/CD (25 pontos)
1. **Secret Manager e IAM de Menor Privilégio (`main.tf`):**
   - Adicione no `main.tf` o recurso do **Secret Manager** (`google_secret_manager_secret` para `oncall-webhook-secret`) e conceda a role `roles/secretmanager.secretAccessor` para a Service Account `triage-agent-event-sa`.
   - Configure a injeção desse segredo como variável de ambiente `ONCALL_WEBHOOK_SECRET` na Cloud Function Gen 2 (`secret_environment_variables` dentro de `service_config`).
2. **Testes Unitários (`test_main.py`) e Esteira (`cloudbuild.yaml`):**
   - Complete o arquivo `test_main.py` com testes unitários (`unittest`) validando:
     - O retorno das funções locais (`local_get_build_logs`, `local_trigger_pipeline_retry` e `local_notify_oncall_team`).
     - O comportamento de **idempotência** quando um `build_id` já consta como `"TRIAGED"` no Firestore (usando `unittest.mock`).
   - Complete o arquivo `cloudbuild.yaml` (baseado na `aula-05`) com 2 etapas: execução do `unittest` e comando de deploy/validação.

### Etapa 4 — Observabilidade, Cold Start e Relatório Técnico (20 pontos)
1. **Logs Estruturados (`src/main.py`):**
   - Utilize a função auxiliar `log_structured(severity, message, build_id=None, **kwargs)` para imprimir JSON estruturado em linha única (`json.dumps(...)`) nos pontos principais do agente.
2. **Otimização de Cold Start (`main.tf` e `src/main.py`):**
   - Ajuste o `service_config` no `main.tf` e documente no relatório `RELATORIO_EXAME.md` as práticas adotadas para reduzir o Cold Start e limitar custos.
3. **Preenchimento do `RELATORIO_EXAME.md`:**
   - Complete o arquivo `RELATORIO_EXAME.md` com o diagrama da arquitetura, explicações técnicas e a saída dos testes executados.

> **Nota importante sobre Conta GCP:** Caso seus créditos gratuitos da conta Google Cloud tenham expirado, você **não será penalizado(a)** se não puder rodar o `terraform apply` na nuvem. Nesse caso, garanta que:
> 1. `python3 -m unittest test_main.py -v` passe 100% localmente (com mocks);
> 2. `terraform fmt -check` e a sintaxe do `main.tf` estejam válidos;
> 3. O `RELATORIO_EXAME.md` esteja completo.

---

## Como Entregar no Canvas

Envie pela tarefa do Canvas **em até 7 dias corridos**:
- Um arquivo `.zip` contendo a pasta `exame-especial/` completa com todas as suas alterações **OU** o link para o seu repositório Git público contendo a resolução.

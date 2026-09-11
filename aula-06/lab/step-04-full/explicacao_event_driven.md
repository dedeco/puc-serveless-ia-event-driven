# Explicação do Funcionamento do Step 04: Agente DevOps Orientado a Eventos Completo

Este documento explica de forma abrangente o funcionamento do quarto e último laboratório (`step-04-full`), consolidando os conceitos de Arquitetura Orientada a Eventos (EDA), o loop ReAct do Gemini e a persistência de dados em banco de dados NoSQL (Firestore).

---

## 1. Visão Geral da Arquitetura
Este laboratório implementa uma arquitetura moderna e totalmente assíncrona para operações de DevOps (AIOps):

```
[Falha no Pipeline] 
       │
       ▼
[Tópico Pub/Sub: build-failures] ──(Mensagem de Evento)──> [Cloud Function: triage-agent-event-driven]
                                                                      │
                                                             (Loop ReAct c/ Gemini)
                                                                      │
                                                                      ├─> Executa Ferramentas
                                                                      ├─> Toma Decisão Autónoma
                                                                      ▼
                                                       [Salva no Firestore: build_triages]
```

1. **Desacoplamento por Mensagens (Pub/Sub):** Uma ferramenta externa (ex: Cloud Build ou GitHub Actions) publica um JSON simples no tópico `build-failures` quando um build quebra.
2. **Processamento Assíncrono (Cloud Function):** A Cloud Function `triage-agent-event-driven` é disparada automaticamente por evento de recebimento de mensagem no Pub/Sub, liberando a ferramenta que gerou a falha de esperar a triagem terminar.
3. **Persistência de Resultados (Firestore):** Todo o relatório final gerado pelo Gemini, incluindo os passos exatos que o agente executou e as observações feitas, é salvo estruturadamente em uma coleção NoSQL (`build_triages`) no Firestore.

---

## 2. Ajustes Técnicos e Resolução de Problemas Realizados

Durante a execução do laboratório, realizamos as seguintes otimizações:
* **Limpeza de Armazenamento do Cloud Shell:** O armazenamento persistente estava a **100% de uso**. Removemos os diretórios `.terraform` acumulados de aulas antigas e limpamos o cache de pacotes, liberando **1.4 GB de espaço** (uso caiu para 70%), o que viabilizou o download e a instalação dos provedores do Terraform.
* **Uso de Banco Existente:** Como o banco Firestore Native `(default)` já estava ativo no projeto GCP, comentamos a declaração do recurso no Terraform para evitar conflitos de duplicação.
* **Modelo Inteligente de Ponta:** Atualizamos a Cloud Function de `gemini-1.5-flash` para **`gemini-2.5-flash`**, garantindo maior rapidez e assertividade na tomada de decisão.

---

## 3. O Comportamento dos Agentes nos Testes

Ao rodarmos o script `./test_full.sh`, simulamos dois incidentes de pipeline distintos:

### Incidente A: Triagem do `build-101` (Falha Transitória de Infraestrutura)
* **Evento Pub/Sub recebido:** `{"build_id": "build-101"}`
* **Logs da Cloud Function:**
  1. A função é disparada e extrai `build_id: "build-101"`.
  2. **Raciocínio/Ação 1 (get_build_logs):** O Gemini decide buscar os logs e observa: `"ERROR: Connection timeout to database at 10.0.1.5..."`
  3. **Raciocínio/Ação 2 (trigger_pipeline_retry):** O Gemini diagnostica que é um erro de timeout (infraestrutura transitória). Ele decide reexecutar o pipeline automaticamente e observa: `"SUCCESS: Nova execução de pipeline criada..."`
  4. **Finalização:** Salva o documento `build-101` no Firestore com o status `TRIAGED`, contendo a conclusão explicativa e a lista de passos executados (`execution_steps`).

### Incidente B: Triagem do `build-202` (Erro de Código)
* **Evento Pub/Sub recebido:** `{"build_id": "build-202"}`
* **Logs da Cloud Function:**
  1. A função é disparada e extrai `build_id: "build-202"`.
  2. **Raciocínio/Ação 1 (get_build_logs):** O Gemini decide buscar os logs e observa: `"ERROR: SyntaxError: invalid syntax in main.py, line 42..."`
  3. **Raciocínio:** O Gemini identifica um erro de sintaxe do desenvolvedor. Ele conclui que disparar uma nova tentativa automática seria inútil e geraria custos à toa.
  4. **Finalização:** Salva o documento `build-202` no Firestore com o status `TRIAGED`, explicando detalhadamente a falha de sintaxe na linha 42 e alertando que o erro requer intervenção humana para ser consertado.

---

## 4. Persistência de Dados no Firestore (Read Model / CQRS)
Os diagnósticos estruturados salvos no Firestore facilitam a criação de dashboards de monitoramento para a equipe de Engenharia. Cada documento gravado na coleção `build_triages` possui a seguinte estrutura de dados:

```json
{
  "build_id": "build-101",
  "status": "TRIAGED",
  "conclusion": "O build 'build-101' falhou devido a um erro de tempo limite de conexão... Acionei uma reexecução automática...",
  "total_steps": 2,
  "execution_steps": [
    {
      "step": 1,
      "tool_called": "get_build_logs",
      "arguments": { "build_id": "build-101" },
      "observation": "ERROR: Connection timeout to database at 10.0.1.5. Retrying failed after 3 attempts."
    },
    {
      "step": 2,
      "tool_called": "trigger_pipeline_retry",
      "arguments": { "build_id": "build-101" },
      "observation": "SUCCESS: Nova execução de pipeline criada para o build build-101 (ID da nova execução: run-build-101-retry)."
    }
  ],
  "updated_at": "2026-09-11T00:11:22.964Z"
}
```

---

## 5. Principais Aprendizados do Curso
Com a conclusão deste Step 4, você consolidou os maiores pilares de Engenharia de Agentes com Generative AI no ecossistema de nuvem:
* **Function Calling:** Como ensinar o LLM a interagir com sistemas reais mapeando seus inputs para schemas estruturados.
* **Loop ReAct em Nuvem:** Como orquestrar raciocínio contínuo em Python para resolver incidentes em fluxos multi-etapas dinâmicos.
* **Orientação a Eventos:** Desacoplamento arquitetural assíncrono e resiliente.
* **CQRS e Persistência NoSQL:** Gravação de estados e relatórios prontos para visualização e auditoria em bancos escaláveis (Firestore).

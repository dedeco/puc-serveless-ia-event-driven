# Guia de Orquestradores: Qual ferramenta escolher?

Este documento serve como material de apoio para a **Aula 3 — Orquestração e Composição de Serviços**, ajudando a entender onde o **GCP Cloud Workflows** se encaixa no ecossistema de software moderno e quando utilizar outras alternativas.

---

## 1. Cloud Workflows vs. Celery (Apps vs. Infraestrutura)

A dúvida mais comum é: "Por que não usar o Celery (Python) para orquestrar?".

| Característica | Celery / Sidekiq | Cloud Workflows / Step Functions |
| :--- | :--- | :--- |
| **Natureza** | Fila de tarefas interna da aplicação. | Orquestrador de infraestrutura serverless. |
| **Linguagem** | Preso a uma stack (ex: Python). | Agnóstico (conecta qualquer API HTTP). |
| **Gerenciamento** | Exige Broker (Redis) e Workers. | Ops Zero (Totalmente gerenciado). |
| **Estado** | Volátil (perde-se se o broker falhar). | Persistente (sobrevive a falhas de serviços). |
| **Ideal para** | Tarefas pesadas e rápidas da app. | Compor microsserviços e APIs externas. |

---

## 2. Panorama do Ecossistema (Open Source e Outras Nuvens)

### **n8n (O "Zapier" dos Devs)**
- **Perfil**: Low-code e visual.
- **Uso Ideal**: Automação de processos de negócio que conectam várias ferramentas SaaS (Slack + Trello + Google Sheets).
- **Vantagem**: Centenas de conectores prontos para uso imediato.

### **Apache Airflow (O Rei dos Dados)**
- **Perfil**: DAGs definidos em Python.
- **Uso Ideal**: Pipelines de dados complexos (ETL/ELT). Mover dados do ponto A para o ponto B com transformações pesadas.
- **Vantagem**: Ecossistema gigante para Big Data (Spark, Hive, BigQuery).

### **Temporal.io (Workflow as Code)**
- **Perfil**: Escrito via SDK (Go, Java, Python).
- **Uso Ideal**: Lógica de negócio ultra-crítica, sistemas financeiros e transações de longa duração (meses).
- **Vantagem**: Lida nativamente com o padrão **Saga** (compensação de erros).

### **Argo Workflows (Nativo do Kubernetes)**
- **Perfil**: Baseado em YAML e Pods.
- **Uso Ideal**: Pipelines que rodam dentro do Kubernetes, como CI/CD ou treinamento de modelos de IA.
- **Vantagem**: Escala horizontalmente dentro do seu próprio cluster.

---

## 3. Resumo Decisório: "Qual eu uso?"

| Se o seu objetivo é... | Use esta ferramenta: |
| :--- | :--- |
| Orquestrar microsserviços no GCP sem gerenciar servidores | **Cloud Workflows** |
| Conectar ferramentas de marketing/vendas visualmente | **n8n** |
| Processar trilhões de linhas de dados para o Data Lake | **Airflow** |
| Executar tarefas assíncronas simples dentro do Django/Flask | **Celery** |
| Construir uma máquina de estado financeira complexa e durável | **Temporal** |
| Rodar pipelines complexos dentro de um Cluster Kubernetes | **Argo** |

---

## 4. Por que focamos em Cloud Workflows nesta aula?

Focamos no Cloud Workflows porque ele permite aprender os **fundamentos da orquestração distribuída**:
1. **Idempotência**: Como garantir que repetir um passo é seguro.
2. **Retries**: Como lidar com APIs que falham temporariamente.
3. **Dead-Letter Queues**: O que fazer quando tudo falha.
4. **Serverless**: Focar na arquitetura, não na manutenção do servidor de orquestração.

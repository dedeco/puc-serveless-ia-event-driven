# Serverless Computing e Arquiteturas Event-Driven
## Pos-Graduacao: DevOps e Cloud Platform Engineering com IA
### Prof. Andre de Sousa Araujo | PUC Minas

Repositorio oficial da disciplina de Serverless Computing e Arquiteturas Event-Driven. Este material foca na construcao de sistemas escalaveis utilizando Google Cloud Platform, infraestrutura como codigo com Terraform e integracao de arquiteturas orientadas a eventos com agentes de Inteligencia Artificial.

Descricao: Repositorio com os materiais praticos, checkpoints e o projeto integrador da disciplina. Inclui infraestrutura como codigo (Terraform), pipelines de eventos no GCP e integracao pratica com Vertex AI.

Tags: serverless, gcp, event-driven-architecture, terraform, python, vertex-ai, puc-minas, devops, cloud-native.

---

## Estrutura da Disciplina

O curso e estruturado de forma incremental. Cada aula evolui o projeto anterior, adicionando novas capacidades de arquitetura, observabilidade, seguranca e IA.

### Aula 1: Fundamentos de Serverless (./aula-01)
- Foco: Evolucao da infraestrutura (Bare Metal -> VM -> Container -> Serverless).
- Checkpoint 1: Deploy de funcao HTTP simples (Cloud Run functions).

### Aula 2: Arquiteturas Event-Driven (./aula-02)
- Foco: Pub/Sub, Eventarc e padroes Publish/Subscribe.
- Checkpoint 2: Transicao de gatilho HTTP para eventos Pub/Sub.

### Aula 3: Orquestracao e Composicao (./aula-03)
- Foco: Cloud Workflows, Orquestracao vs. Coreografia, Idempotencia.
- Checkpoint 3: Criacao de pipelines de dados orquestrados.

### Aula 4: Observabilidade e Performance (./aula-04)
- Foco: Cloud Logging, Monitoring e Trace. Otimizacao de Cold Starts.
- Checkpoint 4: Instrumentacao e analise de metricas do pipeline.

### Aula 5: Seguranca e CI/CD (./aula-05)
- Foco: IAM, Secret Manager, Cloud Build e Cloud Deploy.
- Checkpoint 5: Configuracao de pipeline de CI/CD automatizado.

### Aula 6: Serverless e IA - Projeto Final (./aula-06)
- Foco: Integracao com Vertex AI e Agentes Autonomos.
- Projeto Final: Arquitetura completa e integrada com IA.

---

## Pre-requisitos
- Conta no Google Cloud Platform com faturamento ativo.
- Google Cloud SDK (gcloud CLI) instalado.
- Python 3.10+
- Terraform 1.5+

## Atividade Extra (Opcional)
- Containerizacao com Docker e deploy no Google Kubernetes Engine (GKE) como contraponto ao modelo Serverless.

---
(c) 2026 PUC Minas - Educacao Continuada

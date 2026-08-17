# Serverless Computing e Arquiteturas Event-Driven
## Pos-Graduacao: DevOps e Cloud Platform Engineering com IA
### Prof. Andre de Sousa Araujo | PUC Minas

Este repositorio contem o material pratico e os checkpoints da disciplina de Serverless Computing e Arquiteturas Event-Driven. O objetivo e capacitar o aluno a projetar, implementar e operar arquiteturas escalaveis no Google Cloud Platform (GCP).

## Descricao do Curso
A disciplina aborda a evolucao dos modelos de infraestrutura, desde servidores fisicos ate FaaS (Function as a Service), explorando padroes de mensageria, orquestracao de workflows e a integracao de agentes de IA em arquiteturas orientadas a eventos.

## Estrutura de Checkpoints
O projeto e construido de forma incremental. Cada pasta representa uma evolucao do sistema:

- Aula 1: Fundamentos de Serverless e deploy de funcoes HTTP.
- Aula 2: Introducao a Arquiteturas Event-Driven com Pub/Sub e Eventarc.
- Aula 3: Orquestracao de processos complexos com Cloud Workflows.
- Aula 4: Observabilidade, tracing e otimizacao de performance (Cold Start).
- Aula 5: Seguranca, IAM e automacao de deploy com pipelines de CI/CD.
- Aula 6: Projeto Final - Integracao com Vertex AI e Agentes Autonomos.

## Instrucoes para Alunos

### 1. Clonando o Repositorio
Execute o comando abaixo para copiar os materiais:
git clone https://github.com/dedeco/puc-serveless-ia-event-driven.git

### 2. Configuracao do Terraform
Os laboratorios utilizam Terraform para provisionamento. Para evitar conflitos de estado entre alunos, cada um deve configurar seu proprio backend remoto:

- Crie um bucket no seu Cloud Storage para armazenar o estado.
- Em cada pasta de aula, edite o bloco 'backend "gcs"' no arquivo main.tf com o nome do seu bucket.

### 3. Pre-requisitos Tecnicos
- Google Cloud SDK (gcloud CLI) devidamente autenticado.
- Terraform instalado (versao 1.5 ou superior).
- Python 3.10 ou superior para o desenvolvimento das funcoes.

## Contribuicao e Duvidas
Utilize a aba 'Issues' deste repositorio para reportar bugs ou tirar duvidas tecnicas sobre os laboratorios.

---
(c) 2026 PUC Minas - Educacao Continuada

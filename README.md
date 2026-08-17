# Serverless Computing e Arquiteturas Event-Driven
## Pós-Graduação: DevOps e Cloud Platform Engineering com IA
### Prof. André de Sousa Araújo | PUC Minas

Repositório oficial da disciplina de Serverless Computing e Arquiteturas Event-Driven. Este material foca na construção de sistemas escaláveis utilizando Google Cloud Platform, infraestrutura como código com Terraform e integração de arquiteturas orientadas a eventos com agentes de Inteligência Artificial.

## Descrição do Curso
A disciplina aborda a evolução dos modelos de infraestrutura, desde servidores físicos até FaaS (Function as a Service), explorando padrões de mensageria, orquestração de workflows e a integração de agentes de IA em arquiteturas orientadas a eventos.

## Estrutura de Checkpoints
O projeto é construído de forma incremental. Cada pasta representa uma evolução do sistema:

- Aula 1: Fundamentos de Serverless e deploy de funções HTTP.
- Aula 2: Introdução a Arquiteturas Event-Driven com Pub/Sub e Eventarc.
- Aula 3: Orquestração de processos complexos com Cloud Workflows.
- Aula 4: Observabilidade, tracing e otimização de performance (Cold Start).
- Aula 5: Segurança, IAM e automação de deploy com pipelines de CI/CD.
- Aula 6: Projeto Final - Integração com Vertex AI e Agentes Autônomos.

## Instruções para Alunos

### 1. Clonando o Repositório
Execute o comando abaixo para copiar os materiais:
git clone https://github.com/dedeco/puc-serveless-ia-event-driven.git

### 2. Configuração do Terraform
Os laboratórios utilizam Terraform para provisionamento. Para evitar conflitos de estado entre alunos, cada um deve configurar seu próprio backend remoto:

- Crie um bucket no seu Cloud Storage para armazenar o estado.
- Em cada pasta de aula, edite o bloco 'backend "gcs"' no arquivo main.tf com o nome do seu bucket.

### 3. Pré-requisitos Técnicos
- Google Cloud SDK (gcloud CLI) devidamente autenticado.
- Terraform instalado (versão 1.5 ou superior).
- Python 3.10 ou superior para o desenvolvimento das funções.

## Contribuição e Dúvidas
Utilize a aba 'Issues' deste repositório para reportar bugs ou tirar dúvidas técnicas sobre os laboratórios.

---
(c) 2026 PUC Minas - Educação Continuada

# Step 04: O Agente DevOps Orientado a Eventos Completo (Aula 06)

Neste quarto e último laboratório, você vai consolidar todos os conceitos do curso conectando seu agente inteligente a uma Arquitetura Orientada a Eventos (EDA) e adicionando persistência em banco de dados NoSQL (Firestore).

---

## Objetivos
1. Criar um tópico Pub/Sub chamado build-failures para representar falhas automáticas de pipeline.
2. Configurar a Cloud Function para ser disparada por eventos desse tópico de forma totalmente assíncrona.
3. Conceder as permissões adequadas de menor privilégio para a Service Account do agente (roles/aiplatform.user e roles/datastore.user).
4. Executar o loop ReAct ao receber o evento, e gravar o relatório detalhado de triagem no Firestore.

---

## Instruções de Execução

### 1. Inicializar e Aplicar o Terraform
Navegue até esta pasta e execute os comandos para provisionar a infraestrutura:

*Observação: Se o banco de dados Firestore Native padrão (default) já estiver criado no projeto devido à Aula 02, o Terraform irá identificá-lo automaticamente ou dará erro de duplicação. Se der erro, você pode comentar o bloco do recurso google_firestore_database no main.tf ou importá-lo.*

```bash
# Inicializar o Terraform
terraform init

# Validar e implantar a infraestrutura
terraform apply -var="project_id=$(gcloud config get-value project)" -auto-approve
```

### 2. Testar o Fluxo Orientado a Eventos (De Ponta a Ponta)
Execute o script de teste para publicar as mensagens de falha diretamente no Pub/Sub e disparar o agente:

```bash
# Executar o script de teste automatizado
chmod +x test_full.sh
./test_full.sh
```

Ou execute manualmente publicando as falhas via gcloud CLI:

**Simular Falha Transitória de Infraestrutura (build-101):**
```bash
gcloud pubsub topics publish build-failures --message='{"build_id": "build-101"}'
```

**Simular Erro de Sintaxe de Código (build-202):**
```bash
gcloud pubsub topics publish build-failures --message='{"build_id": "build-202"}'
```

### 3. Verificar os Resultados no Firestore
Abra o Console do GCP e navegue até o Firestore.
- Veja a coleção build_triages.
- Verifique os dois documentos criados (build-101 e build-202).
- Analise os campos como conclusion, execution_steps (com todo o histórico de chamadas de ferramentas e observações) e o carimbo de data/hora updated_at.

Você também pode verificar os logs de execução da Cloud Function:
```bash
gcloud functions logs read triage-agent-event-driven --gen2 --region=us-central1 --limit=30
```

---

## Conclusão do Curso
Parabéns! Você acaba de construir uma arquitetura de IA em DevOps moderna de ponta a ponta:
- Assíncrona e Desacoplada (EDA): Reage a eventos do Pub/Sub.
- Inteligente (IA + Loop ReAct): Raciocina sobre logs de erros reais e toma ações autônomas.
- Segura (IAM): Roda sob privilégios mínimos.
- Observável: Produz logs estruturados e passos rastreáveis salvos no banco.
- Orientada a Dados (CQRS / Read Model): Salva o modelo de visualização diretamente no Firestore.

# Step 01: Integração Base com Vertex AI & Gemini (Aula 06)

Neste primeiro laboratório, você vai criar a infraestrutura básica e implementar a comunicação inicial com a plataforma de IA generativa do Google Cloud (Vertex AI) usando o modelo Gemini 1.5 Flash.

---

## Objetivos
1. Provisionar uma Cloud Function HTTP Gen 2 utilizando o Terraform.
2. Criar uma Service Account dedicada com as permissões IAM adequadas (roles/aiplatform.user).
3. Inicializar o SDK do Vertex AI em Python e consumir o modelo Gemini para responder a prompts enviados via JSON.

---

## Instruções de Execução

### 1. Inicializar e Aplicar o Terraform
Navegue até esta pasta e execute os comandos para provisionar a infraestrutura:

```bash
# Inicializar o Terraform
terraform init

# Validar e implantar a infraestrutura
terraform apply -var="project_id=$(gcloud config get-value project)" -auto-approve
```

Ao finalizar, guarde a URL da função gerada no output (function_url).

### 2. Testar o Endpoint com Curl
Como a função exige autenticação (padrão de segurança estabelecido nas aulas anteriores), use seu token de identidade para realizar a chamada de teste:

```bash
# Executar o script de teste automatizado
chmod +x test_step1.sh
./test_step1.sh
```

Ou execute manualmente pelo terminal:

```bash
TOKEN=$(gcloud auth print-identity-token)
URL=$(terraform output -raw function_url)

curl -X POST "$URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explique brevemente o que é arquitetura Serverless em uma frase."}'
```

---

## O que analisar?
- IAM: Note como a Service Account criada (triage-agent-sa) recebeu apenas o papel de roles/aiplatform.user seguindo o princípio de menor privilégio. Ela não possui acesso de escrita ao banco ou a outros recursos do GCP neste momento.
- SDK Python: Veja em src/main.py como a chamada ao Gemini se resume a poucas linhas de código idiomático com GenerativeModel.

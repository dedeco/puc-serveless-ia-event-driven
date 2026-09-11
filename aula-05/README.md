# Guia Prático - CI/CD Automatizado com Cloud Build e Secret Manager (Aula 05)

Este guia consolida todos os comandos necessários para provisionar, implantar e testar a calculadora serverless com esteira de CI/CD automatizada utilizando o **Google Cloud Build** e o **Google Secret Manager**.

---

## 🚀 Pré-requisitos e Configuração Inicial

Antes de executar, certifique-se de estar conectado no projeto correto do Google Cloud:

```bash
# Definir o projeto ativo no gcloud
gcloud config set project andresousa-puc

# Verificar se o projeto foi configurado corretamente
gcloud config get-value project
```

---

## 🛠️ 1. Provisionamento de Infraestrutura e IAM

Para automatizar a criação da Service Account, configuração do segredo e liberação de permissões IAM necessárias para o Cloud Build, execute o script de automação:

```bash
# Tornar o script executável
chmod +x aula-05/setup_infra.sh

# Executar o script de provisionamento
./aula-05/setup_infra.sh
```

### O que este script faz?
1. Ativa as APIs do **Secret Manager, Cloud Build, Cloud Run, Cloud Functions e Artifact Registry**.
2. Cria a Service Account dedicada `calculator-service-sa` para a execução da função.
3. Cria o segredo `calculator-secret` no **Secret Manager** e adiciona uma versão inicial (`Chave-Super-Secreta-Aula-05`).
4. Concede permissão de acesso (`secretAccessor`) ao segredo para a Service Account da função.
5. Libera as permissões necessárias para o executor do **Cloud Build** (SA padrão do Compute Engine) para que ele possa gerenciar e atualizar a função.

---

## ⚙️ 2. Execução da Esteira de CI/CD (Cloud Build)

A esteira de CI/CD é definida no arquivo `cloudbuild.yaml`. Ela executa as seguintes etapas sequenciais:
1. **Testes Unitários:** Levanta um container `python:3.11-slim`, instala as dependências em `requirements.txt` e roda o `test_main.py` com `unittest`.
2. **Deploy Automático:** Faz o deploy da Cloud Function Gen 2 utilizando o papel IAM da Service Account criada e monta o segredo do Secret Manager como variável de ambiente (`CALCULATOR_SECRET`).

Para disparar a esteira manualmente a partir dos arquivos locais:

```bash
gcloud builds submit --config=cloudbuild.yaml .
```

---

## 🧪 3. Validação e Teste do Endpoint

Como a função foi implantada seguindo as políticas recomendadas de segurança (**acesso restrito / autenticado**), você precisa de um token de identidade válido do GCP para consumi-la.

Você pode rodar o script de teste automatizado:

```bash
# Tornar o script executável
chmod +x aula-05/test_endpoint.sh

# Executar o teste
./aula-05/test_endpoint.sh
```

Ou executar manualmente via terminal:

```bash
# Gerar token de identidade temporário
TOKEN=$(gcloud auth print-identity-token)

# URL do endpoint implantado
URL="https://calculator-service-aula5-uucgfw647q-uc.a.run.app"

# Fazer a requisição POST autenticada
curl -i -X POST "$URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"operation": "add", "a": 10, "b": 5}'
```

### Exemplo de Retorno com Sucesso (Segredo Injetado)
```json
{
  "a": 10,
  "b": 5,
  "operation": "add",
  "result": 15,
  "secret_value": "Chave-Super-Secreta-Aula-05"
}
```

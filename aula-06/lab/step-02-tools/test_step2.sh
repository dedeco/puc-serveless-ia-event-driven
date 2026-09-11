#!/bin/bash
echo ">>> TESTE STEP 2: Validando o Function Calling do Gemini"

# 1. Recuperar a URL da função usando Terraform Output
if ! command -v terraform &> /dev/null; then
    echo "Erro: Terraform não está instalado."
    exit 1
fi

URL=$(terraform output -raw function_url 2>/dev/null)

if [ -z "$URL" ] || [ "$URL" == "No outputs found" ]; then
    echo "Erro: URL da função não encontrada. Certifique-se de que o 'terraform apply' foi executado com sucesso."
    exit 1
fi

echo "URL da Função: $URL"

# 2. Gerar Token de Identidade
echo "Gerando token de identidade..."
TOKEN=$(gcloud auth print-identity-token)

if [ -z "$TOKEN" ]; then
    echo "Erro ao gerar o token de identidade do gcloud."
    exit 1
fi

# 3. Teste do Cenário A: Com necessidade de ferramenta
echo -e "\n--------------------------------------------------------------"
echo "Cenário A: Enviando um prompt de triagem de build (Ativa ferramenta)"
echo 'Prompt: "Busque os logs do build de ID build-999 para que eu possa analisar o erro."'

RESPONSE_A=$(curl -s -X POST "$URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Busque os logs do build de ID build-999 para que eu possa analisar o erro."}')

echo -e "\nJSON Recebido no Cenário A:"
echo "$RESPONSE_A"


# 4. Teste do Cenário B: Sem necessidade de ferramenta
echo -e "\n--------------------------------------------------------------"
echo "Cenário B: Enviando prompt genérico (Não ativa ferramenta)"
echo 'Prompt: "Olá, me diga qual é a importância de DevOps com IA em poucas palavras."'

RESPONSE_B=$(curl -s -X POST "$URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Olá, me diga qual é a importância de DevOps com IA em poucas palavras."}')

echo -e "\nJSON Recebido no Cenário B:"
echo "$RESPONSE_B"

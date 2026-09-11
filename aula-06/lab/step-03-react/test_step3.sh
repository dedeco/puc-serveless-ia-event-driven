#!/bin/bash
echo ">>> TESTE STEP 3: Validando o Agente ReAct em Ação"

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

# 3. Teste do Cenário 1: Erro transitório (Gera reexecução)
echo -e "\n--------------------------------------------------------------"
echo "Teste 1: Triando o build-101 (Falha transitória de infraestrutura)"
echo 'Prompt: "Investigue por que o build build-101 quebrou e tome a melhor decisao."'

RESPONSE_1=$(curl -s -X POST "$URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Investigue por que o build build-101 quebrou e tome a melhor decisao."}')

echo -e "\nResposta do Teste 1 (JSON Completo):"
echo "$RESPONSE_1"


# 4. Teste do Cenário 2: Erro de código (Não gera reexecução)
echo -e "\n--------------------------------------------------------------"
echo "Teste 2: Triando o build-202 (Erro de sintaxe)"
echo 'Prompt: "Investigue por que o build build-202 quebrou e tome a melhor decisao."'

RESPONSE_2=$(curl -s -X POST "$URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Investigue por que o build build-202 quebrou e tome a melhor decisao."}')

echo -e "\nResposta do Teste 2 (JSON Completo):"
echo "$RESPONSE_2"

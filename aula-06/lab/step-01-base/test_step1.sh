#!/bin/bash
echo ">>> TESTE STEP 1: Validando a integração básica com Gemini"

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

# 3. Fazer requisição
echo "Enviando requisição de teste para o Gemini..."
echo 'Prompt: "Explique brevemente o que é arquitetura Serverless em uma frase."'


RESPONSE=$(curl -s -X POST "$URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "gemini-3.1-pro-preview",
  "prompt": "Prompt para Interpretação de Erros de Pipeline\nPapel:\nAtue como um Especialista em DevOps e Engenheiro de Plataforma Sênior, com foco em solução de problemas de pipelines de CI/CD (GitHub Actions, GitLab CI, Jenkins, Azure DevOps, Bitbucket Pipelines, etc.).\n\nTarefa:\nAnálise a mensagem de erro da pipeline fornecida e forneça um diagnóstico estruturado para correção rápida.\n\nContexto e Informações:\n\nPlataforma da Pipeline: Google Cloud Build\n\nLinguagem/Framework/Ferramenta envolvida: Python 3.11, Flask\n\nLog ou Mensagem de Erro:\n\nstarting build \"21095bb0-f17f-4567-85f6-5248b1077731\"\nFETCHSOURCE\nFrom https://github.com/dedeco/calculator-service\n * branch            14f3c95d66f0c0d6399a51e7e73ebc1e95e5d4f2 -> FETCH_HEAD\nHEAD is now at 14f3c95 Merge pull request #6 from dedeco/develop\nGitCommit:\n14f3c95d66f0c0d6399a51e7e73ebc1e95e5d4f2\nBUILD\nStarting Step #0\nPulling image: python:3.11-slim\nDigest: sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534\nStatus: Downloaded newer image for python:3.11-slim\nInstalling collected packages: watchdog, MarkupSafe, itsdangerous, gunicorn, deprecation, click, blinker, Werkzeug, Jinja2, cloudevents, Flask, functions-framework\nSuccessfully installed Flask-3.0.3 Jinja2-3.1.6 MarkupSafe-3.0.3 Werkzeug-3.1.8 blinker-1.9.0 click-8.5.0 cloudevents-1.13.0 deprecation-2.1.0 functions-framework-3.8.1 gunicorn-26.2.0 itsdangerous-2.2.0 watchdog-6.0.0\nF....F\n======================================================================\nFAIL: test_add (test_main.TestCalculator.test_add)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"/workspace/test_main.py\", line 9, in test_add\n    self.assertEqual(res[\"result\"], 15)\nAssertionError: 5 != 15\n======================================================================\nFAIL: test_subtract (test_main.TestCalculator.test_subtract)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"/workspace/test_main.py\", line 15, in test_subtract\n    self.assertEqual(res[\"result\"], 5)\nAssertionError: 15 != 5\n----------------------------------------------------------------------\nRan 6 tests in 0.001s\nFAILED (failures=2)\nFinished Step #0\nERROR\nERROR: build step 0 \"python:3.11-slim\" failed: step exited with non-zero status: 1\n\nInstruções de Resposta:\n\nResponda de forma direta e técnica, dividindo a resposta exatamente nas seguintes partes:\n\nO que aconteceu (Causa Raiz): Explique em 2 ou 3 frases simples o motivo real da falha (ex: versão incompatível, falta de variável de ambiente, falha de permissão, memória excedida).\n\nAções para Corrigir (Passo a Passo): Forneça uma lista numerada das etapas necessárias para resolver o erro. Se houver código, arquivo de configuração (YAML, Dockerfile) ou comandos CLI para ajustar, forneça o trecho exato.\n\nOpções/Alternativas de Contorno: Se houver mais de uma maneira de resolver ou uma solução temporária rápida, liste brevemente as alternativas."
}')

echo -e "\nResposta completa da Cloud Function:"
echo "$RESPONSE"

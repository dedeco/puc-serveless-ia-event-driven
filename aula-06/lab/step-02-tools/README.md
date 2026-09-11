# Step 02: Declarando Ferramentas (Function Calling) (Aula 06)

Neste segundo laboratório, você vai aprender um dos conceitos mais importantes na criação de agentes inteligentes: Function Calling (Chamada de Função).

---

## Objetivos
1. Declarar uma ferramenta (get_build_logs) usando a estrutura de schema do Vertex AI (FunctionDeclaration).
2. Disponibilizar essa ferramenta para o modelo Gemini 1.5 Flash.
3. Compreender que o modelo não executa a função, mas retorna um objeto estruturado contendo a intenção de execução e os parâmetros necessários extraídos do prompt do usuário.

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

### 2. Testar o Endpoint com o Script de Teste
Execute o script de teste para validar se o Function Calling está ativo:

```bash
# Executar o script de teste automatizado
chmod +x test_step2.sh
./test_step2.sh
```

Ou execute manualmente no terminal para ver os dois comportamentos do modelo:

**Cenário A: Prompt que deve ativar a ferramenta (Investigar build)**
```bash
TOKEN=$(gcloud auth print-identity-token)
URL=$(terraform output -raw function_url)

curl -X POST "$URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Busque os logs do build de ID build-999 para que eu possa analisar o erro."}'
```
*Note que o retorno conterá "function_calling_detected": true e os argumentos estruturados que o modelo extraiu.*

**Cenário B: Prompt que não deve ativar a ferramenta (Texto livre)**
```bash
curl -X POST "$URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Olá, me conte uma piada curta."}'
```
*Note que o retorno conterá "function_calling_detected": false e a resposta normal em texto livre.*

---

## O que analisar?
- Schema do Parâmetro: Veja em src/main.py como especificamos que o argumento build_id é obrigatório ("required": ["build_id"]) e do tipo string. O Gemini respeita rigorosamente essa especificação.
- Fluxo Decisório: O modelo decide sozinho, com base na descrição semântica que você forneceu na declaração da ferramenta, se a ferramenta é relevante ou não para atender ao pedido do usuário.

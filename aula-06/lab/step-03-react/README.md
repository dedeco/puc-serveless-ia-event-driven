# Step 03: O Loop ReAct (Reasoning, Action, Observation) (Aula 06)

Neste terceiro laboratório, você vai implementar o loop completo do padrão ReAct (Raciocinar + Agir + Observar) de ponta a ponta.

---

## Objetivos
1. Declarar múltiplas ferramentas para o modelo (get_build_logs e trigger_pipeline_retry).
2. Implementar a orquestração do loop ReAct em Python usando o recurso de chat contínuo (start_chat) e envio estruturado de observações (Part.from_function_response).
3. Observar a capacidade de tomada de decisão do modelo em cenários reais:
   - Cenário de Falha Transitória: O modelo lê um erro de rede e decide reexecutar o pipeline automaticamente.
   - Cenário de Erro de Código: O modelo lê um erro de sintaxe e decide alertar os engenheiros, evitando reexecuções desnecessárias.

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

### 2. Testar o Agente ReAct com o Script de Teste
Execute o script para ver o agente em ação resolvendo os dois problemas:

```bash
# Executar o script de teste automatizado
chmod +x test_step3.sh
./test_step3.sh
```

Ou teste manualmente pelo terminal:

**Teste 1: Triando o build-101 (Falha de infraestrutura/conexão)**
```bash
TOKEN=$(gcloud auth print-identity-token)
URL=$(terraform output -raw function_url)

curl -X POST "$URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Investigue por que o build build-101 quebrou e tome a melhor decisao."}'
```
*Note que o loop chamará get_build_logs, lerá a falha de timeout, chamará trigger_pipeline_retry e concluirá informando que a reexecução foi iniciada.*

**Teste 2: Triando o build-202 (Erro de sintaxe de código)**
```bash
curl -X POST "$URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Investigue por que o build build-202 quebrou e tome a melhor decisao."}'
```
*Note que o loop chamará get_build_logs, identificará o SyntaxError, decidirá NÃO chamar o retry e terminará explicando amigavelmente que o desenvolvedor precisa consertar a linha de código.*

---

## O que analisar?
- O Loop ReAct em Python: Olhe o bloco while response.candidates[0].function_calls no arquivo src/main.py. É ali que a orquestração acontece de forma dinâmica.
- Instruções de Sistema (System Instruction): Veja como as instruções de sistema moldam a lógica de decisão do modelo sem a necessidade de if/else rígidos no código Python. O modelo lê semanticamente os logs e decide o caminho a seguir.

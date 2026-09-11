# Explicação do Funcionamento do Step 02: Declarando Ferramentas

Este documento explica de forma detalhada o que o código do laboratório `step-02-tools` e o seu script de teste fazem.

---

## 1. O que o código da Cloud Function (`src/main.py`) faz?

O código demonstra o conceito de **Function Calling (Chamada de Função)** usando o Vertex AI e o modelo Gemini 2.5 Flash. Ele expõe uma API HTTP que atua como um cérebro de triagem inteligente de DevOps.

### Como funciona passo a passo:

1. **Declaração da Ferramenta (`get_build_logs`):**
   Definimos uma ferramenta chamada `get_build_logs` com uma descrição semântica clara e seus parâmetros esperados:
   - **Descrição:** *"Retorna os logs de um build que falhou no Cloud Build, a partir do build ID. Use para diagnosticar falhas de pipeline."*
   - **Parâmetros:** Um campo obrigatório (`required: ["build_id"]`) do tipo `string` chamado `build_id`, que representa o identificador do build.

2. **Decisão Inteligente do Modelo:**
   Quando a Cloud Function recebe uma requisição HTTP contendo um `prompt`:
   - **Cenário de Ferramenta (Ativação):** Se o usuário perguntar algo como *"Busque os logs do build-999"*, o Gemini analisa semanticamente a solicitação e percebe que a ferramenta `get_build_logs` é perfeita para resolver a intenção. Em vez de inventar uma resposta de texto, o modelo responde estruturadamente com a intenção de chamar a função e extrai o argumento correto (`build_id: "build-999"`).
   - **Cenário de Conversação Livre (Não-Ativação):** Se o usuário perguntar algo geral como *"Me conte uma piada"* ou *"Qual a importância de DevOps?"*, o Gemini entende que nenhuma das ferramentas registradas é aplicável. Ele responde normalmente gerando uma resposta textual fluida.

> **Importante:** O Gemini **não executa** a função real. Ele apenas analisa o prompt, decide usar a ferramenta e extrai os argumentos estruturados de forma confiável para que o seu código backend possa executar a ação real em seguida.

---

## 2. O que o script de teste (`test_step2.sh`) faz?

O script `test_step2.sh` é um utilitário de validação automática que simula as interações com a Cloud Function implantada. Ele executa as seguintes etapas:

1. **Recupera a URL da Função:** Executa comandos do Terraform (`terraform output -raw function_url`) para descobrir o endereço seguro sob o qual a Cloud Function foi criada.
2. **Gera Token de Autenticação:** Executa `gcloud auth print-identity-token` para obter de forma dinâmica um token JWT correspondente ao seu usuário logado no Google Cloud SDK. Esse token é repassado no cabeçalho `Authorization: Bearer <TOKEN>` para passar pela autenticação padrão da Cloud Function.
3. **Valida o Cenário A (Ativação da Ferramenta):**
   - Dispara uma requisição HTTP `POST` enviando o prompt: *"Busque os logs do build de ID build-999 para que eu possa analisar o erro."*
   * **Resultado esperado:** Retorna um JSON com `"function_calling_detected": true`, confirmando que o Gemini identificou corretamente que precisava da ferramenta `get_build_logs` e extraiu com sucesso o argumento `build_id` como `"build-999"`.
4. **Valida o Cenário B (Conversação Comum):**
   - Dispara outra requisição HTTP `POST` enviando um prompt genérico: *"Olá, me diga qual é a importância de DevOps com IA em poucas palavras."*
   * **Resultado esperado:** Retorna um JSON com `"function_calling_detected": false` e um texto com a resposta livre gerada pelo Gemini, mostrando que o modelo não ativou a ferramenta erroneamente.

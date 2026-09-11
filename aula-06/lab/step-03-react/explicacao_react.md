# Explicação do Funcionamento do Step 03: O Loop ReAct

Este documento descreve detalhadamente o funcionamento do terceiro laboratório (`step-03-react`), as correções que realizamos no modelo e os resultados dos testes automatizados de tomada de decisão do agente de DevOps.

---

## 1. O Conceito do Loop ReAct
O padrão **ReAct (Reasoning, Action, Observation)** combina raciocínio estruturado com a capacidade de interagir com o mundo externo através de ferramentas. Diferente de fluxos condicionais rígidos (`if/else`), o agente inteligente decide dinamicamente o que fazer:
1. **Raciocínio (Thought):** O modelo analisa o estado atual e decide se precisa chamar alguma ferramenta.
2. **Ação (Act):** O modelo solicita que seu backend execute uma ferramenta com parâmetros estruturados.
3. **Observação (Observation):** O backend executa a ferramenta, obtém o resultado e envia-o de volta ao modelo.
4. **Iteração:** O modelo avalia a nova informação e pode decidir chamar outra ferramenta ou concluir seu raciocínio.

---

## 2. Ajuste Técnico Realizado
No arquivo original `src/main.py`, o modelo utilizado era o `gemini-1.5-flash`. Porém, devido a restrições de disponibilidade regional na infraestrutura da GCP, essa versão retornou um erro HTTP `404 (Not Found)`. 

Ajustamos cirurgicamente o modelo para **`gemini-2.5-flash`** (a versão mais moderna e disponível), que resolveu o problema e garantiu tempos de resposta extremamente rápidos.

---

## 3. Comportamento nos Cenários de Teste

O script `test_step3.sh` validou duas situações distintas na triagem de builds do Cloud Build:

### Teste 1: Triagem do `build-101` (Falha Transitória de Infraestrutura)
* **Prompt original:** *"Investigue por que o build build-101 quebrou e tome a melhor decisao."*
* **Histórico de Execução do Loop:**
  1. **Ação 1 (get_build_logs):** O agente solicitou a busca dos logs para `build-101`.
  2. **Observação 1:** Retornou `"ERROR: Connection timeout to database at 10.0.1.5. Retrying failed after 3 attempts."`
  3. **Raciocínio:** O Gemini identificou que um timeout de conexão com banco de dados é uma **falha transitória** de infraestrutura. Seguindo as instruções de sistema, ele decidiu que o melhor curso de ação seria tentar uma nova execução do pipeline.
  4. **Ação 2 (trigger_pipeline_retry):** O agente acionou o retry para o `build-101`.
  5. **Observação 2:** Retornou `"SUCCESS: Nova execução de pipeline criada para o build build-101 (ID da nova execução: run-build-101-retry)."`
  6. **Conclusão:** O loop terminou e o modelo forneceu o diagnóstico final confirmando que a reexecução foi iniciada.

---

### Teste 2: Triagem do `build-202` (Erro de Código)
* **Prompt original:** *"Investigue por que o build build-202 quebrou e tome a melhor decisao."*
* **Histórico de Execução do Loop:**
  1. **Ação 1 (get_build_logs):** O agente solicitou os logs para `build-202`.
  2. **Observação 1:** Retornou `"ERROR: SyntaxError: invalid syntax in main.py, line 42. x = 10 y = 20"`
  3. **Raciocínio:** O Gemini interpretou que um `SyntaxError` é um **erro de código** (não-transitório). Ele sabe que reexecutar o pipeline sem corrigir o arquivo seria inútil. Por isso, ele **não chamou** a ferramenta de retry.
  4. **Conclusão:** O loop terminou imediatamente após a primeira observação. O modelo gerou uma resposta amigável e instrutiva para o desenvolvedor explicando que o problema está na linha 42 e precisa ser corrigido manualmente antes de um novo deploy.

---

## 4. Orquestração do Loop em Python (`src/main.py`)
No código Python, o loop ReAct é mantido através da classe `start_chat()` do SDK do Vertex AI. Isso permite que enviemos os resultados das ferramentas preservando o contexto das interações anteriores:

```python
# Usamos o chat para manter o histórico de pensamentos e execuções
chat = model.start_chat()
response = chat.send_message(prompt)

while response.candidates[0].function_calls and loop_count < max_loops:
    loop_count += 1
    call = response.candidates[0].function_calls[0]
    
    # Executa a ação correspondente no backend local...
    result = executar_acao_local(call.name, call.args)

    # Devolve a Observação como um Part do tipo function_response
    response = chat.send_message(
        Part.from_function_response(
            name=call.name,
            response={"result": result}
        )
    )
```

Essa elegante estrutura evita loops condicionais rígidos no código e delega toda a tomada de decisão para a inteligência lógica do Gemini.

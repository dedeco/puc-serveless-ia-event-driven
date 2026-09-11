# Aula 6: Serverless e IA (Projeto Final)

## Foco
- Integração com Vertex AI
- Function calling e orquestração de agentes

## Laboratórios Práticos (Labs)

Esta aula conta com laboratórios práticos divididos em 4 etapas (steps) incrementais para você dominar o uso de IA e agentes inteligentes de forma serverless e orientada a eventos.

### Como Executar os Laboratórios
Para facilitar sua navegação, criamos um menu interativo. Basta executar o comando abaixo a partir da raiz do projeto:

```bash
./aula-06/menu.sh
```

### Estrutura dos Laboratórios
1. [Step 01 - Base](lab/step-01-base): Comunicação inicial com o Gemini 1.5 Flash usando o SDK da Vertex AI em uma Cloud Function HTTP Gen 2.
2. [Step 02 - Tools](lab/step-02-tools): Uso de Function Calling para ensinar o modelo a expressar intenções e parâmetros usando schemas.
3. [Step 03 - ReAct](lab/step-03-react): Implementação de um loop ReAct (Raciocinar + Agir + Observar) completo em Python para triagem inteligente de builds.
4. [Step 04 - Full](lab/step-04-full): Integrante final acoplando o agente inteligente DevOps ao Pub/Sub (Event-Driven) e persistência de diagnósticos no Firestore NoSQL.

---

## Projeto Final
Consolidar os checkpoints em uma arquitetura event-driven completa integrada com IA.

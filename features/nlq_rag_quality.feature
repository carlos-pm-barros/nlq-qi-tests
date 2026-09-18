# language: pt
Funcionalidade: Qualidade semântica do NLQ com RAG
  Como engenheiro de qualidade de IA
  Quero validar NLQ, recuperação RAG e avaliação semântica
  Para impedir regressões de qualidade no pipeline

  Esquema do Cenário: Validar consulta NLQ com RAG e LLM-as-a-Judge
    Dado o caso de teste "<case_id>" do dataset
    Quando envio a pergunta para o NLQ
    Então a API NLQ deve retornar sucesso
    E a resposta não deve estar vazia
    E o RAG deve retornar contexto
    E executo o LLM-as-a-Judge três vezes
    E o resultado deve atender ao Quality Gate

    Exemplos:
      | case_id |
      | NLQ-001 |
      | NLQ-002 |

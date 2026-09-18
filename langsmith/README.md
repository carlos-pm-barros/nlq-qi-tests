# LangSmith

A API usa `@traceable` no pipeline `NLQ → RAG → SQL → resposta → Judge → Quality Gate`.

Configure:
- `LANGSMITH_TRACING=true`
- `LANGSMITH_API_KEY`
- `LANGSMITH_PROJECT=nlq-ai-tests`

Os datasets funcionais de QA ficam em `/datasets`. Eles podem ser posteriormente sincronizados com datasets/experiments do LangSmith.

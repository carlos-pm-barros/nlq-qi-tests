# nlq-ai-tests

Solução única para desenvolvimento e teste de uma aplicação de **NLQ + RAG + LLM + LLM-as-a-Judge**, com **pytest + pytest-bdd**, **LangSmith**, **Allure**, **Docker** e **GitHub Actions**.

## Arquitetura

```text
NLQ do usuário
     ↓
FastAPI / NLQ Layer
     ↓
Retriever / RAG
     ↓
LLM → SQL
     ↓
Banco somente leitura
     ↓
LLM → Resposta
     ↓
LLM-as-a-Judge × 3
     ↓
Quality Gate
  média >= 0.85
  mínimo >= 0.60
  stddev <= 0.20
     ↓
LangSmith
Trace / Dataset / Experiment / Metrics
```

## Estrutura

```text
nlq-ai-tests/
├── src/                    # NLQ + RAG + LLM + Judge
├── tests/
│   ├── steps/              # pytest-bdd
│   ├── unit/               # pytest
│   └── clients/
├── datasets/
├── features/
├── langsmith/
├── allure/
├── Dockerfile
├── docker-compose.yml
└── .github/workflows/
```

## Preparação

Python 3.12 recomendado.

```bash
python3.12 -m venv .venv
```

Ative o virtualenv e execute:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Copie `.env.example` para `.env` e informe ao menos `OPENAI_API_KEY`. Para tracing, configure também `LANGSMITH_API_KEY`.

## Executar API

Use este caminho quando quiser rodar a API diretamente na sua máquina, dentro do virtualenv:

```bash
python -m uvicorn src.app.main:app --reload
```

Swagger: `http://localhost:8000/docs`

Health: `http://localhost:8000/health`

## Executar API com Docker Compose

O `docker-compose.yml` entra no fluxo como a forma containerizada de subir a API para que ela possa ser testada depois pelo pytest.

Ele usa o `Dockerfile`, carrega as variáveis do arquivo `.env`, publica a porta `8000` do container em `localhost:8000` e mantém um volume Docker para dados em `/app/data`.

```bash
docker compose up --build
```

Em outro terminal, valide que a API subiu:

```bash
curl http://localhost:8000/health
```

Resposta esperada:

```json
{"status":"UP"}
```

Para manter a API rodando em segundo plano:

```bash
docker compose up --build -d
```

Para encerrar:

```bash
docker compose down
```

## Executar testes

Para executar os testes, gerar os resultados do Allure e abrir o relatório ao final:

```bash
./scripts/run_tests.sh
```

No Windows 11, usando PowerShell:

```powershell
.\scripts\run_tests.ps1
```

O script executa:

```bash
pytest tests -v --alluredir=allure/results
```

E, se os testes passarem, abre o relatório com:

```bash
allure serve allure/results
```

Para executar sem abrir o relatório:

```bash
OPEN_ALLURE=false ./scripts/run_tests.sh
```

No Windows 11:

```powershell
.\scripts\run_tests.ps1 -OpenAllure $false
```

Os testes usam `NLQ_BASE_URL=http://localhost:8000` e `NLQ_ENDPOINT=/api/nlq` por padrão, conforme definido no `.env.example`.

## Observação sobre RAG

O exemplo mantém um retriever lexical local para reduzir dependências e deixar o laboratório simples. `src/app/rag.py` é o ponto de extensão para pgvector, Chroma, Pinecone ou outro Vector DB.

## Segurança NLQ → SQL

A aplicação de demonstração aceita somente `SELECT`. Para produção, complemente com credencial read-only, allowlist de schemas/tabelas, parser SQL/AST, timeout e limites de linhas.

## Fluxo de QA

O teste BDD envia a pergunta à própria API. A API recupera contexto, gera SQL, consulta o banco, produz a resposta, executa o Judge três vezes e calcula o Quality Gate. O pytest-bdd valida o resultado de ponta a ponta e publica evidências no Allure.

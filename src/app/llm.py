import json, os
from openai import OpenAI

def _client():
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def nlq_to_sql(question: str, contexts: list[str]) -> str:
    prompt = f"""Você é um gerador seguro de SQL SQLite.
Use SOMENTE SELECT e a tabela/colunas descritas no contexto.
Retorne somente SQL, sem markdown.

CONTEXTO:
{chr(10).join(contexts)}

PERGUNTA:
{question}
"""
    r = _client().responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        input=prompt,
        temperature=0
    )
    return r.output_text.strip().replace("```sql","").replace("```","").strip()

def rows_to_answer(question: str, contexts: list[str], rows: list[dict]) -> str:
    prompt = f"""Responda em português, diretamente e sem inventar dados.
Pergunta: {question}
Contexto: {json.dumps(contexts, ensure_ascii=False)}
Resultado SQL: {json.dumps(rows, ensure_ascii=False)}
"""
    r = _client().responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        input=prompt,
        temperature=0
    )
    return r.output_text.strip()

def judge(question: str, answer: str, reference_context: str,
          acceptance_criteria: list[str]) -> tuple[float, str]:
    prompt = f"""Você é um LLM-as-a-Judge.
Avalie a resposta contra contexto e critérios.
Retorne JSON estrito: {{"score":0.0,"reason":"..."}}.
score deve estar entre 0 e 1.

PERGUNTA:
{question}

RESPOSTA:
{answer}

CONTEXTO/REFERÊNCIA:
{reference_context}

CRITÉRIOS:
{json.dumps(acceptance_criteria, ensure_ascii=False)}
"""
    r = _client().responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        input=prompt,
        temperature=0
    )
    raw = r.output_text.strip().replace("```json","").replace("```","").strip()
    data = json.loads(raw)
    return float(data["score"]), str(data.get("reason", ""))

import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from langsmith import traceable

load_dotenv()

from src.app.database import init_db, execute_readonly
from src.app.rag import retrieve
from src.app.llm import nlq_to_sql, rows_to_answer, judge
from src.app.quality import calculate_gate
from src.app.models import NLQRequest, NLQResponse, JudgeEvaluation

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="NLQ + RAG + LLM-as-a-Judge API",
    version="1.0.0",
    description="API demonstrativa para AI Quality Engineering.",
    lifespan=lifespan,
)

@app.get("/health")
def health():
    return {"status": "UP"}

@traceable(name="nlq-rag-judge-pipeline", run_type="chain")
def process(req: NLQRequest) -> NLQResponse:
    contexts = retrieve(req.question)
    sql = nlq_to_sql(req.question, contexts)
    rows = execute_readonly(sql)
    answer = rows_to_answer(req.question, contexts, rows)

    reference = "\n".join(contexts)
    repetitions = int(os.getenv("JUDGE_REPETITIONS", "3"))
    judge_results = []
    for execution in range(1, repetitions + 1):
        score, reason = judge(
            req.question, answer, reference, req.acceptance_criteria
        )
        judge_results.append(
            JudgeEvaluation(execution=execution, score=score, reason=reason)
        )

    gate = calculate_gate(
        [x.score for x in judge_results],
        float(os.getenv("QUALITY_GATE_MIN_AVERAGE", "0.85")),
        float(os.getenv("QUALITY_GATE_MIN_ITEM", "0.60")),
        float(os.getenv("QUALITY_GATE_MAX_STDDEV", "0.20")),
    )

    return NLQResponse(
        question=req.question,
        answer=answer,
        generated_sql=sql,
        retrieved_contexts=contexts,
        judge_results=judge_results,
        quality_gate=gate,
    )

@app.post("/api/nlq", response_model=NLQResponse)
def nlq(req: NLQRequest):
    try:
        return process(req)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

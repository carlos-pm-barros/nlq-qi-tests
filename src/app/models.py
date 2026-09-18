from pydantic import BaseModel, Field

class NLQRequest(BaseModel):
    question: str = Field(min_length=3)
    acceptance_criteria: list[str] = Field(default_factory=lambda: [
        "Responder diretamente à pergunta",
        "Não inventar fatos ou valores",
        "Usar apenas informações suportadas pelo contexto recuperado",
        "Manter consistência com a referência"
    ])

class JudgeEvaluation(BaseModel):
    execution: int
    score: float
    reason: str = ""

class QualityGate(BaseModel):
    average: float
    minimum: float
    stddev: float
    passed: bool
    failures: list[str]

class NLQResponse(BaseModel):
    question: str
    answer: str
    generated_sql: str | None
    retrieved_contexts: list[str]
    judge_results: list[JudgeEvaluation]
    quality_gate: QualityGate

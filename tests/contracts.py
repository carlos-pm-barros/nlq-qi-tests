from typing import Any
from pydantic import BaseModel

class TestCase(BaseModel):
    id: str
    question: str
    reference_context: str
    acceptance_criteria: list[str]
    expected_sql_contains: list[str] = []

class NLQResult(BaseModel):
    status_code: int
    answer: str
    generated_sql: str | None = None
    retrieved_contexts: list[str] = []
    raw: dict[str, Any] = {}

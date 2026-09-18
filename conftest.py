import json, os
from pathlib import Path
import pytest
from dotenv import load_dotenv

load_dotenv()
os.environ["LANGSMITH_TRACING"] = "false"

from fastapi.testclient import TestClient
from src.app import main as app_module
from tests.clients.nlq_client import NLQClient
from tests.contracts import TestCase

@pytest.fixture(scope="session")
def dataset():
    path = Path(__file__).parent / "datasets/nlq_dataset.json"
    return {x["id"]: TestCase.model_validate(x) for x in json.loads(path.read_text(encoding="utf-8"))}

@pytest.fixture
def nlq_client(monkeypatch):
    def fake_nlq_to_sql(question: str, contexts: list[str]) -> str:
        question_lower = question.lower()
        if "pedidos" in question_lower:
            return "SELECT approved_orders FROM sales WHERE month = 'agosto'"
        return "SELECT total FROM sales WHERE month = 'agosto'"

    def fake_rows_to_answer(question: str, contexts: list[str], rows: list[dict]) -> str:
        first_row = rows[0] if rows else {}
        if "approved_orders" in first_row:
            return f"Foram aprovados {first_row['approved_orders']} pedidos."
        return f"O total de vendas de agosto foi R$ {first_row['total']:,.0f}."

    def fake_judge(
        question: str,
        answer: str,
        reference_context: str,
        acceptance_criteria: list[str],
    ) -> tuple[float, str]:
        return 0.95, "Resposta aderente ao contexto e aos critérios de aceite."

    monkeypatch.setattr(app_module, "nlq_to_sql", fake_nlq_to_sql)
    monkeypatch.setattr(app_module, "rows_to_answer", fake_rows_to_answer)
    monkeypatch.setattr(app_module, "judge", fake_judge)

    endpoint = os.getenv("NLQ_ENDPOINT", "/api/nlq")
    with TestClient(app_module.app, base_url="http://testserver") as client:
        yield NLQClient("http://testserver", endpoint, os.getenv("NLQ_API_KEY", ""), client)

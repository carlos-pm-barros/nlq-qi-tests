import json
import allure
import httpx
import pytest
from pytest_bdd import scenarios, given, when, then, parsers

scenarios("nlq_rag_quality.feature")

@given(parsers.parse('o caso de teste "{case_id}" do dataset'), target_fixture="ctx")
def load_case(case_id, dataset):
    return {"case": dataset[case_id], "nlq": None}

@when("envio a pergunta para o NLQ")
def send_question(ctx, nlq_client):
    case = ctx["case"]
    try:
        result = nlq_client.ask(case.question)
    except httpx.ConnectError as exc:
        pytest.skip(f"API NLQ indisponível em {nlq_client.url}: {exc}")
    ctx["nlq"] = result
    allure.attach(
        json.dumps(result.raw, ensure_ascii=False, indent=2),
        "NLQ + RAG + Judge response",
        allure.attachment_type.JSON
    )

@then("a API NLQ deve retornar sucesso")
def assert_http(ctx):
    detail = str(ctx["nlq"].raw.get("detail", ""))
    if ctx["nlq"].status_code == 500 and "Missing credentials" in detail:
        pytest.skip("API NLQ sem OPENAI_API_KEY configurada no ambiente em execução.")
    assert 200 <= ctx["nlq"].status_code < 300

@then("a resposta não deve estar vazia")
def assert_answer(ctx):
    assert ctx["nlq"].answer.strip()

@then("o RAG deve retornar contexto")
def assert_rag(ctx):
    assert ctx["nlq"].retrieved_contexts

@then("executo o LLM-as-a-Judge três vezes")
def assert_three_judges(ctx):
    judge_results = ctx["nlq"].raw.get("judge_results", [])
    assert len(judge_results) == 3, f"Esperadas 3 avaliações; recebidas {len(judge_results)}"

@then("o resultado deve atender ao Quality Gate")
def assert_quality_gate(ctx):
    raw = ctx["nlq"].raw
    gate = raw.get("quality_gate", {})
    assert gate, "quality_gate ausente"
    allure.attach(json.dumps(gate, indent=2), "Quality Gate", allure.attachment_type.JSON)
    assert gate.get("passed") is True, f"Quality Gate falhou: {gate.get('failures', [])}"

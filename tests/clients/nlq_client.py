import httpx
from tests.contracts import NLQResult

class NLQClient:
    def __init__(self, base_url: str, endpoint: str, api_key: str = "", http_client=None):
        self.url = base_url.rstrip("/") + "/" + endpoint.lstrip("/")
        self.http_client = http_client
        self.headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def ask(self, question: str) -> NLQResult:
        if self.http_client:
            response = self.http_client.post(self.url, json={"question": question}, headers=self.headers)
        else:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(self.url, json={"question": question}, headers=self.headers)
        data = response.json() if response.content else {}
        # Adapt these aliases to the real SUT contract if necessary.
        answer = data.get("answer") or data.get("response") or data.get("output") or ""
        sql = data.get("generated_sql") or data.get("sql")
        contexts = data.get("retrieved_contexts") or data.get("contexts") or data.get("sources") or []
        if isinstance(contexts, str):
            contexts = [contexts]
        return NLQResult(
            status_code=response.status_code,
            answer=str(answer),
            generated_sql=sql,
            retrieved_contexts=[str(x) for x in contexts],
            raw=data,
        )

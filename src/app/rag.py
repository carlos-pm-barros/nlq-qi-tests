from dataclasses import dataclass
import math
import re

@dataclass
class Document:
    id: str
    text: str

DOCUMENTS = [
    Document("schema-sales",
             "Tabela sales: id INTEGER, month TEXT, total REAL, approved_orders INTEGER. "
             "month contém o mês em português; total contém o total de vendas; "
             "approved_orders contém a quantidade de pedidos aprovados."),
    Document("rule-sales",
             "Para perguntas sobre vendas use a coluna total da tabela sales. "
             "Para pedidos aprovados use approved_orders. Filtre o mês pela coluna month."),
    Document("business-aug",
             "Referência de demonstração: agosto possui total de vendas de R$ 1.250.000 e 42 pedidos aprovados."),
]

def _tokens(s: str):
    return set(re.findall(r"[a-záàâãéêíóôõúç0-9_]+", s.lower()))

def retrieve(question: str, k: int = 3) -> list[str]:
    # Vetor lexical local para demo sem dependência externa.
    # Em produção, substitua por pgvector/Chroma/Pinecone/etc.
    q = _tokens(question)
    ranked = []
    for doc in DOCUMENTS:
        d = _tokens(doc.text)
        score = len(q & d) / math.sqrt(max(1, len(q) * len(d)))
        ranked.append((score, doc.text))
    ranked.sort(reverse=True, key=lambda x: x[0])
    return [text for score, text in ranked[:k] if score > 0] or [DOCUMENTS[0].text]

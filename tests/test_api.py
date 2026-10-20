import pytest
from fastapi.testclient import TestClient

import mpesaparse.api as api_module
from mpesaparse.api import create_app
from mpesaparse.categorizer import MerchantCategorizer

RECEIVE = "QH12AB34CD Confirmed. You have received Ksh1,500.00 from JOHN DOE 0712345678 on 19/10/26 at 3:30 PM. New M-PESA balance is Ksh5,430.50."
TILL = "QH12AB34CG Confirmed. Ksh850.00 paid to SUNRISE SUPERMARKET. on 19/10/26 at 4:20 PM. New M-PESA balance is Ksh680.50. Transaction cost, Ksh0.00."


@pytest.fixture(scope="module")
def categorizer():
    return MerchantCategorizer()


@pytest.fixture
def client(categorizer):
    return TestClient(create_app(categorizer))


class FakeCategorizer:
    created = 0
    metrics = {"accuracy": 1.0}

    def __init__(self):
        FakeCategorizer.created += 1

    def predict(self, merchant):
        return "groceries", 0.9


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model_loaded": True}


def test_parse_recognised_message(client):
    response = client.post("/parse", json={"message": TILL})
    assert response.status_code == 200
    body = response.json()
    assert body["recognized"] is True
    assert body["transaction_type"] == "till"
    assert body["amount"] == 850.0
    assert body["counterparty"] == "SUNRISE SUPERMARKET"
    assert body["category"] == "groceries"


def test_parse_unrecognised_message(client):
    body = client.post("/parse", json={"message": "hello there"}).json()
    assert body["recognized"] is False
    assert body["amount"] is None
    assert body["category"] == "unknown"


def test_analyze_batch(client):
    response = client.post(
        "/analyze", json={"messages": [RECEIVE, TILL, "not a message"]}
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["transactions"]) == 3
    summary = body["summary"]
    assert summary["recognised"] == 2
    assert summary["unrecognised"] == 1
    assert summary["money_in"] == 1500.0
    assert summary["money_out"] == 850.0
    assert summary["out_by_category"] == {"groceries": 850.0}


def test_analyze_rejects_empty_list(client):
    assert client.post("/analyze", json={"messages": []}).status_code == 422


def test_analyze_rejects_too_many_messages(client):
    assert client.post("/analyze", json={"messages": ["x"] * 501}).status_code == 422


def test_parse_rejects_too_long_message(client):
    assert client.post("/parse", json={"message": "x" * 1001}).status_code == 422


def test_parse_rejects_missing_field(client):
    assert client.post("/parse", json={}).status_code == 422


def test_model_metrics(client):
    body = client.get("/model/metrics").json()
    assert body["accuracy"] > 0.85
    assert "per_category_f1" in body


def test_categorizer_is_created_lazily_and_once(monkeypatch):
    FakeCategorizer.created = 0
    monkeypatch.setattr(api_module, "MerchantCategorizer", FakeCategorizer)
    client = TestClient(create_app())
    assert client.get("/health").json()["model_loaded"] is False
    client.post("/parse", json={"message": TILL})
    client.post("/parse", json={"message": TILL})
    assert client.get("/health").json()["model_loaded"] is True
    assert FakeCategorizer.created == 1

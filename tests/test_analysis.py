from pathlib import Path

import pytest

from mpesaparse.analysis import analyze

SAMPLE = Path(__file__).resolve().parent.parent / "sample_data" / "messages.txt"


def sample_lines():
    text = SAMPLE.read_text(encoding="utf-8")
    return [line.strip() for line in text.splitlines() if line.strip()]


@pytest.fixture(scope="module")
def result():
    return analyze(sample_lines())


def test_counts(result):
    summary = result["summary"]
    assert summary["transactions_total"] == 8
    assert summary["recognised"] == 7
    assert summary["unrecognised"] == 1


def test_money_totals_ignore_unrecognised_lines(result):
    summary = result["summary"]
    assert summary["money_in"] == 1500.0
    assert summary["money_out"] == 7500.0
    assert summary["fees"] == 35.0


def test_rule_based_categories_in_summary(result):
    out = result["summary"]["out_by_category"]
    assert out["personal_transfer"] == 500.0
    assert out["airtime_data"] == 100.0
    assert out["cash_withdrawal"] == 2000.0


def test_merchant_categories(result):
    by_code = {
        item["transaction_code"]: item["category"]
        for item in result["transactions"]
        if item["transaction_code"]
    }
    assert by_code["QH12AB34CF"] == "utilities"
    assert by_code["QH12AB34CG"] == "groceries"
    assert by_code["QH12AB34CK"] == "health"


def test_no_messages_gives_empty_summary():
    summary = analyze([])["summary"]
    assert summary["transactions_total"] == 0
    assert summary["money_in"] == 0.0
    assert summary["money_out"] == 0.0
    assert summary["out_by_category"] == {}

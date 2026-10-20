import pytest

from mpesaparse.categorizer import MerchantCategorizer, categorize_transaction
from mpesaparse.merchants import generate_merchants


@pytest.fixture(scope="module")
def categorizer():
    return MerchantCategorizer()


class StubCategorizer:
    def predict(self, merchant):
        return "groceries", 0.9


def test_generated_data_is_balanced_and_reproducible():
    names, labels = generate_merchants(n_per_category=10, seed=1)
    assert len(names) == len(labels) == 80
    assert labels.count("groceries") == 10
    assert (names, labels) == generate_merchants(n_per_category=10, seed=1)


def test_held_out_accuracy_is_reported_and_reasonable(categorizer):
    assert categorizer.metrics["accuracy"] > 0.85
    assert categorizer.metrics["test_samples"] == 300
    assert set(categorizer.metrics["per_category_f1"]) >= {"groceries", "health", "other"}


@pytest.mark.parametrize(
    "name,expected",
    [
        ("SUNRISE SUPERMARKET", "groceries"),
        ("LAKESIDE PHARMACY", "health"),
        ("ZURI RESTAURANT", "eating_out"),
        ("BLUE ACADEMY", "education"),
        ("PRIME PETROL STATION", "transport"),
        ("UMOJA ENTERPRISES", "other"),
    ],
)
def test_known_merchant_types(categorizer, name, expected):
    category, confidence = categorizer.predict(name)
    assert category == expected
    assert 0 < confidence <= 1


def test_tolerates_a_typo(categorizer):
    assert categorizer.predict("SUNRISE SUPERMARKT")[0] == "groceries"


def test_empty_name_is_other_with_zero_confidence(categorizer):
    assert categorizer.predict("") == ("other", 0.0)
    assert categorizer.predict(None) == ("other", 0.0)


def test_rule_based_categories():
    stub = StubCategorizer()
    assert categorize_transaction({"transaction_type": "receive", "counterparty": "X"}, stub) == ("income", 1.0)
    assert categorize_transaction({"transaction_type": "withdraw", "counterparty": "X"}, stub) == ("cash_withdrawal", 1.0)
    assert categorize_transaction({"transaction_type": "airtime", "counterparty": None}, stub) == ("airtime_data", 1.0)
    assert categorize_transaction({"transaction_type": "send", "counterparty": "X"}, stub) == ("personal_transfer", 1.0)
    assert categorize_transaction({"transaction_type": "till", "counterparty": "X"}, stub) == ("groceries", 0.9)
    assert categorize_transaction({"transaction_type": "paybill", "counterparty": "X"}, stub) == ("groceries", 0.9)
    assert categorize_transaction({"transaction_type": "unknown", "counterparty": None}, stub) == ("unknown", 0.0)

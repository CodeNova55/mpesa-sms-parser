from collections import defaultdict

from .categorizer import MerchantCategorizer, categorize_transaction
from .parser import parse_message


def summarise(transactions):
    """Totals for a list of parsed and categorised transactions."""
    out_by_category = defaultdict(float)
    money_in = 0.0
    money_out = 0.0
    fees = 0.0
    unrecognised = 0
    for item in transactions:
        if not item["recognized"]:
            unrecognised += 1
            continue
        fees += item["fee"]
        if item["transaction_type"] == "receive":
            money_in += item["amount"]
        else:
            money_out += item["amount"]
            out_by_category[item["category"]] += item["amount"]
    return {
        "transactions_total": len(transactions),
        "recognised": len(transactions) - unrecognised,
        "unrecognised": unrecognised,
        "money_in": round(money_in, 2),
        "money_out": round(money_out, 2),
        "fees": round(fees, 2),
        "out_by_category": {
            name: round(total, 2)
            for name, total in sorted(out_by_category.items(), key=lambda pair: -pair[1])
        },
    }


def analyze(messages, categorizer=None):
    """Parse and categorise messages, then summarise them."""
    categorizer = categorizer or MerchantCategorizer()
    transactions = []
    for text in messages:
        parsed = parse_message(text)
        category, confidence = categorize_transaction(parsed, categorizer)
        parsed["category"] = category
        parsed["category_confidence"] = confidence
        transactions.append(parsed)
    return {"transactions": transactions, "summary": summarise(transactions)}

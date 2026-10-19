import re
from typing import Dict, Any

def parse_mpesa_sms(sms: str) -> Dict[str, Any]:
    """Parses a raw M-Pesa SMS string into structured key-value components."""
    result: Dict[str, Any] = {
        "raw_text": sms,
        "transaction_code": None,
        "amount": None,
        "transaction_type": "unknown",
        "name": None,
        "phone_or_account": None,
        "datetime": None,
        "balance": None,
        "fee": 0.0
    }

    code_match = re.search(r"^([A-Z0-9]{10})\s+Confirmed", sms)
    if code_match:
        result["transaction_code"] = code_match.group(1)

    amount_match = re.search(r"Ksh\s*([\d,]+\.\d{2}|[\d,]+)", sms)
    if amount_match:
        result["amount"] = float(amount_match.group(1).replace(",", ""))

    balance_match = re.search(r"balance\s+is\s+Ksh\s*([\d,]+\.\d{2}|[\d,]+)", sms, re.IGNORECASE)
    if balance_match:
        result["balance"] = float(balance_match.group(1).replace(",", ""))

    fee_match = re.search(r"(?:cost|fee),?\s+Ksh\s*([\d,]+\.\d{2}|[\d,]+)", sms, re.IGNORECASE)
    if fee_match:
        result["fee"] = float(fee_match.group(1).replace(",", ""))

    if "received" in sms.lower():
        result["transaction_type"] = "receive"
        party_match = re.search(r"from\s+([A-Z\s]+)(?:\s+(07\d{8}|\d+))?", sms)
        if party_match:
            result["name"] = party_match.group(1).strip()
            result["phone_or_account"] = party_match.group(2)
    elif "sent to" in sms.lower():
        if "for account" in sms.lower():
            result["transaction_type"] = "paybill"
            party_match = re.search(r"sent to\s+([A-Z\s]+?)\s+for account", sms)
            acc_match = re.search(r"for account\s+([A-Z0-9]+)", sms)
            if party_match: result["name"] = party_match.group(1).strip()
            if acc_match: result["phone_or_account"] = acc_match.group(1)
        else:
            result["transaction_type"] = "send"
            party_match = re.search(r"sent to\s+([A-Z\s]+)(?:\s+(07\d{8}|\d+))?", sms)
            if party_match:
                result["name"] = party_match.group(1).strip()
                result["phone_or_account"] = party_match.group(2)
    elif "paid to" in sms.lower():
        result["transaction_type"] = "buy_goods"
        party_match = re.search(r"paid to\s+([A-Z\s]+?)(?:\s+on|\.|$)", sms)
        if party_match: result["name"] = party_match.group(1).strip()
    elif "withdraw" in sms.lower():
        result["transaction_type"] = "withdraw"
        agent_match = re.search(r"Agent\s+([A-Z0-9\s-]+?)(?:\s+on|\.|$)", sms)
        if agent_match: result["name"] = agent_match.group(1).strip()

    return result

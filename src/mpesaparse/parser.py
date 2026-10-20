import re
from datetime import datetime

# Message formats are modelled on common M-Pesa wording, not an official spec.
# Anything that does not match is reported as unrecognised instead of guessed.

AMT = r"Ksh\s?(?P<amount>[\d,]+(?:\.\d{1,2})?)"
PHONE = r"(?:\+?254|0)\d{9}"
BEFORE_DATE = r"(?=\s+on\s+\d)"

RECEIVE = re.compile(
    r"received\s+" + AMT + r"\s+from\s+(?P<name>.+?)(?:\s+(?P<party>" + PHONE + r"))?" + BEFORE_DATE,
    re.IGNORECASE,
)
PAYBILL = re.compile(
    AMT + r"\s+sent to\s+(?P<name>.+?)\s+for account\s+(?P<party>\S+?)" + BEFORE_DATE,
    re.IGNORECASE,
)
SEND = re.compile(
    AMT + r"\s+sent to\s+(?P<name>.+?)(?:\s+(?P<party>" + PHONE + r"))?" + BEFORE_DATE,
    re.IGNORECASE,
)
TILL = re.compile(
    AMT + r"\s+paid to\s+(?P<name>.+?)\.?" + BEFORE_DATE,
    re.IGNORECASE,
)
AIRTIME = re.compile(
    r"bought\s+" + AMT + r"\s+of airtime(?:\s+for\s+(?P<party>" + PHONE + r"))?" + BEFORE_DATE,
    re.IGNORECASE,
)
WITHDRAW = re.compile(
    r"Withdraw\s+" + AMT + r"\s+from\s+(?P<party>\d+)\s*-\s*(?P<name>.+?)(?=\s+New\s+M-?PESA\s+balance)",
    re.IGNORECASE,
)

# Order matters: paybill must be tried before send, because both say "sent to".
PATTERNS = [
    ("receive", RECEIVE),
    ("paybill", PAYBILL),
    ("send", SEND),
    ("till", TILL),
    ("airtime", AIRTIME),
    ("withdraw", WITHDRAW),
]

CODE = re.compile(r"^\s*(?P<code>[A-Z0-9]{10})\s+Confirmed", re.IGNORECASE)
DATE = re.compile(
    r"(?P<date>\d{1,2}/\d{1,2}/\d{2,4})\s+at\s+(?P<time>\d{1,2}:\d{2})\s?(?P<ampm>[AP]M)",
    re.IGNORECASE,
)
BALANCE = re.compile(r"balance\s+is\s+Ksh\s?(?P<value>[\d,]+(?:\.\d{1,2})?)", re.IGNORECASE)
FEE = re.compile(r"(?:cost|fee),?\s+Ksh\s?(?P<value>[\d,]+(?:\.\d{1,2})?)", re.IGNORECASE)


def _number(text):
    return float(text.replace(",", ""))


def _datetime(text):
    match = DATE.search(text)
    if not match:
        return None
    date = match.group("date")
    year_format = "%y" if len(date.split("/")[2]) == 2 else "%Y"
    stamp = date + " " + match.group("time") + " " + match.group("ampm").upper()
    try:
        return datetime.strptime(stamp, "%d/%m/" + year_format + " %I:%M %p").isoformat()
    except ValueError:
        return None


def parse_message(text):
    """Turn one message into a dict of fields.

    Messages in a format we do not know come back with recognized=False
    and no amount, so nothing is guessed.
    """
    result = {
        "recognized": False,
        "transaction_code": None,
        "transaction_type": "unknown",
        "amount": None,
        "counterparty": None,
        "reference": None,
        "datetime": None,
        "balance": None,
        "fee": 0.0,
    }
    if not isinstance(text, str):
        return result
    code = CODE.search(text)
    if not code:
        return result
    result["transaction_code"] = code.group("code").upper()

    for kind, pattern in PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        fields = match.groupdict()
        result["recognized"] = True
        result["transaction_type"] = kind
        result["amount"] = _number(fields["amount"])
        if fields.get("name"):
            result["counterparty"] = " ".join(fields["name"].split())
        result["reference"] = fields.get("party")
        result["datetime"] = _datetime(text)
        balance = BALANCE.search(text)
        if balance:
            result["balance"] = _number(balance.group("value"))
        fee = FEE.search(text)
        if fee:
            result["fee"] = _number(fee.group("value"))
        break
    return result

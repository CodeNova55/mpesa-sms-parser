from mpesaparse.parser import parse_message

RECEIVE = "QH12AB34CD Confirmed. You have received Ksh1,500.00 from JOHN DOE 0712345678 on 19/10/26 at 3:30 PM. New M-PESA balance is Ksh5,430.50."
SEND = "QH12AB34CE Confirmed. Ksh500.00 sent to JANE WANJIKU 0723456789 on 19/10/26 at 4:00 PM. New M-PESA balance is Ksh4,930.50. Transaction cost, Ksh7.00."
PAYBILL = "QH12AB34CF Confirmed. Ksh3,400.00 sent to POWER TOKENS for account 12345678 on 19/10/26 at 4:10 PM. New M-PESA balance is Ksh1,530.50. Transaction cost, Ksh0.00."
TILL = "QH12AB34CG Confirmed. Ksh850.00 paid to SUNRISE SUPERMARKET. on 19/10/26 at 4:20 PM. New M-PESA balance is Ksh680.50. Transaction cost, Ksh0.00."
AIRTIME = "QH12AB34CH Confirmed. You bought Ksh100.00 of airtime on 19/10/26 at 4:30 PM. New M-PESA balance is Ksh580.50. Transaction cost, Ksh0.00."
WITHDRAW = "QH12AB34CJ Confirmed. on 19/10/26 at 5:00 PM Withdraw Ksh2,000.00 from 123456 - GRACE AGENT New M-PESA balance is Ksh3,580.50. Transaction cost, Ksh28.00."


def test_receive():
    r = parse_message(RECEIVE)
    assert r["recognized"] is True
    assert r["transaction_type"] == "receive"
    assert r["transaction_code"] == "QH12AB34CD"
    assert r["amount"] == 1500.0
    assert r["counterparty"] == "JOHN DOE"
    assert r["reference"] == "0712345678"
    assert r["datetime"] == "2026-10-19T15:30:00"
    assert r["balance"] == 5430.5
    assert r["fee"] == 0.0


def test_send_to_a_person():
    r = parse_message(SEND)
    assert r["transaction_type"] == "send"
    assert r["amount"] == 500.0
    assert r["counterparty"] == "JANE WANJIKU"
    assert r["reference"] == "0723456789"
    assert r["datetime"] == "2026-10-19T16:00:00"
    assert r["balance"] == 4930.5
    assert r["fee"] == 7.0


def test_paybill():
    r = parse_message(PAYBILL)
    assert r["transaction_type"] == "paybill"
    assert r["amount"] == 3400.0
    assert r["counterparty"] == "POWER TOKENS"
    assert r["reference"] == "12345678"
    assert r["datetime"] == "2026-10-19T16:10:00"
    assert r["balance"] == 1530.5


def test_till_payment():
    r = parse_message(TILL)
    assert r["transaction_type"] == "till"
    assert r["amount"] == 850.0
    assert r["counterparty"] == "SUNRISE SUPERMARKET"
    assert r["reference"] is None


def test_airtime():
    r = parse_message(AIRTIME)
    assert r["transaction_type"] == "airtime"
    assert r["amount"] == 100.0
    assert r["counterparty"] is None


def test_withdrawal():
    r = parse_message(WITHDRAW)
    assert r["transaction_type"] == "withdraw"
    assert r["amount"] == 2000.0
    assert r["counterparty"] == "GRACE AGENT"
    assert r["reference"] == "123456"
    assert r["fee"] == 28.0
    assert r["datetime"] == "2026-10-19T17:00:00"


def test_four_digit_year_and_pm_without_space():
    text = RECEIVE.replace("19/10/26 at 3:30 PM", "19/10/2026 at 3:30PM")
    r = parse_message(text)
    assert r["recognized"] is True
    assert r["datetime"] == "2026-10-19T15:30:00"


def test_missing_space_after_confirmed():
    text = RECEIVE.replace("Confirmed. You", "Confirmed.You")
    assert parse_message(text)["recognized"] is True


def test_amount_without_decimals():
    text = SEND.replace("Ksh500.00", "Ksh1,500")
    assert parse_message(text)["amount"] == 1500.0


def test_extra_spaces_in_names_are_tidied():
    text = SEND.replace("JANE WANJIKU", "JANE   WANJIKU")
    assert parse_message(text)["counterparty"] == "JANE WANJIKU"


def test_invalid_date_gives_none_but_message_is_still_recognised():
    text = SEND.replace("19/10/26", "31/02/26")
    r = parse_message(text)
    assert r["recognized"] is True
    assert r["datetime"] is None


def test_unrelated_text_is_unrecognised():
    r = parse_message("This is not an M-Pesa message")
    assert r["recognized"] is False
    assert r["amount"] is None
    assert r["transaction_type"] == "unknown"


def test_unknown_format_is_not_guessed():
    text = "QH12AB34CD Confirmed. Fuliza M-PESA amount is Ksh500.00. Available limit is Ksh1,000.00."
    r = parse_message(text)
    assert r["recognized"] is False
    assert r["amount"] is None
    assert r["transaction_code"] == "QH12AB34CD"


def test_non_text_input_does_not_crash():
    assert parse_message(None)["recognized"] is False
    assert parse_message(123)["recognized"] is False

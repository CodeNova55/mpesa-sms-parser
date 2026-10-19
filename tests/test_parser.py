from mpesaparse.parser import parse_mpesa_sms
from mpesaparse.categorizer import TransactionCategorizer

def test_parse_receive():
    sms = "ABC123XYZ9 Confirmed.You have received Ksh1,500.00 from JOHN DOE 0712345678 on 19/10/2026 at 3:30 PM New M-Pesa balance is Ksh5,430.50"
    res = parse_mpesa_sms(sms)
    assert res["transaction_code"] == "ABC123XYZ9"
    assert res["amount"] == 1500.00
    assert res["transaction_type"] == "receive"
    assert res["name"] == "JOHN DOE"
    assert res["balance"] == 5430.50

def test_categorizer():
    cat = TransactionCategorizer()
    assert cat.predict("You have received Ksh500 from JOHN DOE") == "income"

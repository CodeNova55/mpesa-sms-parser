import random
from datetime import datetime, timedelta

NAMES = ["JOHN DOE", "JANE WANJIKU", "KIPRONO ROTICH", "AMINA OMOLLO", "TECH HUB LTD", "POWER LIGHTING CO"]

def generate_sample_sms(tx_type: str = None) -> str:
    """Generates a realistic mock M-Pesa SMS string."""
    code = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=10))
    amount = random.choice([150, 500, 1250, 3400, 10500, 25000])
    fee = round(amount * 0.015, 2) if amount > 1000 else 0.00
    balance = random.choice([5430.50, 12340.00, 45200.10, 890.25])
    name = random.choice(NAMES)
    phone = f"07{random.randint(10, 99)}{random.randint(100, 999)}{random.randint(100, 999)}"
    
    date_str = (datetime.now() - timedelta(minutes=random.randint(1, 1440))).strftime("%d/%m/%Y at %I:%M %p")
    types = tx_type or random.choice(["receive", "send", "paybill", "buy_goods", "withdraw"])

    if types == "receive":
        return f"{code} Confirmed.You have received Ksh{amount:.2f} from {name} {phone} on {date_str} New M-Pesa balance is Ksh{balance:.2f}"
    elif types == "send":
        return f"{code} Confirmed. Ksh{amount:.2f} sent to {name} {phone} on {date_str}. New M-Pesa balance is Ksh{balance:.2f}. Transaction cost, Ksh{fee:.2f}."
    elif types == "paybill":
        return f"{code} Confirmed.Ksh{amount:.2f} sent to {name} for account {random.randint(1000, 9999)} on {date_str} New balance is Ksh{balance:.2f}. Transaction fee, Ksh{fee:.2f}"
    elif types == "buy_goods":
        return f"{code} Confirmed. Ksh{amount:.2f} paid to {name} on {date_str}.New M-Pesa balance is Ksh{balance:.2f}"
    else:
        return f"{code} Confirmed.Withdraw Ksh{amount:.2f} from Agent {random.randint(10000, 99999)} - NAIROBI on {date_str} New M-Pesa balance is Ksh{balance:.2f}"

from fastapi import FastAPI
from pydantic import BaseModel
from mpesaparse.parser import parse_mpesa_sms
from mpesaparse.categorizer import TransactionCategorizer
from mpesaparse.generator import generate_sample_sms

app = FastAPI(title="M-Pesa SMS Parser API", version="1.0.0")
categorizer = TransactionCategorizer()

class SMSRequest(BaseModel):
    sms_text: str

@app.get("/")
def read_root():
    return {"message": "Welcome to M-Pesa SMS Parser API"}

@app.post("/parse")
def parse_sms_endpoint(payload: SMSRequest):
    parsed = parse_mpesa_sms(payload.sms_text)
    parsed["category"] = categorizer.predict(payload.sms_text)
    return parsed

@app.get("/generate")
def generate_sms(type: str = None):
    sms = generate_sample_sms(type)
    return {"generated_sms": sms, "parsed": parse_mpesa_sms(sms)}

import threading
from typing import Annotated

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .analysis import analyze
from .categorizer import MerchantCategorizer

MAX_MESSAGES = 500
MAX_LENGTH = 1000


class Message(BaseModel):
    message: str = Field(max_length=MAX_LENGTH, description="One M-Pesa-style message")


class MessageBatch(BaseModel):
    messages: list[Annotated[str, Field(max_length=MAX_LENGTH)]] = Field(
        min_length=1,
        max_length=MAX_MESSAGES,
        description="M-Pesa-style messages to parse and summarise",
    )


def create_app(categorizer=None):
    """Build the API. Pass a trained categorizer (used by tests), or let it train one."""
    app = FastAPI(
        title="M-Pesa Message Parser",
        version="1.0.0",
        description=(
            "Parses M-Pesa-style messages into structured data and spending categories. "
            "Message formats are modelled on common M-Pesa wording and the categorizer is "
            "trained on invented merchant names, so this is a demo. Nothing you send is "
            "stored or logged, but do not send real messages to a public demo."
        ),
    )
    app.state.categorizer = categorizer
    lock = threading.Lock()

    def get_categorizer():
        with lock:
            if app.state.categorizer is None:
                app.state.categorizer = MerchantCategorizer()
            return app.state.categorizer

    @app.get("/health")
    def health():
        return {"status": "ok", "model_loaded": app.state.categorizer is not None}

    @app.get("/model/metrics")
    def metrics():
        return get_categorizer().metrics

    @app.post("/parse")
    def parse(body: Message):
        result = analyze([body.message], get_categorizer())
        return result["transactions"][0]

    @app.post("/analyze")
    def analyze_messages(body: MessageBatch):
        return analyze(body.messages, get_categorizer())

    return app


app = create_app()

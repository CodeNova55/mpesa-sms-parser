from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline

from .merchants import generate_merchants

MIN_CONFIDENCE = 0.3


class MerchantCategorizer:
    """Sorts merchant names into spending categories.

    Trained on generated names (character n-grams plus logistic regression) and
    evaluated on names it has not seen. Names it is unsure about become "other".
    """

    def __init__(self, seed=42):
        self.seed = seed
        self.pipeline = make_pipeline(
            TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4)),
            LogisticRegression(C=10, max_iter=1000),
        )
        self.metrics = {}
        self._train()

    def _train(self):
        names, labels = generate_merchants(seed=self.seed)
        X_train, X_test, y_train, y_test = train_test_split(
            names, labels, test_size=0.25, stratify=labels, random_state=self.seed
        )
        self.pipeline.fit(X_train, y_train)
        predictions = self.pipeline.predict(X_test)
        report = classification_report(y_test, predictions, output_dict=True, zero_division=0)
        self.metrics = {
            "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
            "test_samples": len(y_test),
            "per_category_f1": {
                label: round(float(report[label]["f1-score"]), 4) for label in sorted(set(y_test))
            },
        }

    def predict(self, merchant):
        """Return (category, confidence) for a merchant name."""
        if not merchant or not merchant.strip():
            return "other", 0.0
        probabilities = self.pipeline.predict_proba([merchant.upper()])[0]
        best = int(probabilities.argmax())
        confidence = round(float(probabilities[best]), 4)
        if confidence < MIN_CONFIDENCE:
            return "other", confidence
        return str(self.pipeline.classes_[best]), confidence


def categorize_transaction(parsed, categorizer):
    """Pick a category for a parsed message. Only merchant payments need the model."""
    kind = parsed["transaction_type"]
    if kind == "receive":
        return "income", 1.0
    if kind == "withdraw":
        return "cash_withdrawal", 1.0
    if kind == "airtime":
        return "airtime_data", 1.0
    if kind == "send":
        return "personal_transfer", 1.0
    if kind in ("paybill", "till"):
        return categorizer.predict(parsed["counterparty"])
    return "unknown", 0.0

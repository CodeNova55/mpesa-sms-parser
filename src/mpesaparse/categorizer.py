from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

class TransactionCategorizer:
    def __init__(self):
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
            ("clf", LogisticRegression())
        ])
        self._train_default_model()

    def _train_default_model(self):
        training_data = [
            ("You have received Ksh500 from JOHN DOE", "income"),
            ("Ksh1,200 sent to JANE WANJIKU 0712345678", "transfer"),
            ("Ksh3,400 sent to POWER LIGHTING CO for account 1234", "bill_payment"),
            ("Ksh500 paid to QUICKMART SUPERMARKET", "merchant_payment"),
            ("Withdraw Ksh10,000 from Agent 56789", "withdrawal"),
        ]
        self.pipeline.fit([x[0] for x in training_data], [x[1] for x in training_data])

    def predict(self, text: str) -> str:
        return self.pipeline.predict([text])[0]

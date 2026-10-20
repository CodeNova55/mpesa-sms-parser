# M-Pesa Message Parser

Turns M-Pesa-style confirmation messages into structured data, puts each payment into a spending category, and totals everything up. It is available as a command line tool and as a FastAPI service.

> **Important:** the message formats are modelled on common M-Pesa wording, not an official specification, and all names, numbers, and merchants in this project are invented. The categorizer is trained on generated merchant names, so its accuracy shows that the pipeline works, not how it would perform on real messages. Real messages contain names and phone numbers, so do not send them to a public demo. This service stores and logs nothing.

## Features
- Parses six message types: money received, sent to a person, paybill, till payment, airtime, and agent withdrawal
- Extracts the transaction code, amount, counterparty, phone or account number, date and time, balance, and fee
- Messages in an unknown format are reported as unrecognised instead of guessed
- A merchant categorizer (character n-gram TF-IDF and logistic regression) sorts paybill and till merchants into groceries, transport, utilities, eating out, health, education, shopping, or other; names it is unsure about become "other"
- Money in, personal transfers, airtime, and withdrawals are categorized by rule
- Spending summary: money in, money out, fees, and spending by category
- Command line tool and FastAPI service with interactive docs at `/docs`
- 45 automated tests

## How It Works
1. **Parse:** pattern matching extracts the fields from each message
2. **Categorize:** rules cover most message types; the model decides only for paybill and till merchants
3. **Summarise:** unrecognised lines are counted but never added to the totals

## Getting Started

```bash
git clone https://github.com/CodeNova55/mpesa-sms-parser.git
cd mpesa-sms-parser
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

The code lives in `src/`, so tell Python where to find it (once per terminal):

```powershell
$env:PYTHONPATH = "src"       # Windows PowerShell
# export PYTHONPATH=src       # macOS/Linux
```

### Command line

```bash
python -m mpesaparse.cli --file sample_data/messages.txt
python -m mpesaparse.cli --file sample_data/messages.txt --output result.json
```

The input is a text file with one message per line.

### API

```bash
uvicorn mpesaparse.api:app
```

Open http://127.0.0.1:8000/docs to try it.

```powershell
$body = @{ message = "QH12AB34CG Confirmed. Ksh850.00 paid to SUNRISE SUPERMARKET. on 19/10/26 at 4:20 PM. New M-PESA balance is Ksh680.50. Transaction cost, Ksh0.00." } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/parse -ContentType "application/json" -Body $body
```

## Endpoints

| Endpoint | Purpose |
|---|---|
| `POST /parse` | parse and categorize one message |
| `POST /analyze` | parse a list of messages (1 to 500) and return the transactions and a summary |
| `GET /model/metrics` | held-out evaluation of the categorizer |
| `GET /health` | service status and whether the categorizer is loaded |

Messages longer than 1000 characters, empty lists, and more than 500 messages are rejected with a `422` error.

## Reading the Results

`GET /model/metrics` reports the categorizer's accuracy and per-category F1 on merchant names it was not trained on. These names are generated from word lists, so the scores are high by design. A real deployment would need real, labelled merchant data.

## Running Tests

```bash
python -m pytest -v
```

## Project Structure

```
src/mpesaparse/parser.py       message parser
src/mpesaparse/merchants.py    generates invented merchant names for training
src/mpesaparse/categorizer.py  merchant categorizer and category rules
src/mpesaparse/analysis.py     parse, categorize, and summarise
src/mpesaparse/cli.py          command line tool
src/mpesaparse/api.py          FastAPI service
sample_data/messages.txt       invented sample messages
tests/                         automated tests
```

## Limitations
- Message wording varies by provider and changes over time, so unrecognised messages are expected; update the patterns when new formats appear
- Trained on generated merchant names only, so real merchants with unusual names may be mis-sorted or fall back to "other"
- Messages have no merchant category, so the model guesses from the name alone
- No storage, accounts, or authentication; the API is stateless
- The categorizer trains when the service first needs it, which takes a moment

## Git Workflow
- One feature branch per piece of work
- Feature branch -> PR into `develop`
- `develop` -> PR into `main` (after approval)
- No direct pushes to `develop` or `main`

## Roadmap
- Add Fuliza, reversal, and other message types
- Train and evaluate on real, consented, anonymised data
- Let users correct a category and learn from it
- Deployment

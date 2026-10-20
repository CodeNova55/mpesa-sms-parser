import json
from pathlib import Path

from mpesaparse.cli import main, process_batch

SAMPLE = Path(__file__).resolve().parent.parent / "sample_data" / "messages.txt"


def test_process_batch_returns_one_transaction_per_message():
    lines = [line.strip() for line in SAMPLE.read_text(encoding="utf-8").splitlines() if line.strip()]
    transactions = process_batch(lines)
    assert len(transactions) == 8
    assert transactions[0]["transaction_code"] == "QH12AB34CD"
    assert transactions[0]["category"] == "income"


def test_main_prints_json(capsys):
    assert main(["--file", str(SAMPLE)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["summary"]["recognised"] == 7


def test_main_writes_output_file(tmp_path):
    target = tmp_path / "out.json"
    assert main(["--file", str(SAMPLE), "--output", str(target)]) == 0
    assert json.loads(target.read_text(encoding="utf-8"))["summary"]["unrecognised"] == 1


def test_main_reports_a_missing_file(tmp_path, capsys):
    assert main(["--file", str(tmp_path / "nope.txt")]) == 1
    assert "Could not read file" in capsys.readouterr().err

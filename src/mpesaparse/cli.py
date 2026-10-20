import argparse
import json
import sys

from .analysis import analyze


def process_batch(messages):
    """Parse and categorise a list of messages. Returns the transactions."""
    return analyze(messages)["transactions"]


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Parse M-Pesa-style messages (one per line) and summarise spending."
    )
    parser.add_argument("--file", "-f", required=True, help="Text file with one message per line")
    parser.add_argument("--output", "-o", help="Write the JSON result to this file")
    args = parser.parse_args(argv)

    try:
        with open(args.file, "r", encoding="utf-8-sig") as handle:
            lines = [line.strip() for line in handle if line.strip()]
    except OSError as error:
        print("Could not read file: " + str(error), file=sys.stderr)
        return 1

    text = json.dumps(analyze(lines), indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as out:
            out.write(text)
        print("Processed " + str(len(lines)) + " messages and saved " + args.output)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())

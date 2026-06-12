from __future__ import annotations

import csv
import json
from pathlib import Path
import sys


def csv_to_cases(input_path: Path, output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0

    with input_path.open("r", encoding="utf-8-sig", newline="") as source, output_path.open("w", encoding="utf-8") as target:
        reader = csv.DictReader(source)
        required = {"id", "question", "context", "answer", "expected_topics", "requires_refusal"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV is missing columns: {', '.join(sorted(missing))}")

        for row in reader:
            case = {
                "id": row["id"].strip(),
                "question": row["question"].strip(),
                "context": split_list(row["context"]),
                "answer": row["answer"].strip(),
                "expected_topics": split_list(row["expected_topics"]),
                "requires_refusal": row["requires_refusal"].strip().lower() in {"true", "1", "yes", "y"},
            }
            target.write(json.dumps(case, ensure_ascii=False) + "\n")
            count += 1

    return count


def split_list(value: str) -> list[str]:
    return [item.strip() for item in value.split("|") if item.strip()]


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2:
        print("Usage: python -m src.evalforge.importers <cases.csv> <cases.jsonl>")
        return 2

    count = csv_to_cases(Path(args[0]), Path(args[1]))
    print(f"Converted {count} CSV rows to {args[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from pathlib import Path
import argparse
import json

from .report import write_html_report
from .runner import evaluate_cases, load_cases, summary_to_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate LLM/RAG outputs and generate a quality report.")
    parser.add_argument("input", help="Path to JSONL evaluation cases.")
    parser.add_argument("output", help="Path to output HTML report.")
    parser.add_argument("--json", dest="json_output", help="Optional path to write JSON summary.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    cases = load_cases(Path(args.input))
    summary = evaluate_cases(cases)
    write_html_report(summary, Path(args.output))

    if args.json_output:
        Path(args.json_output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_output).write_text(json.dumps(summary_to_json(summary), indent=2), encoding="utf-8")

    print(f"Evaluated {summary.total} cases")
    print(f"Pass: {summary.passed} | Review: {summary.review} | Fail: {summary.failed} | Avg risk: {summary.average_risk}")
    print(f"Report: {args.output}")
    return 0 if summary.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

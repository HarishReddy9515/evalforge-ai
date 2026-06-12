from __future__ import annotations

from pathlib import Path
import argparse
import json

from .compare import compare_summaries
from .linting import has_errors, lint_cases
from .markdown import write_markdown_report
from .privacy import redact_cases, scan_cases
from .report import write_html_report
from .runner import evaluate_cases, load_cases, summary_to_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate LLM/RAG outputs and generate a quality report.")
    parser.add_argument("input", help="Path to JSONL evaluation cases.")
    parser.add_argument("output", help="Path to output HTML report.")
    parser.add_argument("--json", dest="json_output", help="Optional path to write JSON summary.")
    parser.add_argument("--markdown", dest="markdown_output", help="Optional path to write markdown summary.")
    parser.add_argument("--baseline", help="Optional JSONL baseline cases for regression comparison.")
    parser.add_argument("--max-risk", type=float, default=0.5, help="Fail when average risk is above this threshold.")
    parser.add_argument("--redacted-jsonl", help="Optional path to write a PII-redacted copy of the input dataset.")
    parser.add_argument("--fail-on-pii", action="store_true", help="Return failure when PII is detected in evaluation data.")
    parser.add_argument("--allow-failures", action="store_true", help="Return success even when eval cases fail.")
    parser.add_argument("--lint-only", action="store_true", help="Only validate the dataset format.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    cases = load_cases(Path(args.input))
    issues = lint_cases(cases)
    privacy_findings = scan_cases(cases)
    for issue in issues:
        print(f"{issue.severity.upper()} [{issue.case_id}] {issue.message}")
    for finding in privacy_findings:
        print(f"PRIVACY [{finding.case_id}] {finding.pii_type} detected in {finding.field}")

    if args.redacted_jsonl:
        redacted_cases = redact_cases(cases)
        redacted_path = Path(args.redacted_jsonl)
        redacted_path.parent.mkdir(parents=True, exist_ok=True)
        redacted_path.write_text(
            "\n".join(json.dumps(case, ensure_ascii=False) for case in redacted_cases) + "\n",
            encoding="utf-8",
        )
        print(f"Redacted dataset: {args.redacted_jsonl}")

    if args.lint_only:
        print(f"Linted {len(cases)} cases with {len(issues)} lint issue(s) and {len(privacy_findings)} privacy finding(s)")
        return 1 if has_errors(issues) or (args.fail_on_pii and privacy_findings) else 0

    if has_errors(issues):
        print("Dataset has lint errors; evaluation stopped.")
        return 2
    if args.fail_on_pii and privacy_findings:
        print("Privacy findings detected; evaluation stopped because --fail-on-pii was set.")
        return 3

    summary = evaluate_cases(cases)
    comparison = None
    if args.baseline:
        baseline_summary = evaluate_cases(load_cases(Path(args.baseline)))
        comparison = compare_summaries(baseline_summary, summary)
        print(
            "Baseline comparison: "
            f"risk delta {comparison.risk_delta} | "
            f"improved {comparison.improved} | regressed {comparison.regressed}"
        )

    write_html_report(summary, Path(args.output))

    if args.json_output:
        Path(args.json_output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_output).write_text(json.dumps(summary_to_json(summary), indent=2), encoding="utf-8")

    if args.markdown_output:
        write_markdown_report(summary, Path(args.markdown_output), comparison)

    print(f"Evaluated {summary.total} cases")
    print(f"Pass: {summary.passed} | Review: {summary.review} | Fail: {summary.failed} | Avg risk: {summary.average_risk}")
    print(f"Report: {args.output}")

    if args.allow_failures:
        return 0
    if summary.failed > 0 or summary.average_risk > args.max_risk:
        return 1
    if comparison and comparison.regressed > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

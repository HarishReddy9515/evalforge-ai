from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evalforge.runner import evaluate_cases, load_cases
from evalforge.report import write_html_report
from evalforge.compare import compare_summaries
from evalforge.linting import lint_cases
from evalforge.markdown import write_markdown_report
from evalforge.importers import csv_to_cases
from evalforge.privacy import redact_cases, scan_cases


def main() -> int:
    cases = load_cases(ROOT / "data" / "eval_cases.jsonl")
    baseline_cases = load_cases(ROOT / "data" / "baseline_cases.jsonl")
    privacy_cases = load_cases(ROOT / "data" / "privacy_cases.jsonl")
    assert not any(issue.severity == "error" for issue in lint_cases(cases))
    assert scan_cases(privacy_cases)
    assert "[REDACTED_EMAIL]" in redact_cases(privacy_cases)[0]["question"]

    summary = evaluate_cases(cases)
    baseline = evaluate_cases(baseline_cases)
    comparison = compare_summaries(baseline, summary)

    assert summary.total == 4
    assert summary.passed >= 1
    assert summary.failed >= 1
    assert any(item.case["id"] == "unsupported-claim" for item in summary.cases)
    assert comparison.improved >= 1

    output = ROOT / "reports" / "smoke_report.html"
    write_html_report(summary, output)
    assert output.exists()
    assert "EvalForge AI" in output.read_text(encoding="utf-8")

    markdown_output = ROOT / "reports" / "smoke_report.md"
    write_markdown_report(summary, markdown_output, comparison)
    assert "Baseline Comparison" in markdown_output.read_text(encoding="utf-8")
    assert "Recommended Next Actions" in markdown_output.read_text(encoding="utf-8")

    imported_output = ROOT / "reports" / "imported_cases.jsonl"
    assert csv_to_cases(ROOT / "data" / "eval_cases.csv", imported_output) == 2

    print("EvalForge smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evalforge.runner import evaluate_cases, load_cases
from evalforge.report import write_html_report


def main() -> int:
    cases = load_cases(ROOT / "data" / "eval_cases.jsonl")
    summary = evaluate_cases(cases)

    assert summary.total == 4
    assert summary.passed >= 1
    assert summary.failed >= 1
    assert any(item.case["id"] == "unsupported-claim" for item in summary.cases)

    output = ROOT / "reports" / "smoke_report.html"
    write_html_report(summary, output)
    assert output.exists()
    assert "EvalForge AI" in output.read_text(encoding="utf-8")

    print("EvalForge smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
